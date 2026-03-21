# Pattern modules for the progressive demo
from importlib import import_module
from pathlib import Path
import sys

# Ensure current directory is in path for imports
patterns_dir = Path(__file__).parent
if str(patterns_dir) not in sys.path:
    sys.path.insert(0, str(patterns_dir))

# Import pattern modules
pattern_01_basic_tools = import_module("01_basic_tools")
pattern_02_with_hooks = import_module("02_with_hooks")
pattern_03_with_permissions = import_module("03_with_permissions")

__all__ = [
    "pattern_01_basic_tools",
    "pattern_02_with_hooks",
    "pattern_03_with_permissions",
]
