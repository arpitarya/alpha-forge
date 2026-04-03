#!/bin/bash
# AlphaForge — Local setup script for macOS (Apple Silicon)
# Installs and starts PostgreSQL + Redis natively via Homebrew.
# No Docker required.

set -e

echo "🔧 AlphaForge — Local Infrastructure Setup"
echo "============================================"

# ── Check Homebrew ───────────────────────────────
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install from https://brew.sh"
    exit 1
fi

# ── Install PostgreSQL ───────────────────────────
if ! brew list postgresql@16 &> /dev/null; then
    echo "📦 Installing PostgreSQL 16..."
    brew install postgresql@16
else
    echo "✅ PostgreSQL 16 already installed"
fi

# ── Install Redis ────────────────────────────────
if ! brew list redis &> /dev/null; then
    echo "📦 Installing Redis..."
    brew install redis
else
    echo "✅ Redis already installed"
fi

# ── Start services ───────────────────────────────
echo "🚀 Starting PostgreSQL..."
brew services start postgresql@16

echo "🚀 Starting Redis..."
brew services start redis

# ── Wait for PostgreSQL to be ready ──────────────
echo "⏳ Waiting for PostgreSQL..."
for i in {1..10}; do
    if pg_isready -q 2>/dev/null; then
        break
    fi
    sleep 1
done

# ── Create database and user ─────────────────────
if psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw alphaforge; then
    echo "✅ Database 'alphaforge' already exists"
else
    echo "📦 Creating database and user..."
    createuser alphaforge 2>/dev/null || true
    createdb alphaforge -O alphaforge 2>/dev/null || true
    psql -c "ALTER USER alphaforge WITH PASSWORD 'alphaforge';" 2>/dev/null || true
    echo "✅ Database 'alphaforge' created"
fi

echo ""
echo "============================================"
echo "✅ Infrastructure ready!"
echo ""
echo "  PostgreSQL: localhost:5432 (user: alphaforge, db: alphaforge)"
echo "  Redis:      localhost:6379"
echo ""
echo "Next steps:"
echo "  cd backend && pdm install && pdm run dev"
echo "  cd frontend && pnpm install && pnpm dev"
echo ""
echo "Or start everything at once:"
echo "  make dev-local"
echo "============================================"
