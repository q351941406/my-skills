#!/usr/bin/env python3
"""Check Style - 检查 Python 代码风格问题的脚本"""

import json
import sys


def check_style(code: str) -> dict:
    """检查代码常见风格问题"""
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        # 检查行长度
        if len(line) > 100:
            issues.append({
                "line": i,
                "severity": "Warning",
                "issue": f"Line exceeds 100 characters ({len(line)})",
            })

        # 检查尾部空白
        if line.rstrip() != line and line.strip():
            issues.append({
                "line": i,
                "severity": "Info",
                "issue": "Trailing whitespace",
            })

        # 检查 tab 缩进
        if line.startswith("\t"):
            issues.append({
                "line": i,
                "severity": "Warning",
                "issue": "Tab indentation (use 4 spaces)",
            })

        # 检查 == None (应使用 is None)
        if "== None" in line or "!= None" in line:
            issues.append({
                "line": i,
                "severity": "Warning",
                "issue": "Use 'is None' or 'is not None' instead of '== None'",
            })

        # 检查裸 except
        if line.strip().startswith("except:"):
            issues.append({
                "line": i,
                "severity": "Warning",
                "issue": "Bare except clause (specify exception type)",
            })

    return {
        "total_issues": len(issues),
        "critical": len([i for i in issues if i["severity"] == "Critical"]),
        "warnings": len([i for i in issues if i["severity"] == "Warning"]),
        "info": len([i for i in issues if i["severity"] == "Info"]),
        "issues": issues,
        "passed": len([i for i in issues if i["severity"] == "Critical"]) == 0,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = sys.stdin.read()

    result = check_style(code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
