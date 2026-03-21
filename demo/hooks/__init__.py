"""
Pattern 2: Hooks for Control

This package demonstrates how to use hooks to intercept and control
agent behavior before and after tool execution.

Available Hooks:
- pre_tool_use_hook (command_blocker): Blocks dangerous bash commands
- pre_tool_use_hook (audit_logger): Logs tool invocations before execution
- post_tool_use_hook (audit_logger): Logs tool results after execution

Note: The SDK expects hooks to be named pre_tool_use_hook and post_tool_use_hook
for proper integration. These hooks can be registered individually or combined.
"""
from .command_blocker import pre_tool_use_hook as command_blocker_pre_hook
from .audit_logger import pre_tool_use_hook as audit_logger_pre_hook
from .audit_logger import post_tool_use_hook as audit_logger_post_hook

__all__ = [
    "command_blocker_pre_hook",
    "audit_logger_pre_hook",
    "audit_logger_post_hook"
]
