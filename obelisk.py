#!/usr/bin/env python3
"""
Natural-language CLI wrapper for OBELISK.

If invoked with positional text only, classifies and routes the command via TaskRouter.
Otherwise, falls back to flag-driven main.py behavior.
"""
import sys
import os
import argparse
import subprocess

from dotenv import load_dotenv
from agent_system.task_router import TaskRouter


def run_nl(command: str):
    """Route a natural-language command through the TaskRouter."""
    router = TaskRouter(
        anthro_model=os.getenv("OBELISK_ARCH_MODEL", "claude-v1"),
        openai_model=os.getenv("OBELISK_QC_MODEL", "gpt-4"),
    )
    resp = router.route_task(command)
    print(resp)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(prog="obelisk", add_help=False)
    # detect flags for main
    parser.add_argument("--project")
    parser.add_argument("--requirements")
    parser.add_argument("--output-dir")
    parser.add_argument("--help", action="store_true")
    args, extra = parser.parse_known_args()

    # If only free text (no flags), treat as NL command
    if not any([args.project, args.requirements, args.output_dir]) and extra:
        cmd = " ".join(extra)
        return run_nl(cmd)

    # Otherwise fallback to main.py CLI
    cmd = [sys.executable, "main.py"] + sys.argv[1:]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
