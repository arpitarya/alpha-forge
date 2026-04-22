"""Recent git changes — thin wrapper over `git log`."""

from __future__ import annotations

import asyncio

from alphaforge_repo_context.config import get_settings


async def recent_changes(limit: int = 20, path: str | None = None) -> list[dict]:
    root = get_settings().repo_root
    cmd = [
        "git",
        "-C",
        str(root),
        "log",
        f"-n{max(1, min(limit, 200))}",
        "--pretty=format:%H%x1f%an%x1f%ad%x1f%s",
        "--date=iso-strict",
    ]
    if path:
        cmd += ["--", path]

    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return [{"error": stderr.decode(errors="replace").strip()}]

    out: list[dict] = []
    for line in stdout.decode(errors="replace").splitlines():
        parts = line.split("\x1f")
        if len(parts) == 4:
            sha, author, date, subject = parts
            out.append({"sha": sha, "author": author, "date": date, "subject": subject})
    return out
