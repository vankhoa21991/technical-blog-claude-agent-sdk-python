"""
Audit Logger Hook - Pattern 2

This hook logs all tool invocations to both console and file.
Useful for debugging, auditing, and monitoring agent behavior.

Hook Type: PreToolUse
Target: All tools
"""
import json
from datetime import datetime
from pathlib import Path


async def log_tool_use(input_data, tool_use_id, context):
    """
    Log all tool invocations to console and file.

    Args:
        input_data: Dict containing tool_name and tool_input
        tool_use_id: Unique identifier for this tool use
        context: Additional context (not used in this hook)

    Returns:
        Empty dict (no interception, just logging)
    """
    tool_name = input_data.get("tool_name")
    tool_input = input_data.get("tool_input", {})

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "input": tool_input,
        "tool_use_id": tool_use_id
    }

    # Console log (with visual marker)
    print(f"[AUDIT] {json.dumps(log_entry)}")

    # File log (append to audit.log in demo directory)
    # Get the demo directory (parent of hooks directory)
    demo_dir = Path(__file__).parent.parent
    audit_log_path = demo_dir / "audit.log"

    with open(audit_log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Return empty dict for no-op (don't intercept)
    return {}
