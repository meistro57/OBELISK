import os
import anthropic
from agent_system.prompt_system import PromptSystem


class CodeArchitect:
    """
    Uses Anthropic API to generate high-level architecture plans.
    """
    def __init__(self, api_key: str = None, model: str = "claude-v1"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        self.client = anthropic.Client(api_key=self.api_key)
        self.model = model
        self.prompt_sys = PromptSystem()

    def generate_architecture(self, project_name: str, requirements: str = "") -> str:
        """
        Generates an architecture plan for the given project.
        """
        tmpl = self.prompt_sys.get("Claude", "generate_architecture")
        if tmpl:
            prompt = tmpl.format(project=project_name, requirements=requirements)
        else:
            prompt = (
                f"You are a software architect. Design a complete software stack for a project named '{project_name}' "
                f"with the following requirements:\n{requirements}\n"
                "Provide a structured plan including components, technologies, and high-level overview."
            )
        try:
            response = self.client.completions.create(
                model=self.model,
                prompt=anthropic.HUMAN_PROMPT + prompt + anthropic.AI_PROMPT,
                max_tokens=1000,
                stop_sequences=[anthropic.HUMAN_PROMPT],
            )
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e

        completion = getattr(response, "completion", None)
        if not completion:
            raise RuntimeError("Empty response from Anthropic API")
        return completion.strip()
