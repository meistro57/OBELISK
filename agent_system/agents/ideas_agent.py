import os
import openai


class IdeasAgent:
    """
    Uses OpenAI API to brainstorm new ideas for improving the app based on architecture plans.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        openai.api_key = self.api_key
        self.model = model

    def generate_ideas(self, project_name: str, architecture_spec: str) -> str:
        """
        Generates a list of creative enhancements and features for the project.
        """
        prompt = (
            f"You are an innovation specialist. Given the architecture plan for '{project_name}', "
            "suggest creative features, enhancements, and improvements to make the app more valuable:\n\n"
            f"{architecture_spec}\n\n"
            "Provide your ideas as a numbered or bulleted list."
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI Ideas API error: {e}") from e

        choices = getattr(response, "choices", None)
        if not choices:
            raise RuntimeError("Empty response from OpenAI Ideas API")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("No content in Ideas API response")
        return content.strip()
