#!/usr/bin/env python3
"""
Standalone script to use the Anthropic API to read through an entire project
and produce a JSON report suitable for Codex to consume for code improvements.
"""
import os
import sys
import json
import argparse

import anthropic


def gather_code_files(root_dir: str) -> list:
    """
    Walks root_dir, returning a list of code-related file paths.
    Hidden directories and common cache dirs are skipped.
    """
    code_exts = ('.py', '.js', '.ts', '.java', '.go', '.c', '.cpp', '.h',
                 '.md', '.yml', '.yaml', '.json')
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        # skip hidden or cache dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for fn in filenames:
            if fn.startswith('.'):
                continue
            if fn.lower().endswith(code_exts):
                files.append(os.path.join(root, fn))
    return files


def load_files_content(paths: list) -> str:
    """
    Reads and concatenates contents of files in paths into a single string,
    prefixed by file markers.
    """
    parts = []
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        parts.append(f"---\nFile: {path}\n{content}\n")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze project files via Anthropic and output a JSON report."
    )
    parser.add_argument(
        '--model', default='claude-v1',
        help='Anthropic model to use for analysis'
    )
    parser.add_argument(
        '--output', default='report.json',
        help='Path to write the JSON report'
    )
    args = parser.parse_args()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print('Error: ANTHROPIC_API_KEY not set in environment', file=sys.stderr)
        sys.exit(1)

    client = anthropic.Client(api_key=api_key)
    root = os.getcwd()
    files = gather_code_files(root)
    if not files:
        print('No code files found to analyze.', file=sys.stderr)
        sys.exit(1)

    project_text = load_files_content(files)
    prompt = (
        "You are a code review assistant. Produce a JSON report with two top-level keys:"
        " 'summary' (a brief overview of project strengths and weaknesses),"
        " and 'files' (an object mapping file paths to lists of issues or improvement suggestions)."
        " Respond with only valid JSON.\n\n"
        f"{project_text}\n"
    )

    try:
        response = client.completions.create(
            model=args.model,
            prompt=anthropic.HUMAN_PROMPT + prompt + anthropic.AI_PROMPT,
            max_tokens=2000,
            stop_sequences=[anthropic.HUMAN_PROMPT],
        )
    except Exception as e:
        print(f'Anthropic API error: {e}', file=sys.stderr)
        sys.exit(1)

    completion = getattr(response, 'completion', '').strip()
    try:
        report = json.loads(completion)
    except json.JSONDecodeError:
        print('Failed to parse JSON from Anthropic response:', file=sys.stderr)
        print(completion, file=sys.stderr)
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f'Report written to {args.output}')


if __name__ == '__main__':
    main()
