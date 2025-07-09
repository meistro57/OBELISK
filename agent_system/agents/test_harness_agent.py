import os
import glob
import openai


class TestHarnessAgent:
    """
    Generates a test harness for generated code using an LLM.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set for TestHarnessAgent")
        openai.api_key = self.api_key
        self.model = model

    def generate_tests(self, code_dir: str) -> str:
        """
        Scan Python source files in code_dir, prompt the LLM to generate a pytest-based
        test file per module, and write tests under code_dir/tests/.
        Returns the concatenated names of generated test files.
        """
        # Collect code files to test
        py_files = glob.glob(os.path.join(code_dir, "**", "*.py"), recursive=True)
        tests_dir = os.path.join(code_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        generated = []
        for path in py_files:
            module_rel = os.path.relpath(path, code_dir)
            with open(path, "r") as f:
                source = f.read()
            prompt = (
                f"Create pytest unit tests for the following Python module '{module_rel}'.\n"
                "Cover main functions and edge cases. Use pytest style.\n"
                "Only return valid Python code without explanation.\n"
                "Module content below:\n```python\n"
                f"{source}\n```"
            )
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            code = resp.choices[0].message.get("content", "").strip()
            if code:
                test_fname = os.path.splitext(os.path.basename(path))[0]
                test_path = os.path.join(tests_dir, f"test_{test_fname}.py")
                with open(test_path, "w") as tf:
                    tf.write(code + "\n")
                generated.append(test_path)
        return "\n".join(generated)
