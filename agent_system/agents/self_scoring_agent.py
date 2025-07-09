import os
import json
import openai


class SelfScoringAgent:
    """
    Uses an LLM to self-evaluate a given output (code or text).
    Returns a score, confidence, and suggestions for improvement.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set for SelfScoringAgent")
        openai.api_key = self.api_key
        self.model = model

    def evaluate(self, content: str) -> dict:
        """
        Evaluate the given content and return a dict with:
        - score: numeric score (0-10)
        - confidence: estimated confidence (0-100%)
        - suggestions: list of improvement suggestions
        """
        prompt = (
            "You are an expert evaluator. "
            "Evaluate the following content and provide:\n"
            "1. A numeric score from 0 to 10 (10 is best quality).\n"
            "2. A confidence percentage (0-100%).\n"
            "3. A bullet list of 3-5 concrete suggestions for improvement.\n\n"
            "Content to evaluate:\n```python\n"
            f"{content}\n```\n\n"
            "Respond in JSON format with keys: score, confidence, suggestions."
        )
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        msg = response.choices[0].message.get("content", "").strip()
        try:
            result = json.loads(msg)
        except json.JSONDecodeError:
            raise RuntimeError(f"Unable to parse JSON from model response: {msg}")
        return result
