import os
import yaml


class PromptSystem:
    """
    Loads and provides prompt templates from a YAML file.
    """
    def __init__(self, template_path: str = None):
        self.template_path = template_path or os.getenv(
            "PROMPT_TEMPLATES_PATH", "config/task_templates.yaml"
        )
        with open(self.template_path, "r") as f:
            self.templates = yaml.safe_load(f)

    def get(self, agent_name: str, action: str, **kwargs) -> str:
        """
        Return the rendered prompt template for the given agent and action,
        formatted via Jinja2. Returns empty string if not found.
        """
        tmpl = self.templates.get(agent_name, {}).get(action, "") or ""
        if not tmpl:
            return ""
        from jinja2 import Template

        return Template(tmpl).render(**kwargs)
