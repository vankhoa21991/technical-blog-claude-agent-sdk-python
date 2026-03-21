import asyncio
import sys
from pathlib import Path

# Add the demo directory to the path so we can import tools
sys.path.append(str(Path(__file__).parent.parent))

from tools.calculator import calculate_tool

async def test_calculate_addition():
    # The @tool decorator returns an SdkMcpTool object that wraps our function
    tool_instance = calculate_tool
    result = await tool_instance.handler({"a": 5, "b": 3, "operation": "add"})
    assert result["content"][0]["text"] == "8"

async def test_calculate_division_by_zero():
    # The @tool decorator returns an SdkMcpTool object that wraps our function
    tool_instance = calculate_tool
    result = await tool_instance.handler({"a": 10, "b": 0, "operation": "divide"})
    assert "Error" in result["content"][0]["text"]

async def run_tests():
    print("Running calculator tool tests...")

    try:
        await test_calculate_addition()
        print("✓ Addition test passed")
    except Exception as e:
        print(f"✗ Addition test failed: {e}")

    try:
        await test_calculate_division_by_zero()
        print("✓ Division by zero test passed")
    except Exception as e:
        print(f"✗ Division by zero test failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())