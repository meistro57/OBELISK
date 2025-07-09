import os
import subprocess


class CodeGenerator:
    """
    Uses Codex CLI to generate code based on architecture plans.
    """
    def __init__(self, codex_cli_path: str = None):
        self.codex_cli = codex_cli_path or os.getenv("CODEX_CLI_PATH")
        if not self.codex_cli:
            raise ValueError("CODEX_CLI_PATH not set")

    def generate_code(self, architecture_spec: str, output_dir: str) -> None:
        """
        Generates code by invoking Codex CLI with the given specification.
        """
        try:
            subprocess.run(
                [
                    self.codex_cli,
                    "generate",
                    "--spec",
                    architecture_spec,
                    "--out",
                    output_dir,
                ],
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Codex CLI failed (exit {e.returncode}): {e}"
            ) from e

    def apply_analysis(self, report_path: str, output_dir: str) -> None:
        """
        Applies analysis suggestions via Codex CLI based on a JSON report.
        """
        try:
            subprocess.run(
                [
                    self.codex_cli,
                    "improve",
                    "--report",
                    report_path,
                    "--out",
                    output_dir,
                ],
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Codex CLI improve failed (exit {e.returncode}): {e}"
            ) from e
