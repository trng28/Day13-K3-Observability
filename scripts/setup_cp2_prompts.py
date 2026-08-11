from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from langfuse import get_client


BASELINE_PROMPT = """Feature={{feature}}
Docs={{docs}}
Question={{message}}"""

CANDIDATE_PROMPT = """Answer the question concisely using the supplied context.
Feature={{feature}}
Context={{docs}}
Question={{message}}
Return a direct answer and do not expose private data."""


def find_label(client, name: str, label: str):
    try:
        return client.get_prompt(
            name,
            label=label,
            cache_ttl_seconds=0,
            max_retries=1,
            fetch_timeout_seconds=5,
        )
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the two managed prompts required by CP2")
    parser.add_argument("--apply", action="store_true", help="Create missing prompt versions in Langfuse")
    args = parser.parse_args()

    load_dotenv()
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        raise SystemExit("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are required")

    name = os.getenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    client = get_client()
    baseline = find_label(client, name, "baseline")
    candidate = find_label(client, name, "candidate")

    if not args.apply:
        print(f"baseline: {'exists' if baseline else 'missing'}")
        print(f"candidate: {'exists' if candidate else 'missing'}")
        print("Run again with --apply to create missing versions.")
        return 0

    if baseline is None:
        baseline = client.create_prompt(
            name=name,
            prompt=BASELINE_PROMPT,
            labels=["baseline", "production"],
            type="text",
            commit_message="CP2 baseline prompt",
        )
        print(f"Created baseline version {baseline.version}")
    else:
        print(f"Baseline already exists at version {baseline.version}")

    if candidate is None:
        candidate = client.create_prompt(
            name=name,
            prompt=CANDIDATE_PROMPT,
            labels=["candidate"],
            type="text",
            commit_message="CP2 candidate prompt",
        )
        print(f"Created candidate version {candidate.version}")
    else:
        print(f"Candidate already exists at version {candidate.version}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
