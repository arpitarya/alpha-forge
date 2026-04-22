"""File chunking: AST-aware for Python, regex for TS/TSX, section-based for Markdown."""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from alphaforge_repo_context.config import get_settings


@dataclass
class Chunk:
    path: str
    chunk_index: int
    start_line: int
    end_line: int
    symbol: str | None
    kind: str | None  # function | class | section | window
    lang: str | None
    content: str

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode("utf-8", errors="replace")).hexdigest()


_LANG_BY_SUFFIX = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "jsx",
    ".md": "markdown",
    ".mdx": "markdown",
    ".toml": "toml",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".css": "css",
    ".sql": "sql",
    ".sh": "bash",
    ".ipynb": "notebook",
}


def detect_lang(path: Path) -> str | None:
    return _LANG_BY_SUFFIX.get(path.suffix.lower())


def chunk_file(rel_path: str, source: str) -> list[Chunk]:
    lang = detect_lang(Path(rel_path))
    if lang == "python":
        chunks = _chunk_python(rel_path, source)
    elif lang in {"typescript", "tsx", "javascript", "jsx"}:
        chunks = _chunk_ts_like(rel_path, source, lang)
    elif lang == "markdown":
        chunks = _chunk_markdown(rel_path, source)
    else:
        chunks = _chunk_window(rel_path, source, lang)

    if not chunks:
        chunks = _chunk_window(rel_path, source, lang)
    return chunks


def _chunk_python(rel_path: str, source: str) -> list[Chunk]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _chunk_window(rel_path, source, "python")

    lines = source.splitlines()
    chunks: list[Chunk] = []
    idx = 0

    def add(node: ast.AST, qualname: str, kind: str) -> None:
        nonlocal idx
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        body = "\n".join(lines[start - 1 : end])
        if not body.strip():
            return
        chunks.append(
            Chunk(
                path=rel_path,
                chunk_index=idx,
                start_line=start,
                end_line=end,
                symbol=qualname,
                kind=kind,
                lang="python",
                content=body,
            )
        )
        idx += 1

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(node, node.name, "function")
        elif isinstance(node, ast.ClassDef):
            add(node, node.name, "class")
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add(sub, f"{node.name}.{sub.name}", "function")

    # module-level body (imports, constants) as a single prelude chunk
    if chunks:
        first_line = min(c.start_line for c in chunks)
        if first_line > 1:
            prelude = "\n".join(lines[: first_line - 1])
            if prelude.strip():
                chunks.insert(
                    0,
                    Chunk(
                        path=rel_path,
                        chunk_index=0,
                        start_line=1,
                        end_line=first_line - 1,
                        symbol="<module>",
                        kind="module",
                        lang="python",
                        content=prelude,
                    ),
                )
                for i, c in enumerate(chunks):
                    c.chunk_index = i
    return chunks


_TS_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?)?"
    r"(?:async\s+)?"
    r"(?:function\s+(?P<fn>[A-Za-z_$][\w$]*)"
    r"|class\s+(?P<cls>[A-Za-z_$][\w$]*)"
    r"|interface\s+(?P<iface>[A-Za-z_$][\w$]*)"
    r"|type\s+(?P<type>[A-Za-z_$][\w$]*)\s*="
    r"|const\s+(?P<const>[A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"
    r")",
    re.MULTILINE,
)


def _chunk_ts_like(rel_path: str, source: str, lang: str) -> list[Chunk]:
    lines = source.splitlines()
    if not lines:
        return []

    hits: list[tuple[int, str, str]] = []  # (line_no, symbol, kind)
    for m in _TS_SYMBOL_RE.finditer(source):
        line_no = source.count("\n", 0, m.start()) + 1
        if m.group("fn"):
            hits.append((line_no, m.group("fn"), "function"))
        elif m.group("cls"):
            hits.append((line_no, m.group("cls"), "class"))
        elif m.group("iface"):
            hits.append((line_no, m.group("iface"), "interface"))
        elif m.group("type"):
            hits.append((line_no, m.group("type"), "type"))
        elif m.group("const"):
            hits.append((line_no, m.group("const"), "function"))

    if not hits:
        return _chunk_window(rel_path, source, lang)

    chunks: list[Chunk] = []
    boundaries = [h[0] for h in hits] + [len(lines) + 1]
    for i, (start, sym, kind) in enumerate(hits):
        end = boundaries[i + 1] - 1
        body = "\n".join(lines[start - 1 : end])
        if body.strip():
            chunks.append(
                Chunk(
                    path=rel_path,
                    chunk_index=i,
                    start_line=start,
                    end_line=end,
                    symbol=sym,
                    kind=kind,
                    lang=lang,
                    content=body,
                )
            )
    return chunks


def _chunk_markdown(rel_path: str, source: str) -> list[Chunk]:
    lines = source.splitlines()
    if not lines:
        return []
    section_starts: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        if line.startswith("## "):
            section_starts.append((i, line.lstrip("#").strip()))
    if not section_starts:
        return _chunk_window(rel_path, source, "markdown")

    chunks: list[Chunk] = []
    boundaries = [s[0] for s in section_starts] + [len(lines) + 1]
    prelude_end = section_starts[0][0] - 1
    if prelude_end >= 1:
        prelude = "\n".join(lines[:prelude_end])
        if prelude.strip():
            chunks.append(
                Chunk(
                    path=rel_path,
                    chunk_index=0,
                    start_line=1,
                    end_line=prelude_end,
                    symbol="<prelude>",
                    kind="section",
                    lang="markdown",
                    content=prelude,
                )
            )
    for i, (start, title) in enumerate(section_starts):
        end = boundaries[i + 1] - 1
        body = "\n".join(lines[start - 1 : end])
        if body.strip():
            chunks.append(
                Chunk(
                    path=rel_path,
                    chunk_index=len(chunks),
                    start_line=start,
                    end_line=end,
                    symbol=title,
                    kind="section",
                    lang="markdown",
                    content=body,
                )
            )
    return chunks


def _chunk_window(rel_path: str, source: str, lang: str | None) -> list[Chunk]:
    s = get_settings()
    lines = source.splitlines()
    if not lines:
        return []
    step = max(1, s.chunk_max_lines - s.chunk_overlap_lines)
    chunks: list[Chunk] = []
    idx = 0
    start = 0
    while start < len(lines):
        end = min(start + s.chunk_max_lines, len(lines))
        body = "\n".join(lines[start:end])
        if body.strip():
            chunks.append(
                Chunk(
                    path=rel_path,
                    chunk_index=idx,
                    start_line=start + 1,
                    end_line=end,
                    symbol=None,
                    kind="window",
                    lang=lang,
                    content=body,
                )
            )
            idx += 1
        if end >= len(lines):
            break
        start += step
    return chunks
