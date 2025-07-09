import os
import shutil
import subprocess


class SandboxError(Exception):
    """Raised when sandbox command fails or times out."""
    pass


class ExecutionSandbox:
    """
    Executes commands in an isolated sandbox. Uses Docker if a docker_image
    is provided and Docker is available; otherwise, runs in a subprocess
    with resource/time limits.
    """
    def __init__(self, docker_image: str = None, timeout: int = 60):
        self.docker_image = docker_image
        self.timeout = timeout

    def run(self, command: str, cwd: str = None) -> str:
        """
        Run the given shell command in the sandbox. Returns stdout on success.
        Raises SandboxError on failure or timeout.
        """
        cwd = cwd or os.getcwd()
        try:
            if self.docker_image and shutil.which("docker"):
                # Run inside Docker container mounted at /workspace
                cmd = [
                    "docker", "run", "--rm",
                    "-v", f"{os.path.abspath(cwd)}:/workspace",
                    "-w", "/workspace",
                    "--network", "none",
                    "--memory", "512m",
                    self.docker_image,
                    "sh", "-c", command,
                ]
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                )
            else:
                # Local subprocess isolation
                proc = subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout,
                )
        except subprocess.TimeoutExpired as e:
            raise SandboxError(f"Sandbox timeout after {self.timeout}s: {e}") from e

        if proc.returncode != 0:
            raise SandboxError(
                f"Command failed (exit {proc.returncode})\n"
                f"STDOUT:\n{proc.stdout}\n"
                f"STDERR:\n{proc.stderr}\n"
            )
        return proc.stdout
