#!/usr/bin/env bash
# ==============================================================================
# AlphaForge — Config & Secrets Bootstrap / Sync
# ==============================================================================
# Idempotent script that:
#   1. Creates real .env files from .env.example templates if missing.
#   2. Adds any new keys defined in templates to existing real files
#      WITHOUT overwriting user-set values (so re-running picks up new
#      template additions automatically).
#   3. Auto-generates blank secret values where possible:
#        BROKER_CACHE_KEY        — Fernet (cryptography)
#        JWT_SECRET_KEY          — secrets.token_urlsafe(48)
#        POSTGRES_PASSWORD       — secrets.token_urlsafe(48)
#   4. Lists keys that still need manual values (broker creds, API keys).
#
# Run this whenever:
#   - You clone the repo for the first time
#   - You pull and a *.env.example template gained new keys
#   - You add a new credential to your local stack
#
# Usage:
#   ./setup-config.sh                    # Sync + auto-generate + prompt + report
#   ./setup-config.sh --check            # Dry-run: show what would change
#   ./setup-config.sh --no-secrets       # Skip auto-secret generation
#   ./setup-config.sh --no-report        # Skip "manual values needed" reminder
#   ./setup-config.sh --non-interactive  # Skip interactive prompts (CI / scripts)
#   ./setup-config.sh --help
# ==============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Mappings (template → real file, both relative to repo root) ────────────────
# Add new entries here when introducing a new .env tier.
MAPPINGS=(
    ".env.cred.example:.env.cred.local"
    "backend/.env.example:backend/.env"
    "frontend/.env.example:frontend/.env.local"
)

# ── Secrets to auto-generate when blank ────────────────────────────────────────
FERNET_KEYS=("BROKER_CACHE_KEY")
RANDOM_KEYS=("JWT_SECRET_KEY" "POSTGRES_PASSWORD")

# ── Keys the user MUST fill in manually (only listed in the reminder) ──────────
MANUAL_KEYS=(
    "GEMINI_API_KEY" "GROQ_API_KEY"
    "HUGGINGFACE_API_KEY" "OPENROUTER_API_KEY"
    "ZERODHA_USER_ID"
)

# ── Keys to prompt for interactively when blank ──────────────────────────────
# Format: "KEY|Prompt text shown to user|secret(0|1)"
# Add a new entry per line to extend.
PROMPT_KEYS=(
    "ZERODHA_USER_ID|Zerodha client ID (e.g. AB1234) — login is manual, no password stored|0"
)

# ── Output helpers ─────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    G='\033[0;32m'; Y='\033[1;33m'; C='\033[0;36m'; R='\033[0;31m'; B='\033[1m'; N='\033[0m'
else
    G=''; Y=''; C=''; R=''; B=''; N=''
fi
ok()   { printf "${G}✅${N} %s\n" "$*"; }
warn() { printf "${Y}⚠️${N}  %s\n" "$*"; }
info() { printf "${C}ℹ${N}  %s\n" "$*"; }
fail() { printf "${R}❌${N} %s\n" "$*"; exit 1; }
hdr()  { printf "\n${B}── %s ──${N}\n" "$*"; }

# ── Args ───────────────────────────────────────────────────────────────────────
DRY_RUN=0
GEN_SECRETS=1
SHOW_REPORT=1
INTERACTIVE=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check|--dry-run)  DRY_RUN=1 ;;
        --no-secrets)       GEN_SECRETS=0 ;;
        --no-report)        SHOW_REPORT=0 ;;
        --non-interactive|--no-prompt) INTERACTIVE=0 ;;
        -h|--help)
            sed -n '2,/^# ===/p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) fail "Unknown option: $1 (use --help)" ;;
    esac
    shift
done

# Auto-disable prompts if stdin is not a TTY (e.g. piped, CI).
if [[ ! -t 0 ]]; then
    INTERACTIVE=0
fi

# ── Resolve a Python that can run helpers ──────────────────────────────────────
resolve_python() {
    local candidates=(
        "$REPO_ROOT/.venv/bin/python"
        "$(command -v python3 || true)"
        "$(command -v python || true)"
    )
    for p in "${candidates[@]}"; do
        [[ -x "$p" ]] && { echo "$p"; return; }
    done
    fail "No usable Python found. Install Python 3 or run ./setup.sh --venv first."
}
PY="$(resolve_python)"

py_has_module() {
    "$PY" -c "import $1" 2>/dev/null
}

# ── Sync example → real (additive merge) ───────────────────────────────────────
sync_file() {
    local rel_src="$1" rel_dst="$2"
    local src="$REPO_ROOT/$rel_src" dst="$REPO_ROOT/$rel_dst"

    if [[ ! -f "$src" ]]; then
        warn "Template missing: $rel_src — skipping"
        return
    fi

    if [[ ! -f "$dst" ]]; then
        if (( DRY_RUN )); then
            info "[dry-run] would create $rel_dst from $rel_src"
        else
            cp "$src" "$dst"
            ok "Created $rel_dst from template"
        fi
        return
    fi

    local result
    result=$(SETUP_CONFIG_DRY="$DRY_RUN" "$PY" - "$src" "$dst" <<'PYEOF'
import os, re, sys
from pathlib import Path

src = Path(sys.argv[1]).read_text().splitlines()
dst_path = Path(sys.argv[2])
dst_lines = dst_path.read_text().splitlines()
dry = os.environ.get("SETUP_CONFIG_DRY") == "1"

KEY_RE = re.compile(r"^([A-Z_][A-Z0-9_]*)=")

def key_set(lines):
    return {m.group(1) for line in lines if (m := KEY_RE.match(line))}

dst_keys, src_keys = key_set(dst_lines), key_set(src)
missing_keys = [k for k in src_keys if k not in dst_keys]

if not missing_keys:
    print("0")
    sys.exit(0)

# For each missing key, capture the contiguous comment block above it.
new_blocks: list[tuple[str, list[str], str]] = []
for i, line in enumerate(src):
    m = KEY_RE.match(line)
    if not m or m.group(1) not in missing_keys:
        continue
    j = i - 1
    block: list[str] = []
    while j >= 0 and src[j].lstrip().startswith("#"):
        block.append(src[j])
        j -= 1
    block.reverse()
    new_blocks.append((m.group(1), block, line))

if not dry:
    out = list(dst_lines)
    if out and out[-1].strip() != "":
        out.append("")
    out.append("# ── Added by setup-config.sh ──")
    for _, comments, ln in new_blocks:
        out.append("")
        out.extend(comments)
        out.append(ln)
    dst_path.write_text("\n".join(out) + "\n")

print(len(new_blocks))
for k, _, _ in new_blocks:
    print(k)
PYEOF
    )

    local count first_line
    first_line="${result%%$'\n'*}"
    count="$first_line"
    local keys="${result#*$'\n'}"
    [[ "$count" == "0" ]] && keys=""

    if [[ "$count" == "0" ]]; then
        ok "$rel_dst — up-to-date"
    elif (( DRY_RUN )); then
        info "[dry-run] $rel_dst would gain $count new key(s):"
        printf '       • %s\n' $keys
    else
        ok "$rel_dst — added $count new key(s):"
        printf '       • %s\n' $keys
    fi
}

# ── Auto-fill a blank secret with a generator ──────────────────────────────────
fill_blank_secret() {
    local key="$1" gen_cmd="$2" file="$3"

    grep -qE "^${key}=$" "$file" 2>/dev/null || return 0

    if (( DRY_RUN )); then
        info "[dry-run] would auto-generate $key in $(realpath --relative-to "$REPO_ROOT" "$file" 2>/dev/null || echo "$file")"
        return 0
    fi

    local val
    val=$(eval "$gen_cmd") || { warn "Failed to generate $key (skipping)"; return 0; }

    # macOS sed needs an empty extension arg
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s|^${key}=$|${key}=${val}|" "$file"
    else
        sed -i "s|^${key}=$|${key}=${val}|" "$file"
    fi
    ok "Generated $key in $(basename "$file")"
}

# ── Set a key's value across every synced file where it currently sits blank ──
write_key_value() {
    local key="$1" val="$2"
    [[ -z "$val" ]] && return 0
    # Escape sed-special chars in val: \ & |
    local esc
    esc=$(printf '%s' "$val" | sed -e 's/[\\&|]/\\&/g')
    for entry in "${MAPPINGS[@]}"; do
        local dst="$REPO_ROOT/${entry##*:}"
        [[ -f "$dst" ]] || continue
        if grep -qE "^${key}=$" "$dst"; then
            if [[ "$(uname)" == "Darwin" ]]; then
                sed -i '' "s|^${key}=$|${key}=${esc}|" "$dst"
            else
                sed -i "s|^${key}=$|${key}=${esc}|" "$dst"
            fi
            ok "Wrote $key → ${entry##*:}"
        fi
    done
}

# ── Interactively prompt for blank PROMPT_KEYS ────────────────────────────────
prompt_for_keys() {
    local any_blank=0
    for spec in "${PROMPT_KEYS[@]}"; do
        local key="${spec%%|*}"
        local rest="${spec#*|}"
        local desc="${rest%|*}"
        local secret="${rest##*|}"

        # Only prompt if currently blank in at least one synced file.
        local blank=0
        for entry in "${MAPPINGS[@]}"; do
            local dst="$REPO_ROOT/${entry##*:}"
            [[ -f "$dst" ]] || continue
            if grep -qE "^${key}=$" "$dst"; then blank=1; break; fi
        done
        (( blank == 0 )) && continue

        if (( any_blank == 0 )); then
            hdr "Interactive setup"
            any_blank=1
        fi

        printf "  ${B}%s${N} — %s\n" "$key" "$desc"

        if (( DRY_RUN )); then
            info "[dry-run] would prompt for $key"
            continue
        fi

        local val=""
        if [[ "$secret" == "1" ]]; then
            read -rsp "    > " val; echo
        else
            read -rp "    > " val
        fi
        val="$(printf '%s' "$val" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

        if [[ -z "$val" ]]; then
            warn "Skipped $key (left blank — fill in manually later)"
            continue
        fi
        write_key_value "$key" "$val"
    done
}

# ── Discover keys still blank in any synced file (for the reminder) ────────────
report_manual_keys() {
    local found=0
    for entry in "${MAPPINGS[@]}"; do
        local dst="$REPO_ROOT/${entry##*:}"
        [[ -f "$dst" ]] || continue
        for k in "${MANUAL_KEYS[@]}"; do
            if grep -qE "^${k}=$" "$dst"; then
                if (( found == 0 )); then
                    hdr "Manual values still needed"
                    found=1
                fi
                printf "  • %s  ${C}(in %s)${N}\n" "$k" "${entry##*:}"
            fi
        done
    done
    if (( found == 0 )); then
        ok "All known credential slots are populated."
    fi
}

# ── Run ────────────────────────────────────────────────────────────────────────
hdr "AlphaForge — config sync"
info "Python: $PY"
(( DRY_RUN )) && warn "DRY RUN — no files will be modified"

hdr "Syncing template → real"
for entry in "${MAPPINGS[@]}"; do
    sync_file "${entry%%:*}" "${entry##*:}"
done

if (( GEN_SECRETS )); then
    hdr "Auto-generating blank secrets"
    if ! py_has_module cryptography; then
        warn "cryptography not installed — Fernet keys will be skipped."
        warn "Run ./setup.sh --backend (or 'uv sync') first, then re-run this script."
        FERNET_KEYS=()
    fi
    for entry in "${MAPPINGS[@]}"; do
        dst="$REPO_ROOT/${entry##*:}"
        [[ -f "$dst" ]] || continue
        for k in "${FERNET_KEYS[@]}"; do
            fill_blank_secret "$k" \
                "$PY -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'" \
                "$dst"
        done
        for k in "${RANDOM_KEYS[@]}"; do
            fill_blank_secret "$k" \
                "$PY -c 'import secrets; print(secrets.token_urlsafe(48))'" \
                "$dst"
        done
    done
fi

if (( INTERACTIVE )); then
    prompt_for_keys
fi

if (( SHOW_REPORT )); then
    report_manual_keys
fi

hdr "Done"
info "Re-run this script anytime an .env.example template is updated."
info "Real secrets live in .env.cred.local (gitignored). Never put them in .env.cred.example."
