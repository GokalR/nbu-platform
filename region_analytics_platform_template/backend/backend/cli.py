"""
Quick CLI for sanity-checking the pipeline without the web server.

Usage:
  python -m backend.cli "Yangiyer shahri Yuksalish mahallasida aholi soni qancha?"
"""
import asyncio
import sys

# Force UTF-8 on Windows console so Cyrillic / Latin Uzbek prints correctly.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from orchestrator import answer_question_blocking


async def _main(question: str):
    result = await answer_question_blocking(question)
    print("=" * 80)
    print("QUESTION:", result["question"])
    print(f"Routed to ({len(result['router_selected'])}): "
          + ", ".join(result["router_selected"]))
    if result["router_matched"]:
        print(f"Matched terms: {result['router_matched']}")
    print(f"Total elapsed: {result['total_elapsed_s']}s")
    print("-" * 80)
    print("ANSWER:")
    print(result["answer"])
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m backend.cli \"<savol>\"")
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    asyncio.run(_main(question))
