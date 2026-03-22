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

## Pattern 5: The Advanced Stuff - Sessions & Skills

This is where things got really interesting. I wanted to build an agent that could:
- Maintain context across multiple conversation turns
- Use domain expertise (skills)
- Accept human feedback
- Explore alternative directions

Enter **sessions and skills**.

```python
from claude_agent_sdk import ClaudeSDKClient, query, ClaudeAgentOptions

client = ClaudeSDKClient()

async def research_agent():
    """Multi-turn research agent with sessions."""

    # Phase 1: Initial research
    async for message in query(
        prompt="Compare LangGraph, AutoGen, and Claude Agent SDK",
        options=ClaudeAgentOptions(
            setting_sources=["project"],  # Loads CLAUDE.md and skills
            allowed_tools=["Skill", "Read", "Bash", "web_search"],
            effort="high"
        )
    ):
        print(message.content)

    session_id = client.get_most_recent_session_id()

    # Phase 2: Get human direction
    direction = input("\nFocus deeper on [architecture/use cases]? ")

    # Phase 3: Continue same session (context preserved!)
    async for message in query(
        prompt=f"Deepen analysis on {direction}",
        options=ClaudeAgentOptions(
            session_id=session_id,  # Continues session
            allowed_tools=["Skill", "Read", "web_search"]
        )
    ):
        print(message.content)
```

**What happened when I ran this:**

```bash
$ python -m patterns.05_deep_research

==================== PHASE 1: Initial Research ====================

[web_search] Searching for documentation...
[Skill] Loading research methodology...

Comparing frameworks:
- LangGraph: Graph-based orchestration...
- AutoGen: Multi-agent conversations...
- Claude Agent SDK: Tool-calling with agent loop...

Session ID: sess_abc123

==================== PHASE 2: User Feedback ====================

Focus deeper on [architecture/use cases]? architecture

==================== PHASE 3: Refined Analysis ====================

Building on previous research, diving into architecture...
[Detailed architectural comparison]

==================== PHASE 4: Optional Fork ====================

Explore alternative direction? [y/N]: y

🔀 Creating forked session...
[Comparing learning curves and documentation]

Forked session: sess_xyz789
```

**The moment it clicked:**

This is **multi-turn reasoning**. The agent:
1. Researches initially (Phase 1)
2. Gets my feedback (Phase 2)
3. **Continues the same session** with all context preserved (Phase 3)
4. Can fork to explore alternatives without losing the original (Phase 4)

The `setting_sources=["project"]` parameter is magic—it loads:
- **CLAUDE.md** - Project context
- **Skills** - Domain expertise (research methodology, documentation standards, etc.)

So the agent automatically knows how to research, how to document, how to analyze—without me prompting it every time.

**What I learned:**
- **ClaudeSDKClient** manages sessions automatically
- **session_id** lets you continue conversations
- **fork_from** explores alternatives safely
- **setting_sources** loads context and skills
- **effort** controls reasoning depth

---

## The Skills System - Domain Expertise

One thing that blew my mind: **skills**.

Skills are just markdown files in `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: research
description: Research methodology for deep analysis
---

# Research Methodology

## Phase 1: Information Gathering
- Search official documentation first
- Find comparison guides
- Identify key differentiators

## Phase 2: Analysis
- Compare architecture patterns
- Evaluate use cases
- Assess trade-offs
```

When you set `setting_sources=["project"]`, the agent loads these automatically. So when it needs to do research, it loads the research skill and follows the methodology—automatically.

**What this means:**
- No need to prompt the agent about methodology every time
- Consistent, repeatable processes
- Domain expertise encoded in markdown
- Easy to update and improve

---

## The CLAUDE.md File - Project Context

The demo also has a `CLAUDE.md` file that loads automatically:

```markdown
# Claude Agent SDK Python - Progressive Patterns Demo

This demo showcases progressive patterns:
1. Custom Tools
2. Hooks for Control
3. Permission Management
4. Advanced Sessions

## Quick Commands
python main.py  # Interactive menu
python -m patterns.05_deep_research  # Run Pattern 5
```

**What this provides:**
- Project context for all agents
- Usage instructions
- Architecture overview
- Quick reference

Every agent automatically loads this context when `setting_sources=["project"]` is set.

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
- `session_id` continues conversations
- `fork_from` explores alternatives
- `setting_sources` loads context

**Production patterns:**
- Always use `setting_sources=["project"]`
- Wrap tools in error handling
- Use hooks for security and logging
- Set appropriate `effort` levels

---

## Common Mistakes I Made (So You Don't Have To)

**Mistake 1: Forgetting web_search**

```python
# ❌ Agent can't search documentation
allowed_tools=["Skill", "Read", "Bash"]

# ✅ Agent can find current info
allowed_tools=["Skill", "Read", "Bash", "web_search"]
```

**Mistake 2: Wrong session_id**

```python
# ❌ Typo creates new session (context lost!)
session_id = "sess_abc12"

# ✅ Use SDK to get exact session ID
session_id = client.get_most_recent_session_id()
```

**Mistake 3: Not using setting_sources**

```python
# ❌ No project context or skills
options=ClaudeAgentOptions(allowed_tools=["Skill"])

# ✅ Loads CLAUDE.md and skills
options=ClaudeAgentOptions(
    setting_sources=["project"],
    allowed_tools=["Skill"]
)
```

**Mistake 4: Wrong effort level**

```python
# ❌ Default effort too shallow for research
options=ClaudeAgentOptions(setting_sources=["project"])

# ✅ Explicit high effort for deep research
options=ClaudeAgentOptions(
    setting_sources=["project"],
    effort="high"
)
```

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
| **Sessions & Skills** | Multi-turn reasoning with context | Complex, multi-step tasks |

**Core concepts:**
- **ClaudeSDKClient** - Automatic session management
- **Agent Loop** - Multi-turn reasoning without custom loops
- **setting_sources** - Load CLAUDE.md and skills
- **Session operations** - continue, fork, resume
- **Effort levels** - Control reasoning depth

**Production mindset:**
- Always use `setting_sources=["project"]` for context
- Wrap tools in error handling
- Use hooks for security and observability
- Set appropriate permissions for your use case
- Monitor costs with effort levels

---

## What's Next?

**For you:**

1. **Clone the demo** and run it yourself
2. **Modify the tools** - add your own capabilities
3. **Create custom skills** - encode your domain expertise
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
