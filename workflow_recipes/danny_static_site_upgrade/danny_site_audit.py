#!/usr/bin/env python3
"""
Audit a static site against Danny's minimum quality bar.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_FILES = ["index.html", "style.css", "app.js", "README.md", "vercel.json"]


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def audit(project_dir: Path) -> dict:
    result: dict = {
        "project_dir": str(project_dir),
        "missing_files": [],
        "quality_issues": [],
        "metrics": {},
        "status": "fail",
    }

    for name in REQUIRED_FILES:
        if not (project_dir / name).exists():
            result["missing_files"].append(name)

    if result["missing_files"]:
        return result

    index_text = read_text(project_dir / "index.html")
    style_text = read_text(project_dir / "style.css")
    app_text = read_text(project_dir / "app.js")
    readme_text = read_text(project_dir / "README.md")

    lower_html = index_text.lower()
    lower_css = style_text.lower()
    lower_js = app_text.lower()

    structural_tags = ["section", "article", "nav", "aside", "canvas", "svg", "input", "select", "button"]
    structural_hits = sum(1 for tag in structural_tags if f"<{tag}" in lower_html)
    control_hits = lower_html.count("<button") + lower_html.count("<input") + lower_html.count("<select")

    result["metrics"] = {
        "index_chars": len(index_text),
        "style_chars": len(style_text),
        "app_chars": len(app_text),
        "readme_chars": len(readme_text),
        "structural_hits": structural_hits,
        "interactive_controls": control_hits,
    }

    if len(index_text) < 1400:
        result["quality_issues"].append("index.html too thin")
    if len(style_text) < 1800:
        result["quality_issues"].append("style.css too thin")
    if len(app_text) < 1400:
        result["quality_issues"].append("app.js too thin")
    if len(readme_text) < 500:
        result["quality_issues"].append("README.md too thin")
    if structural_hits < 4:
        result["quality_issues"].append("not enough structural UI elements")
    if control_hits < 2:
        result["quality_issues"].append("not enough interactive controls")
    if not any(token in lower_css for token in ["gradient", "--", "@media", "grid", "backdrop-filter", "box-shadow"]):
        result["quality_issues"].append("styling lacks visual depth")
    if any(token in lower_css for token in ["background: #fff", "background:#fff", "background: white", "background:white"]):
        result["quality_issues"].append("white-page styling detected")
    if not any(token in lower_js for token in ["addeventlistener", "onclick", "onchange"]):
        result["quality_issues"].append("missing UI event handling")
    if not any(token in lower_js for token in ["const data", "let data", "fetch(", "map(", "filter(", "reduce(", "chart", "dataset", "metrics", "scenario"]):
        result["quality_issues"].append("missing substantive app logic or data")

    if not result["quality_issues"]:
        result["status"] = "pass"
    return result


def to_markdown(report: dict) -> str:
    lines = [
        "# Danny Static Site Audit",
        "",
        f"- Project: `{report['project_dir']}`",
        f"- Status: `{report['status'].upper()}`",
        "",
    ]

    if report["missing_files"]:
        lines.append("## Missing Files")
        lines.append("")
        for name in report["missing_files"]:
            lines.append(f"- `{name}`")
        lines.append("")

    lines.append("## Metrics")
    lines.append("")
    for key, value in report["metrics"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")

    lines.append("## Quality Issues")
    lines.append("")
    if report["quality_issues"]:
        for issue in report["quality_issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Guidance")
    lines.append("")
    if report["status"] == "pass":
        lines.append("- The site clears Danny's minimum bar.")
    else:
        lines.append("- Add more visible structure, richer interactions, and substantive UI logic before accepting the build.")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a static site for Danny's quality bar.")
    parser.add_argument("project_dir", help="Project directory to audit")
    parser.add_argument("-o", "--output", help="Write markdown report to this path")
    parser.add_argument("--json-out", help="Write JSON report to this path")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    report = audit(project_dir)
    markdown = to_markdown(report)

    if args.output:
        Path(args.output).write_text(markdown, encoding="utf-8")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(markdown)
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
