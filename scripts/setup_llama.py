#!/usr/bin/env python3
"""
Script to download and configure a local LLaMA model via Hugging Face.
"""
import os
import shutil
import argparse

from huggingface_hub import snapshot_download


def main():
    parser = argparse.ArgumentParser(
        description="Download and set up a LLaMA model locally."
    )
    parser.add_argument(
        "--model",
        default="decapoda-research/llama-7b-hf",
        help="Hugging Face repo ID of the LLaMA model to download",
    )
    parser.add_argument(
        "--dest",
        default=os.getenv("LLAMA_MODEL_PATH", "./models/llama"),
        help="Destination directory to cache the model",
    )
    args = parser.parse_args()

    # Check for llama CLI availability
    if shutil.which("llama") is None:
        print("WARNING: 'llama' CLI not found in PATH. \n"
              "Please install llama.cpp tools per their documentation.")

    os.makedirs(args.dest, exist_ok=True)
    print(f"Downloading model '{args.model}' to '{args.dest}'...")
    try:
        repo_path = snapshot_download(repo_id=args.model, cache_dir=args.dest)
    except Exception as e:
        print(f"Error downloading model: {e}")
        return 1

    print(f"Model downloaded to: {repo_path}")
    print("Add or update LLAMA_MODEL_PATH in your .env file to point to this directory:")
    print(f"LLAMA_MODEL_PATH={args.dest}")
    return 0


if __name__ == '__main__':
    exit(main())
