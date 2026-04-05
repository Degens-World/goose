#!/usr/bin/env python3
"""
Run Danny's static-site build loop without requiring a Goose binary.
"""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


DEFAULT_AGENT_SCRIPT = Path(r"D:\Agent Heartbeat\ollama_agent.py")


def load_audit_module(audit_path: Path):
    spec = importlib.util.spec_from_file_location("danny_site_audit", audit_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load audit module from {audit_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_agent(
    agent_script: Path,
    project_dir: Path,
    prompt: str,
    model: str,
    ollama_url: str,
    call_timeout_secs: int,
    agent_timeout_secs: int,
) -> str:
    proc = subprocess.run(
        [
            sys.executable,
            str(agent_script),
            prompt,
            "--model",
            model,
            "--url",
            ollama_url,
            "--timeout",
            str(call_timeout_secs),
            "--max-iters",
            "60",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(project_dir),
        timeout=agent_timeout_secs,
    )
    return ((proc.stdout or "") + (proc.stderr or "")).strip()


def build_prompt(project_name: str, project_dir: Path, description: str, issues: list[str], audit_markdown: str) -> str:
    issue_block = "\n".join(f"- {issue}" for issue in issues) if issues else "- create the required project files"
    build_mode = "rebuild and improve the existing site" if any(project_dir.iterdir()) else "build the site from scratch"
    description_line = description.strip() or "Upgrade the existing static site so it feels like a real crypto/AI/degen product."
    return (
        "You are Danny's dedicated static-site builder.\n\n"
        f"Project: {project_name}\n"
        f"Project directory: {project_dir}\n"
        f"Description: {description_line}\n\n"
        "Rules:\n"
        "- Work only inside the project directory above.\n"
        "- The machine is Windows. Do not rely on Unix-only shell commands like ls, mv, or sed.\n"
        "- Do not touch git, deployment, or heartbeat logs.\n"
        "- Do not use append_task_row, git_publish, or deploy_static_site.\n"
        "- Create or update these files: index.html, style.css, app.js, README.md, vercel.json.\n"
        "- Keep it a pure static HTML/CSS/JS site with no build system.\n"
        f"- For this run, {build_mode}.\n"
        "- Do not replace the project with a thin hero page.\n"
        "- Produce a bold, content-rich interface with multiple visible sections, purposeful styling, and real interactivity.\n"
        "- JavaScript must drive meaningful UI state, filtering, toggles, calculators, charts, or derived metrics.\n"
        "- If the audit says app logic or data is weak, you must rewrite app.js so it contains substantive datasets, derived metrics, and event-driven UI updates.\n"
        "- Update README.md so it accurately describes the improved product.\n"
        "- When the project is materially improved, call done() with a short summary.\n\n"
        "Quality issues to fix:\n"
        f"{issue_block}\n\n"
        "Current audit report:\n"
        f"{audit_markdown}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or rebuild a static site until it clears Danny's quality bar.")
    parser.add_argument("project_dir", help="Absolute or relative project directory")
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--description", default="", help="Project description")
    parser.add_argument("--model", default="qwen3-coder:30b", help="Ollama model")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--call-timeout-secs", type=int, default=240, help="Timeout per Ollama call")
    parser.add_argument("--agent-timeout-secs", type=int, default=1800, help="Timeout for the full agent run")
    parser.add_argument("--max-attempts", type=int, default=2, help="Improvement attempts before giving up")
    parser.add_argument("--agent-script", default=str(DEFAULT_AGENT_SCRIPT), help="Path to ollama_agent.py")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    agent_script = Path(args.agent_script).resolve()
    distro_dir = Path(__file__).resolve().parent
    repo_root = distro_dir.parent.parent
    audit_path = repo_root / "workflow_recipes" / "danny_static_site_upgrade" / "danny_site_audit.py"

    project_dir.mkdir(parents=True, exist_ok=True)
    if not agent_script.exists():
        print(f"[danny-upgrade-tool] missing ollama agent script: {agent_script}")
        return 1
    if not audit_path.exists():
        print(f"[danny-upgrade-tool] missing audit script: {audit_path}")
        return 1

    audit_module = load_audit_module(audit_path)
    report = audit_module.audit(project_dir)
    if report["status"] == "pass":
        print(f"[danny-builder-tool] {args.project_name} already passes Danny audit")
        print(audit_module.to_markdown(report))
        return 0

    for attempt in range(1, max(1, args.max_attempts) + 1):
        audit_markdown = audit_module.to_markdown(report)
        prompt = build_prompt(
            args.project_name,
            project_dir,
            args.description,
            list(report.get("quality_issues", [])) or list(report.get("missing_files", [])),
            audit_markdown,
        )
        output = run_agent(
            agent_script,
            project_dir,
            prompt,
            args.model,
            args.ollama_url,
            args.call_timeout_secs,
            args.agent_timeout_secs,
        )
        print(f"[danny-builder-tool] attempt {attempt} agent output:\n{output}\n")

        report = audit_module.audit(project_dir)
        if report["status"] == "pass":
            print(f"[danny-builder-tool] PASS after attempt {attempt}")
            print(audit_module.to_markdown(report))
            return 0

    print(f"[danny-builder-tool] FAIL after {max(1, args.max_attempts)} attempt(s)")
    print(audit_module.to_markdown(report))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
