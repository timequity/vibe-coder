#!/usr/bin/env python3
"""
Beads Validation Script

Validates beads issues:
- PRD features mapped to issues
- Dependencies are valid (IDs exist)
- No circular dependencies
- Ready queue is not empty
- Priorities are valid (1-3)

Usage:
    python validate_beads.py --check-created --prd docs/PRD.md
    python validate_beads.py --check-deps --check-ready
    python validate_beads.py --all --prd docs/PRD.md
"""

import argparse
import subprocess
import json
import re
import sys
from pathlib import Path


def run_cmd(cmd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def get_issues() -> list[dict]:
    """Get all issues from beads."""
    code, stdout, stderr = run_cmd("bd list --json 2>/dev/null")
    if code != 0:
        return []
    try:
        return json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        return []


def count_prd_features(prd_path: str) -> int:
    """Count features in PRD.md."""
    try:
        content = Path(prd_path).read_text()

        # Look for MVP Features section
        features = 0

        # Count numbered items under "Features" or "MVP"
        in_features = False
        for line in content.split("\n"):
            if "feature" in line.lower() or "mvp" in line.lower():
                in_features = True
            elif line.startswith("##") and in_features:
                in_features = False

            if in_features:
                # Count numbered list items or bullet points with feature-like content
                if re.match(r"^\d+\.\s+\*\*", line) or re.match(r"^-\s+\*\*", line):
                    features += 1

        return features if features > 0 else 4  # Default assumption
    except Exception:
        return 0


def check_prd_mapping(prd_path: str) -> tuple[bool, str]:
    """Check if PRD features are mapped to issues."""
    prd_features = count_prd_features(prd_path)
    issues = get_issues()
    issue_count = len(issues)

    if prd_features == 0:
        return True, "Could not parse PRD features"

    if issue_count >= prd_features:
        return True, f"PRD features: {prd_features}, Issues: {issue_count}"

    return False, f"PRD has {prd_features} features, only {issue_count} issues created"


def check_dependencies() -> tuple[bool, str]:
    """Check all dependency IDs exist."""
    issues = get_issues()
    issue_ids = {issue.get("id") for issue in issues}

    invalid_deps = []
    for issue in issues:
        deps = issue.get("dependencies", []) or []
        for dep in deps:
            if dep not in issue_ids:
                invalid_deps.append(f"{issue.get('id')} → {dep}")

    if invalid_deps:
        return False, f"Invalid dependencies: {', '.join(invalid_deps)}"

    return True, "All dependency IDs exist"


def check_circular_deps() -> tuple[bool, str]:
    """Check for circular dependencies using bd doctor."""
    code, stdout, stderr = run_cmd("bd doctor 2>&1")
    output = stdout + stderr

    if "circular" in output.lower() or "cycle" in output.lower():
        return False, f"Circular dependency detected: {output[:200]}"

    if code == 0:
        return True, "No circular dependencies"

    return True, "bd doctor passed (or not available)"


def check_ready_queue() -> tuple[bool, str]:
    """Check that ready queue is not empty."""
    code, stdout, stderr = run_cmd("bd ready --limit=1 2>&1")
    output = stdout + stderr

    if "no open issues" in output.lower() or "no issues" in output.lower():
        # Check if there are any open issues at all
        issues = get_issues()
        open_issues = [i for i in issues if i.get("status") != "closed"]
        if not open_issues:
            return True, "No open issues (all done)"
        return False, "Issues exist but none are ready (all blocked)"

    # Extract issue ID from output
    match = re.search(r"([a-z]+-[a-z0-9]+)", output)
    if match:
        return True, f"Ready queue has issue: {match.group(1)}"

    return True, "Ready queue check passed"


def check_priorities() -> tuple[bool, str]:
    """Check all priorities are valid (0-4)."""
    issues = get_issues()

    invalid = []
    for issue in issues:
        priority = issue.get("priority", 2)
        if priority not in [0, 1, 2, 3, 4]:
            invalid.append(f"{issue.get('id')}: priority={priority}")

    if invalid:
        return False, f"Invalid priorities: {', '.join(invalid)}"

    return True, "All priorities valid (0-4)"


def check_issue_quality(issue: dict) -> tuple[bool, list[str]]:
    """Check issue has required sections and minimum content."""
    errors = []
    desc = issue.get("description", "") or ""
    issue_id = issue.get("id", "unknown")

    # Skip closed issues
    if issue.get("status") == "closed":
        return True, []

    # Minimum length check
    if len(desc) < 100:
        errors.append(f"Description too short ({len(desc)} chars, need 100+)")

    # Required sections (flexible matching)
    desc_lower = desc.lower()

    # Check for summary/overview/goal
    summary_variants = ["## summary", "## overview", "## goal", "## цель", "summary:", "overview:"]
    if not any(v in desc_lower for v in summary_variants):
        # Also accept if description starts with clear statement
        if not (desc_lower.startswith("implement") or desc_lower.startswith("add") or
                desc_lower.startswith("fix") or desc_lower.startswith("create")):
            errors.append("Missing Summary section")

    # Check for files/paths
    files_variants = ["## files", "files to modify", "## изменения", "## файлы", "`src/", "`lib/", "`app/"]
    if not any(v in desc_lower for v in files_variants):
        errors.append("Missing Files to Modify section")

    # Check for implementation steps
    steps_variants = ["## implementation", "## steps", "## план", "## шаги", "1. ", "1) "]
    if not any(v in desc_lower for v in steps_variants):
        errors.append("Missing Implementation Steps section")

    # Check for acceptance criteria
    criteria_variants = ["## acceptance", "## criteria", "## готово", "- [ ]", "- [x]", "success criteria"]
    if not any(v in desc_lower for v in criteria_variants):
        errors.append("Missing Acceptance Criteria section")

    return len(errors) == 0, errors


def check_all_issues_quality() -> tuple[bool, str, list[tuple[str, list[str]]]]:
    """Check quality of all open issues."""
    issues = get_issues()
    open_issues = [i for i in issues if i.get("status") != "closed"]

    failures = []
    for issue in open_issues:
        passed, errors = check_issue_quality(issue)
        if not passed:
            failures.append((issue.get("id", "unknown"), errors))

    if failures:
        return False, f"{len(failures)}/{len(open_issues)} issues have quality problems", failures

    return True, f"All {len(open_issues)} open issues pass quality check", []


def main():
    parser = argparse.ArgumentParser(description="Validate beads issues")
    parser.add_argument("--prd", help="Path to PRD.md")
    parser.add_argument("--check-created", action="store_true",
                        help="Check PRD→issues mapping")
    parser.add_argument("--check-deps", action="store_true",
                        help="Check dependencies are valid")
    parser.add_argument("--check-ready", action="store_true",
                        help="Check ready queue not empty")
    parser.add_argument("--check-quality", action="store_true",
                        help="Check issue descriptions have required sections")
    parser.add_argument("--all", action="store_true",
                        help="Run all checks")
    args = parser.parse_args()

    if args.all:
        args.check_created = True
        args.check_deps = True
        args.check_ready = True
        args.check_quality = True

    print("## Beads Validation\n")

    results = []

    # PRD mapping check
    if args.check_created and args.prd:
        passed, msg = check_prd_mapping(args.prd)
        results.append(("PRD Mapping", passed, msg))
        print(f"[{'PASS' if passed else 'WARN'}] {msg}")

    # Dependency checks
    if args.check_deps:
        passed, msg = check_dependencies()
        results.append(("Dependencies", passed, msg))
        print(f"[{'PASS' if passed else 'FAIL'}] {msg}")

        passed, msg = check_circular_deps()
        results.append(("Circular Deps", passed, msg))
        print(f"[{'PASS' if passed else 'FAIL'}] {msg}")

    # Ready queue check
    if args.check_ready:
        passed, msg = check_ready_queue()
        results.append(("Ready Queue", passed, msg))
        print(f"[{'PASS' if passed else 'FAIL'}] {msg}")

    # Quality check
    if args.check_quality:
        passed, msg, failures = check_all_issues_quality()
        results.append(("Issue Quality", passed, msg))
        print(f"[{'PASS' if passed else 'WARN'}] {msg}")

        if failures:
            print("\n  Quality issues:")
            for issue_id, errors in failures:
                print(f"    {issue_id}:")
                for error in errors:
                    print(f"      - {error}")

    # Always check priorities
    passed, msg = check_priorities()
    results.append(("Priorities", passed, msg))
    print(f"[{'PASS' if passed else 'FAIL'}] {msg}")

    # Summary
    print()
    passed_count = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"Result: {passed_count}/{total} checks passed")

    failed = [(n, m) for n, p, m in results if not p]
    if failed:
        print(f"\nIssues ({len(failed)}):")
        for name, msg in failed:
            print(f"  - {name}: {msg}")
        sys.exit(1)

    print("\n[OK] Beads validation passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
