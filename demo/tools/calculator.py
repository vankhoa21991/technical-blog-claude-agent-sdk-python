from claude_agent_sdk import tool

@tool(
    name="calculate",
    description="Perform basic arithmetic operations",
    input_schema={
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
            "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}
        },
        "required": ["a", "b", "operation"]
    }
)
async def calculate_tool(input_data):
    try:
        a = input_data["a"]
        b = input_data["b"]
        operation = input_data["operation"]

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"content": [{"type": "text", "text": "Error: Division by zero"}]}
            result = a / b
        else:
            return {"content": [{"type": "text", "text": f"Error: Unknown operation {operation}"}]}

        return {"content": [{"type": "text", "text": str(result)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}