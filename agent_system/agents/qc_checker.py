import os
import openai


class QCChecker:
    """
    Uses OpenAI API to perform quality checks on generated code.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        openai.api_key = self.api_key
        self.model = model

    def check_directory(self, code_dir: str) -> str:
        """
        Checks code quality for all code under code_dir and returns a report.
        """
        report_parts = []
        for root, dirs, files in os.walk(code_dir):
            for fname in files:
                if fname.endswith((".py", ".js", ".ts", ".java", ".go")):
                    path = os.path.join(root, fname)
                    with open(path, "r") as f:
                        content = f.read()
                    report_parts.append(f"File: {path}\n{content}\n\n")
        prompt = (
            "You are a code quality analyst. Review the following code files for bugs, "
            "best practices, and potential improvements, and provide a concise report:\n\n"
            + "\n".join(report_parts)
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI QC API error: {e}") from e

        choices = getattr(response, "choices", None)
        if not choices or not choices:
            raise RuntimeError("Empty response from OpenAI QC API")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("No content in QC API response")
        return content.strip()
