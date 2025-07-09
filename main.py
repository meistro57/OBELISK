#!/usr/bin/env python3
"""
Entry point for the agent system to generate and QC complete software stacks.
"""
import argparse
import logging
import os
import sys
import shutil
import traceback

from dotenv import load_dotenv

from agent_system.agent_registry import AgentRegistry
from agent_system.agents.code_generator import CodeGenerator


def main():
    load_dotenv()
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    # Show availability of supported LLMs (green = available, red = unavailable)
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"
    has_anthro = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_lmstudio = shutil.which("lmstudio") is not None
    has_llama = shutil.which("llama") is not None
    print("Model availability:")
    for role, models in [
        ("Architect", ["claude-v1", "lmstudio", "llama"]),
        ("Ideas", ["gpt-4", "gpt-3.5-turbo", "llama", "lmstudio"]),
        ("Creativity", ["claude-v1", "lmstudio", "llama"]),
        ("QC", ["gpt-4", "gpt-3.5-turbo", "llama", "lmstudio"]),
    ]:
        print(f"  {role} models:")
        for m in models:
            available = (
                (m.startswith("claude") and has_anthro)
                or (m.startswith("gpt") and has_openai)
                or (m == "lmstudio" and has_lmstudio)
                or (m == "llama" and has_llama)
            )
            color = GREEN if available else RED
            print(f"    {color}{m}{RESET}")

    parser = argparse.ArgumentParser(
        description="Automated system for software stack generation and QC"
    )
    parser.add_argument(
        "--project", required=True, help="Name of the project to generate"
    )
    parser.add_argument(
        "--requirements", default="", help="High-level requirements or description"
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory to place generated code"
    )
    parser.add_argument(
        "--architect-model",
        default="claude-v1",
        help="Anthropic (or local) model to use for architecture (e.g. claude-v1, lmstudio, llama)",
    )
    parser.add_argument(
        "--qc-model",
        default="gpt-4",
        help="OpenAI (or local) model to use for QC (e.g. gpt-4, gpt-3.5-turbo, llama, lmstudio)",
    )
    parser.add_argument(
        "--analysis-report",
        help="Path to JSON analysis report for Codex to apply improvements",
    )
    parser.add_argument(
        "--use-memory",
        action="store_true",
        help="Enable SQLite memory of all agent interactions",
    )
    parser.add_argument(
        "--memory-db",
        help="Path to SQLite memory DB (overrides MEMORY_DB_PATH env)",
    )
    parser.add_argument(
        "--ideas-model",
        default="gpt-4",
        help="OpenAI (or local) model to use for brainstorming ideas (e.g. gpt-4, gpt-3.5-turbo, llama, lmstudio)",
    )
    parser.add_argument(
        "--creativity-model",
        default="claude-v1",
        help="Anthropic (or local) model to use for refining ideas (e.g. claude-v1, lmstudio, llama)",
    )
    parser.add_argument(
        "--scoring-model",
        default="gpt-4",
        help="OpenAI (or local) model to use for self-scoring outputs (e.g. gpt-4, gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Enable execution sandbox for running tests or custom commands on generated code",
    )
    parser.add_argument(
        "--sandbox-docker-image",
        help="Docker image to use for sandbox isolation (requires --sandbox)",
    )
    parser.add_argument(
        "--test-command",
        default="pytest",
        help="Command to execute in sandbox when --sandbox is enabled (default: pytest)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run code validation (pylint & black) after code generation",
    )
    parser.add_argument(
        "--validate-flags",
        default="",
        help="Additional flags for validation commands",
    )
    parser.add_argument(
        "--generate-tests",
        action="store_true",
        help="Automatically generate pytest harness for the generated code",
    )
    parser.add_argument(
        "--test-harness-model",
        default="gpt-4",
        help="OpenAI (or local) model to use for test harness generation",
    )
    args = parser.parse_args()

    fallback_models = {
        'architect': ['claude-v1', 'lmstudio', 'llama'],
        'ideas': ['gpt-4', 'gpt-3.5-turbo', 'llama', 'lmstudio'],
        'creativity': ['claude-v1', 'lmstudio', 'llama'],
        'qc': ['gpt-4', 'gpt-3.5-turbo', 'llama', 'lmstudio'],
    }

    spec = None
    # Initialize memory if enabled
    registry = AgentRegistry()
    if args.use_memory:
        from agent_system.memory import Memory
        memory = Memory(db_path=args.memory_db)
    else:
        memory = None

    # Generate architecture plan using AgentRegistry
    for model in [args.architect_model] + [m for m in fallback_models['architect'] if m != args.architect_model]:
        try:
            architect = registry.get_agent('CodeArchitect', model=model)
            spec = architect.generate_architecture(args.project, args.requirements)
            if spec and spec.strip():
                # Log reasoning for architecture plan
                if memory:
                    from agent_system.logging import ReasoningLog
                    rl = ReasoningLog(memory)
                    rl.log('CodeArchitect', model, spec)
                print(f"[Architect] Architecture plan generated by {model}.")
                break
        except Exception:
            continue
    if not spec or not spec.strip():
        print(f"[ERROR][Architect] All models failed or returned empty for architecture plan: {fallback_models['architect']}", file=sys.stderr)
        sys.exit(1)
    if args.use_memory:
        memory.add("architect", "generate_architecture", spec)

    # Generate and review improvement ideas
    ideas = None
    for model in ([args.ideas_model] + [m for m in fallback_models['ideas'] if m != args.ideas_model]):
        try:
            ideas_agent = registry.get_agent('IdeasAgent', model=model)
            ideas = ideas_agent.generate_ideas(args.project, spec)
            if ideas and ideas.strip():
                print(f"[IdeasAgent] Brainstormed ideas by {model}:\n", ideas)
                break
        except Exception:
            continue
    if not ideas or not ideas.strip():
        print(f"[ERROR][IdeasAgent] All models failed or returned empty ideas: {fallback_models['ideas']}", file=sys.stderr)
        sys.exit(1)
    if args.use_memory:
        memory.add("ideas", "generate_ideas", ideas)

    creative_review = None
    for model in ([args.creativity_model] + [m for m in fallback_models['creativity'] if m != args.creativity_model]):
        try:
            creativity_agent = registry.get_agent('CreativityAgent', model=model)
            creative_review = creativity_agent.review_ideas(args.project, ideas)
            if creative_review and creative_review.strip():
                print(f"[CreativityAgent] Refined ideas review by {model}:\n", creative_review)
                break
        except Exception:
            continue
    if not creative_review or not creative_review.strip():
        print(f"[ERROR][CreativityAgent] All models failed or returned empty review: {fallback_models['creativity']}", file=sys.stderr)
        sys.exit(1)
    if args.use_memory:
        memory.add("creativity", "review_ideas", creative_review)

    try:
        os.makedirs(args.output_dir, exist_ok=True)
        generator = CodeGenerator()
        generator.generate_code(spec, args.output_dir)
        print(f"[Generator] Code generated at {args.output_dir}")
        if args.use_memory:
            memory.add("generator", "generate_code", args.output_dir)
    except Exception as e:
        print(f"[ERROR][Generator] {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    # Optional automatic test harness generation
    if args.generate_tests:
        try:
            harness = registry.get_agent('TestHarnessAgent', model=args.test_harness_model)
            tests = harness.generate_tests(args.output_dir)
            print(f"[TestHarnessAgent] Generated test files:\n{tests}")
            if args.use_memory:
                memory.add("test_harness", "generate_tests", tests)
        except Exception as e:
            print(f"[ERROR][TestHarnessAgent] {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

    # Optional validation stage (pylint + black)
    if args.validate:
        from agent_system.sandbox import ExecutionSandbox, SandboxError

        validator = ExecutionSandbox(docker_image=None)
        cmd = (
            f"pylint {args.validate_flags} {args.output_dir} && "
            f"black --check {args.validate_flags} {args.output_dir}"
        )
        try:
            val_out = validator.run(cmd)
            print(f"[Validation] Passed:\n{val_out}")
            if args.use_memory:
                memory.add("validation", "run_validation", val_out)
        except SandboxError as e:
            print(f"[ERROR][Validation] {e}", file=sys.stderr)
            sys.exit(1)

    # Apply analysis report improvements via Codex CLI
    if args.analysis_report:
        try:
            generator.apply_analysis(args.analysis_report, args.output_dir)
            print(f"[Generator] Applied analysis improvements from {args.analysis_report}")
            if args.use_memory:
                memory.add("generator", "apply_analysis", args.analysis_report)
        except Exception as e:
            print(f"[ERROR][Generator] applying analysis report: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

    # Optional execution sandbox for test commands
    if args.sandbox:
        from agent_system.sandbox import ExecutionSandbox, SandboxError

        sandbox = ExecutionSandbox(docker_image=args.sandbox_docker_image)
        try:
            output = sandbox.run(args.test_command, cwd=args.output_dir)
            print(f"[Sandbox] Command '{args.test_command}' succeeded:\n{output}")
            if args.use_memory:
                memory.add("sandbox", "run_tests", {"command": args.test_command, "output": output})
        except SandboxError as e:
            print(f"[ERROR][Sandbox] {e}", file=sys.stderr)
            sys.exit(1)

    report = None
    for model in [args.qc_model] + [m for m in fallback_models['qc'] if m != args.qc_model]:
        try:
            checker = registry.get_agent('QCChecker', model=model)
            report = checker.check_directory(args.output_dir)
            if report and str(report).strip():
                print(f"[QCChecker] Quality check report by {model}:\n", report)
                break
        except Exception:
            continue
    if not report or not str(report).strip():
        print(f"[ERROR][QCChecker] All models failed or returned empty report: {fallback_models['qc']}", file=sys.stderr)
        sys.exit(1)
    if args.use_memory:
        memory.add("qc", "check_directory", report)

    # Self-score the quality check report or final output
    try:
        scorer = registry.get_agent('SelfScoringAgent', model=args.scoring_model)
        score_result = scorer.evaluate(report)
        print("[SelfScoringAgent] Self-evaluation result:\n", score_result)
        if args.use_memory:
            memory.add("self_scoring", "evaluate", score_result)
    except Exception as e:
        print(f"[ERROR][SelfScoringAgent] {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
