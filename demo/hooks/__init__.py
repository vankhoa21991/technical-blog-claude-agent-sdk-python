"""
Pattern 2: Hooks for Control

This package demonstrates how to use hooks to intercept and control
agent behavior before and after tool execution.

Available Hooks:
- block_dangerous_commands: Blocks dangerous bash commands
- log_tool_use: Logs all tool invocations for auditing
"""
from .command_blocker import block_dangerous_commands
from .audit_logger import log_tool_use

__all__ = ["block_dangerous_commands", "log_tool_use"]
