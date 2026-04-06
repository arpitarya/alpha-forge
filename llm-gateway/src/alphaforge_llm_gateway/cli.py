"""CLI interface for the LLM Gateway — standalone terminal usage."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from alphaforge_llm_gateway.types import LLMProvider, LLMResponse, QueryType


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alphaforge-llm-gateway",
        description="AlphaForge LLM Gateway — free multi-provider AI for Indian market analysis",
    )
    parser.add_argument("--env-file", help="Path to .env file for API keys")
    parser.add_argument(
        "--provider",
        choices=[p.value for p in LLMProvider],
        help="Force a specific provider (skip router)",
    )
    parser.add_argument("--model", help="Force a specific model")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Output raw JSON")
    parser.add_argument(
        "--no-disclaimer", action="store_true", help="Suppress disclaimer in output"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # analyze-screener
    sc = sub.add_parser("analyze-screener", help="Analyze screener output (stdin or file)")
    sc.add_argument("-f", "--file", help="Path to screener output file")

    # explain-picks
    ep = sub.add_parser("explain-picks", help="Translate SHAP explanations to plain English")
    ep.add_argument("-f", "--file", help="Path to SHAP explanation file")

    # chat
    ch = sub.add_parser("chat", help="Interactive single-turn or piped chat")
    ch.add_argument("message", nargs="?", help="Chat message (or pipe via stdin)")

    # complete
    cp = sub.add_parser("complete", help="Raw completion with explicit query type")
    cp.add_argument(
        "--type",
        choices=[q.value for q in QueryType],
        default="chat",
        help="Query type for routing",
    )
    cp.add_argument("message", nargs="?", help="Message (or pipe via stdin)")

    # benchmark
    sub.add_parser("benchmark", help="Run auto-benchmark across all providers")

    # providers
    sub.add_parser("providers", help="Show provider health & remaining quota")

    return parser


def _read_input(args: argparse.Namespace) -> str:
    """Read input from --file flag, positional arg, or stdin."""
    if hasattr(args, "file") and args.file:
        with open(args.file) as f:
            return f.read()
    if hasattr(args, "message") and args.message:
        return args.message
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def _format_response(response: LLMResponse, json_output: bool, show_disclaimer: bool) -> str:
    """Format an LLMResponse for terminal output."""
    if json_output:
        return json.dumps({
            "content": response.content,
            "model": response.model,
            "provider": response.provider.value,
            "tokens_used": response.tokens_used,
            "latency_ms": response.latency_ms,
            "cost": response.cost,
        }, indent=2)

    parts = [response.content]
    parts.append(
        f"\n--- [{response.provider.value}/{response.model}] "
        f"{response.latency_ms:.0f}ms | {response.tokens_used} tokens | $0.00"
    )
    if show_disclaimer:
        parts.append(
            "\n⚠️  NOT SEBI registered investment advice. For personal research only."
        )
    return "\n".join(parts)


async def _run(args: argparse.Namespace) -> None:
    from alphaforge_llm_gateway.gateway import LLMGateway

    gateway = LLMGateway.from_env(env_file=args.env_file)

    provider = LLMProvider(args.provider) if args.provider else None
    show_disclaimer = not args.no_disclaimer

    if args.command == "providers":
        statuses = await gateway.providers_status()
        if args.json_output:
            print(json.dumps(statuses, indent=2))
        else:
            print("Provider Status")
            print("=" * 60)
            for s in statuses:
                health = "✅" if s["healthy"] else "❌"
                local = " (local)" if s["is_local"] else ""
                print(f"  {health} {s['provider']}{local}")
                print(f"    Default model: {s['default_model']}")
                print(f"    Models: {len(s['models'])}")
                print(f"    Utilization: {s['utilization_pct']}%")
                if s["remaining"]:
                    rem = ", ".join(f"{k}: {v}" for k, v in s["remaining"].items())
                    print(f"    Remaining: {rem}")
                print()
        return

    if args.command == "benchmark":
        from alphaforge_llm_gateway.benchmark import run_benchmark

        results = await run_benchmark(gateway, json_output=args.json_output)
        print(results)
        return

    if args.command == "analyze-screener":
        text = _read_input(args)
        if not text:
            print("Error: No input. Provide via -f <file> or pipe via stdin.", file=sys.stderr)
            sys.exit(1)
        response = await gateway.analyze_screener(text)
        print(_format_response(response, args.json_output, show_disclaimer))
        return

    if args.command == "explain-picks":
        text = _read_input(args)
        if not text:
            print("Error: No input. Provide via -f <file> or pipe via stdin.", file=sys.stderr)
            sys.exit(1)
        response = await gateway.explain_picks(text)
        print(_format_response(response, args.json_output, show_disclaimer))
        return

    if args.command == "chat":
        text = _read_input(args)
        if not text:
            # Interactive mode — read one line
            try:
                text = input("> ")
            except (EOFError, KeyboardInterrupt):
                return
        response = await gateway.complete(
            QueryType.CHAT,
            [{"role": "user", "content": text}],
            provider=provider,
            model=args.model,
        )
        print(_format_response(response, args.json_output, show_disclaimer))
        return

    if args.command == "complete":
        text = _read_input(args)
        if not text:
            print("Error: No input.", file=sys.stderr)
            sys.exit(1)
        query_type = QueryType(args.type)
        response = await gateway.complete(
            query_type,
            [{"role": "user", "content": text}],
            provider=provider,
            model=args.model,
        )
        print(_format_response(response, args.json_output, show_disclaimer))
        return

    # No command — show help
    _build_parser().print_help()


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    asyncio.run(_run(args))
