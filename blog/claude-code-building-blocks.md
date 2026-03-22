# How I Built an Interactive Demo for Claude Agent SDK Python

A few months ago, I was trying to learn Claude Agent SDK Python. The documentation was good. I'll give them that. But I kept finding myself wishing I could just **see the code running**.

You know what I mean?

You read about tools and hooks and sessions, and it all makes sense on paper. Then you sit down to actually use it and... nothing. The concepts don't click. The examples feel disconnected from reality.

So I did what any developer would do. I built an interactive demo.

Not a slide deck. Not a tutorial. Actual code you can run and watch work. And I want to walk you through how I built it, pattern by pattern, because that's how I learned it myself.

---

## The Problem: Learning SDKs from Documentation Sucks

Here's the thing about learning a new SDK.

**Reading the docs:**
> "The `@tool` decorator registers a function as a tool that Claude can invoke..."

**Me:**
> Okay, but what does that actually look like? How do I use it? What happens when it goes wrong?

I needed something I could **play with**. Something where I could try:
- "What if I make a tool that does X?"
- "What happens if I block this dangerous operation?"
- "How do I continue a conversation across multiple turns?"

So I built a progressive demo that starts simple and adds complexity one pattern at a time. Let me show you what I built and why.

---

## Pattern 1: Starting Simple - Custom Tools

The first thing I wanted to understand was **tools**. How do you give Claude new capabilities?

I started with something dead simple: a calculator.

```python
from claude_agent_sdk import tool

@tool
def calculator(operation: str, a: float, b: float) -> str:
    """Perform arithmetic operations."""
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }

    if operation not in operations:
        return f"Unknown operation: {operation}"

    result = operations[operation](a, b)
    return f"{a} {operation} {b} = {result}"
```

**What happened when I ran this:**

```bash
$ python -m patterns.01_basic_tools

User: What is 15 times 7?

[Tool Use] calculator(operation='multiply', a=15, b=7)
Tool Result: 15 * 7 = 105

Claude: The result of 15 times 7 is 105.
```

**The moment it clicked:**

I saw Claude actually **using my tool**. Not just calculating itself, but invoking the function I wrote, getting the result, and presenting it naturally.

That's when I got it—tools are just Python functions that Claude can call. The `@tool` decorator is just saying "hey Claude, this is something you can use."

**What I learned:**
- Tools extend Claude's capabilities
- The decorator handles all the registration magic
- Claude figures out when to use them
- You write normal Python, Claude handles the integration

---

## Pattern 2: Adding Safety - Hooks

Once I had tools working, I started thinking: *what if someone asks Claude to do something dangerous?* Like run `rm -rf /` or something?

I needed a way to intercept tool calls and block the bad ones. Enter **hooks**.

```python
from claude_agent_sdk import PreToolUseHook, HookResult

class CommandBlockerHook(PreToolUseHook):
    """Block dangerous tools from executing."""

    BLOCKED_TOOLS = {
        "run_shell_command",
        "write_file",
        "delete_file",
        "network_request"
    }

    async def before_tool_use(self, tool_name: str, input_data: dict) -> HookResult:
        if tool_name in self.BLOCKED_TOOLS:
            print(f"[CommandBlocker] BLOCKED {tool_name}: Too dangerous!")
            return HookResult(
                action="block",
                reason=f"Tool {tool_name} is blocked for security reasons"
            )

        return HookResult(action="allow")
```

**What happened when I ran this:**

```bash
$ python -m patterns.02_with_hooks

User: Run: rm -rf /

[CommandBlocker] BLOCKED run_shell_command: Too dangerous!

Claude: I cannot execute that command as it's been blocked.
```

**The moment it clicked:**

Hooks are like middleware for tool calls. They run **before** the tool executes (PreToolUseHook) or **after** (PostToolUseHook). You can block them, modify inputs, log them, whatever you need.

I also built an `AuditLoggerHook` that logs every tool call to a file for compliance. Because in production, you need to know what your agents are doing.

**What I learned:**
- Hooks intercept tool calls before/after execution
- You can block dangerous operations
- You can log everything for audit trails
- Multiple hooks can run in sequence

---

## Pattern 3: Control Access - Permissions

Now I had tools and hooks working. But what if I want to give different agents different capabilities? Like a read-only agent vs. a read-write agent?

That's where **permissions** come in.

```python
from claude_agent_sdk import Agent, PermissionMode

# Define what each tier can do
SAFE_TOOLS = ["calculator", "text_analyzer"]
SEMI_TRUSTED_TOOLS = SAFE_TOOLS + ["read_file"]
RISKY_TOOLS = SEMI_TRUSTED_TOOLS + ["write_file", "run_shell_command"]

# Create agent with limited permissions
agent = Agent(
    allowed_tools=SAFE_TOOLS,
    permission_mode=PermissionMode.STRICT
)
```

**What happened when I ran this:**

```bash
$ python -m patterns.03_with_permissions

Permission Level: SAFE

User: Read /etc/passwd

Claude: I don't have access to file reading tools at my current
permission level. I can only use calculator and text_analyzer.
```

**The moment it clicked:**

The `allowed_tools` list is a whitelist. Claude respects boundaries—it won't even try to use tools that aren't on the list. And `PermissionMode.STRICT` enforces this. In `PERMISSIVE` mode, Claude can try any tool (great for exploration, scary for production).

I built a tiered system:
- **SAFE** - Calculator, text analysis
- **SEMI_TRUSTED** - Plus file reading
- **RISKY** - Plus file writing, shell commands

**What I learned:**
- `allowed_tools` creates a whitelist
- `permission_mode` controls strictness
- You can upgrade/downgrade permissions dynamically
- Claude respects boundaries automatically

---

## Pattern 4: Putting It All Together - Complete Agent

At this point, I understood tools, hooks, and permissions separately. But how do they work **together**?

I needed to see the full picture.

```python
from claude_agent_sdk import Agent, PermissionMode
from tools.calculator import calculator
from hooks.command_blocker import CommandBlockerHook
from hooks.audit_logger import AuditLoggerHook

agent = Agent(
    tools=[calculator],
    hooks=[CommandBlockerHook(), AuditLoggerHook()],
    allowed_tools=["calculator"],
    permission_mode=PermissionMode.STRICT
)
```

**What happened when I ran this:**

```bash
$ python -m patterns.04_complete_agent

User: Calculate 123 * 456

[CommandBlocker] Checking tool: calculator
[CommandBlocker] Status: ALLOWED
[AuditLogger] Tool use: calculator
[AuditLogger] Result: Success

Claude: The result of 123 * 456 is 56,088.
```

**The moment it clicked:**

All three patterns work together seamlessly:
- **Tools** extend capabilities (calculator)
- **Hooks** provide safety and logging (blocker + logger)
- **Permissions** control access (only calculator allowed)

This is a **production-ready agent**. It has custom capabilities, security boundaries, and audit logging. Everything you need for real-world use.

**What I learned:**
- Tools, hooks, and permissions complement each other
- They layer without conflicts
- This is how you build production agents
- Security and observability are built-in

---

## Pattern 5: The Advanced Stuff - Sessions

This is where things got interesting.

By now I had tools, hooks, and permissions working. But something was missing. Every conversation with Claude started from scratch. No memory. No context. Just one-off queries that forgot everything as soon as they finished.

I wanted to build something different. An agent that could:
- Remember what we talked about
- Ask me questions and actually use my answers
- Explore different angles without losing the original thread

Basically, I wanted a conversation, not a query.

Enter **sessions**.

So here's what I built: a research agent that compares three AI frameworks in four phases.

**Phase 1: Initial Research**

The agent starts with a quick web search. It looks up basic information about three AI agent frameworks: LangGraph, AutoGen, and Claude Agent SDK. For each one, it gathers the essentials—what it is, what it's used for, and key features. Just the basics, nothing overwhelming. This all happens in one session with a unique ID.

**Phase 2: Get Your Direction**

Once the initial research is done, the demo pauses and asks you what to focus on next. You can choose: architecture patterns, real-world use cases, learning curve, performance benchmarks, or a custom topic. This is a manual pause—you tell the agent where to go deeper.

**Phase 3: Refined Analysis**

Now here's the key: the agent continues with the SAME session ID from Phase 1. It remembers everything it just researched. When you say "focus on architecture," it doesn't start from scratch—it builds on the existing report and dives deeper into that specific aspect. The context is preserved.

**Phase 4: Explore Alternatives (Optional)**

Finally, you can choose to explore a completely different angle—like comparing community ecosystems or learning curves. The demo creates a NEW session ID for this, so it's a fresh conversation. But the original research session stays intact, untouched. You can explore tangents without losing your main thread.

That's the pattern: research → feedback → deepen → (optionally) explore alternatives. All powered by session IDs.

```python
from claude_agent_sdk import ClaudeSDKClient
import uuid

async def research_agent():
    """Multi-turn research agent with sessions."""

    # Initialize and connect
    client = ClaudeSDKClient()
    await client.connect()

    # Create a unique session ID
    session_id = f"research-{uuid.uuid4().hex[:8]}"

    # Phase 1: Initial research
    await client.query(
        prompt="Compare LangGraph, AutoGen, and Claude Agent SDK",
        session_id=session_id
    )

    # Receive the response stream
    async for message in client.receive_messages():
        print(message.content, end='', flush=True)

    # Phase 2: Get human direction
    direction = input("\nFocus deeper on [architecture/use cases]? ")

    # Phase 3: Continue same session (context preserved!)
    await client.query(
        prompt=f"Deepen analysis on {direction}",
        session_id=session_id  # Same ID = same conversation
    )

    async for message in client.receive_messages():
        print(message.content, end='', flush=True)

    # Phase 4: Fork to explore alternative
    fork_session_id = f"{session_id}-fork"

    await client.query(
        prompt="Compare learning curves instead",
        session_id=fork_session_id  # New ID = fresh conversation
    )

    async for message in client.receive_messages():
        print(message.content, end='', flush=True)

    await client.disconnect()
```

**What happened when I ran this:**

```bash
$ python -m patterns.05_deep_research

Connecting to Claude Code...
✓ Connected

📝 Session ID: research-a3f2b1c9

==================== PHASE 1: Initial Research ====================

# Literature Review: LangGraph vs AutoGen vs Claude Agent SDK

## Overview
Comparing three leading frameworks for building AI agents...

## LangGraph
**Architecture:** Graph-based orchestration...
[Full research output]

✓ Phase 1 complete. Session ID: research-a3f2b1c9

==================== PHASE 2: User Feedback ====================

Focus deeper on [architecture/use cases/learning curve]? architecture

==================== PHASE 3: Refined Analysis ====================

# Deep Dive: Architectural Comparison

## LangGraph Architecture
[Detailed architectural analysis]

✓ Phase 3 complete. Session updated with refined analysis.

==================== PHASE 4: Optional Fork ====================

Explore alternative direction? [y/N]: y

🔀 Creating forked session...
Original session: research-a3f2b1c9
Fork session: research-a3f2b1c9-fork

[Learning curve comparison output]

✓ Phase 4 complete. Forked session created.
```

**The moment it clicked:**

This is **multi-turn reasoning**. The agent:
1. Researches initially (Phase 1)
2. Gets my feedback (Phase 2)
3. **Continues the same session** with all context preserved (Phase 3)
4. Creates a **new session** to explore alternatives without changing the original (Phase 4)

The key insight: **Session IDs are conversation handles**. Same ID = same conversation. Different ID = fresh start.

**What I learned:**
- **ClaudeSDKClient** requires `connect()` before use
- **session_id** is just a string - you manage it yourself
- Pass the same `session_id` to continue conversations
- Use a different `session_id` to start fresh
- **receive_messages()** streams the response in real-time

---

## Session Management Best Practices

After working with sessions, here's what I'd do differently:

**Session IDs:**
- Use meaningful prefixes: `research-`, `chat-`, `analysis-`
- Add UUID or timestamp for uniqueness: `session-20250321-a3f2b1c9`
- Store session IDs in a database if you need to resume later
- Use environment variables for session IDs in long-running processes

**Error Handling:**
```python
try:
    await client.query(prompt, session_id=session_id)
    async for message in client.receive_messages():
        print(message.content)
except Exception as e:
    print(f"Session error: {e}")
    await client.disconnect()
```

**Cleanup:**
Always call `await client.disconnect()` when done to free resources.

---

## How You Can Use This Demo

Here's how to run it yourself:

```bash
# Clone the repo
git clone [repo-url]
cd claude-agent-sdk-python-demo/demo

# Set up Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run interactive menu
python main.py

# Or run individual patterns
python -m patterns.01_basic_tools
python -m patterns.02_with_hooks
python -m patterns.03_with_permissions
python -m patterns.04_complete_agent
python -m patterns.05_deep_research
```

**What you'll experience:**
- Pattern 1: See Claude use your calculator tool
- Pattern 2: Watch dangerous commands get blocked
- Pattern 3: Test permission boundaries
- Pattern 4: All patterns working together
- Pattern 5: Multi-turn research with sessions

---

## What I Learned Building This

**Tool patterns:**
- Tools are just Python functions with `@tool`
- Claude figures out when to use them
- Error handling in tools matters

**Hook patterns:**
- PreToolUseHook for blocking/modifying
- PostToolUseHook for logging/response
- Hooks compose (run in sequence)

**Permission patterns:**
- Whitelists with `allowed_tools`
- STRICT vs PERMISSIVE modes
- Tiered access levels

**Session patterns:**
- Session IDs are just strings—you manage them yourself
- Same session ID = same conversation (context preserved)
- Different session ID = fresh conversation
- Use descriptive names like `research-20250321` for clarity

**Production patterns:**
- Always call `await client.connect()` before querying
- Store session IDs in a database for long-running conversations
- Wrap sessions in try/except/finally for error handling
- Call `await client.disconnect()` to clean up resources
- Use unique session IDs to avoid conflicts between users

---

## Common Mistakes I Made (So You Don't Have To)

**Mistake 1: Forgetting to call connect()**

The client won't work if you don't call `await client.connect()` first. I got a "Not connected" error the first time. Always connect before querying, and disconnect when you're done to free up resources.

**Mistake 2: Using the wrong session ID**

If you pass a different session ID by accident, you'll start a fresh conversation instead of continuing the existing one. I lost context several times by mistyping the session ID. Use clear, consistent naming and store session IDs in variables so you don't have to retype them.

**Mistake 3: Not receiving messages**

`client.query()` only sends the prompt—it doesn't return the response. You need to call `client.receive_messages()` in an async loop to actually get Claude's output. I sat wondering why nothing was happening until I realized I wasn't receiving the messages.

**Mistake 4: Not handling disconnection**

If your script crashes or gets interrupted, the connection might stay open. Always wrap your session in a try/except block and call `await client.disconnect()` in a finally block to ensure clean cleanup.

---

## The Project Structure

Here's how I organized everything:

```
demo/
├── main.py                 # Interactive menu launcher
├── CLAUDE.md              # Project context
├── requirements.txt        # Dependencies
├── patterns/              # 5 progressive patterns
│   ├── 01_basic_tools.py
│   ├── 02_with_hooks.py
│   ├── 03_with_permissions.py
│   ├── 04_complete_agent.py
│   └── 05_deep_research.py
├── tools/                 # Custom tools
│   └── calculator.py
├── hooks/                 # Hook implementations
│   ├── command_blocker.py
│   └── audit_logger.py
├── tests/                 # Tests
└── .claude/
    └── skills/             # Domain expertise
        ├── research/
        ├── documentation/
        └── analysis/
```

**Why this structure:**
- **patterns/** - Each pattern is self-contained, can run independently
- **tools/** - Reusable custom tools
- **hooks/** - Reusable hook implementations
- **tests/** - Ensures everything works
- **.claude/skills/** - Domain expertise in markdown

---

## What You Can Do With This

**Learn the patterns:**
- Run each pattern and see what happens
- Read the code to understand implementation
- Modify tools and hooks for your use case

**Build your own agents:**
- Start with Pattern 1 (add custom tools)
- Add Pattern 2 (hooks for safety)
- Add Pattern 3 (permissions)
- Combine everything with Pattern 4
- Go advanced with Pattern 5 (sessions)

**Extend the demo:**
- Add your own tools (database, API calls, file processing)
- Add your own hooks (rate limiting, custom logging)
- Add your own skills (your domain expertise)
- Experiment with session operations

---

## Key Takeaways

**The five patterns in order:**

| Pattern | What It Does | When to Use It |
|---------|-------------|---------------|
| **Custom Tools** | Extend Claude with Python functions | Need new capabilities |
| **Hooks** | Intercept and control behavior | Need safety, logging, validation |
| **Permissions** | Control what tools Claude can use | Need tiered access control |
| **Complete Agent** | All patterns combined | Building production agents |
| **Sessions** | Multi-turn reasoning with context | Complex, multi-step tasks |

**Core concepts:**
- **ClaudeSDKClient** - Main client for agent interactions
- **session_id** - String identifier for conversations
- **query()** - Send prompts to Claude
- **receive_messages()** - Stream Claude's responses
- **connect/disconnect** - Manage connection lifecycle

**Production mindset:**
- Always call `await client.connect()` before querying
- Store session IDs for long-running conversations
- Use unique session IDs to avoid conflicts
- Call `await client.disconnect()` to clean up
- Wrap sessions in try/except for error handling

---

## What's Next?

**For you:**

1. **Clone the demo** and run it yourself
2. **Modify the tools** - add your own capabilities
3. **Add your own hooks** - implement custom validation
4. **Build your own agent** - combine all patterns
5. **Deploy to production** - add monitoring, error handling

**Resources:**
- **SDK Docs:** https://docs.anthropic.com/claude-agent-sdk
- **GitHub:** [repo link]
- **Community:** discord.gg/anthropic

---

## Final Thoughts

Building this demo taught me more about the Claude Agent SDK than reading documentation ever could. There's something about **seeing it work** that makes concepts click.

I hope this demo helps you learn SDK patterns the same way it helped me. Start with Pattern 1, run the code, see what happens. Then add Pattern 2, then 3, then 4, then 5.

By the end, you'll have built intuition for how tools, hooks, permissions, and sessions work together. And you'll be ready to build your own production agents.

**Go build something cool.** 🚀
