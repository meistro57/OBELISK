import os
import subprocess

import anthropic
import openai


class TaskRouter:
    """
    Intelligent dispatcher that assigns tasks to Claude (Anthropic),
    Codex CLI, or ChatGPT (OpenAI) based on task description.
    """
    def __init__(self,
                 anthro_model: str = "claude-v1",
                 openai_model: str = "gpt-4",
                 codex_cli_path: str = None):
        self.anthro_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthro_key:
            raise ValueError("ANTHROPIC_API_KEY not set for Claude agent")
        self.anthro = anthropic.Client(api_key=self.anthro_key)
        self.anthro_model = anthro_model

        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set for ChatGPT agent")
        openai.api_key = self.openai_key
        self.openai_model = openai_model

        self.codex_cli = codex_cli_path or os.getenv("CODEX_CLI_PATH")
        if not self.codex_cli:
            raise ValueError("CODEX_CLI_PATH not set for Codex agent")

    def classify_task(self, description: str) -> str:
        """
        Simple heuristic to classify task description to one of: 'claude', 'codex', 'chatgpt'.
        """
        desc = description.lower()
        if any(k in desc for k in ("architecture", "design plan", "stack")):
            return "claude"
        if any(k in desc for k in ("generate code", "scaffold", "implement")):
            return "codex"
        # default to ChatGPT for general Q&A or analysis
        return "chatgpt"

    def route_task(self, description: str, **kwargs) -> str:
        """
        Dispatch the task according to classification and return the agent's response.
        Additional kwargs may include 'spec', 'output_dir', etc. for codex.
        """
        agent = self.classify_task(description)
        if agent == "claude":
            prompt = anthropic.HUMAN_PROMPT + description + anthropic.AI_PROMPT
            resp = self.anthro.completions.create(
                model=self.anthro_model,
                prompt=prompt,
                max_tokens=1000,
                stop_sequences=[anthropic.HUMAN_PROMPT],
            )
            return resp.completion.strip()

        if agent == "codex":
            # expects kwargs: spec, output_dir
            spec = kwargs.get("spec", description)
            output_dir = kwargs.get("output_dir", "./output")
            subprocess.run([
                self.codex_cli, "generate",
                "--spec", spec,
                "--out", output_dir,
            ], check=True)
            return f"Code generated to {output_dir}"

        # chatgpt
        resp = openai.ChatCompletion.create(
            model=self.openai_model,
            messages=[{"role": "user", "content": description}],
            temperature=0,
        )
        return resp.choices[0].message.get("content", "").strip()
