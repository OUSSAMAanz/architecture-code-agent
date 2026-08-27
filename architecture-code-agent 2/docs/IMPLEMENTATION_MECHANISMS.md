# Implementation Mechanisms Studied

This document records the research part of the assignment and explains which
mechanisms were implemented in the educational agent.

## Sources

1. [Anthropic Claude Code](https://github.com/anthropics/claude-code) — a
   teacher-provided research reference. It is not installed or used at runtime.
2. [How Claude Code Works](https://github.com/Windy3f3f3f3f3f/how-claude-code-works)
   — independent educational analysis covering the main loop, tools, context,
   permissions, editing, and validation.
3. [Claw Code](https://github.com/ultraworkers/claw-code) — open-source agent
   harness reference. Its current README describes it as an agent-managed exhibit,
   so this project uses it as research material rather than a direct dependency.
4. [Official OpenAI function-calling guide](https://developers.openai.com/api/docs/guides/function-calling)
   — Responses API model/tool/result protocol used by the live provider.
5. [Official GPT-5.3-Codex model page](https://developers.openai.com/api/docs/models/gpt-5.3-codex)
   — Codex model capabilities and Responses API support.

## Mechanism-to-code mapping

| Mechanism | Educational implementation | Location |
| --- | --- | --- |
| Agent loop | Repeated model response, tool execution, tool-result reinjection | `code_agent/agent.py` |
| Context construction | System rules plus structured architecture JSON | `code_agent/prompts.py` |
| Tool registry | Provider-neutral JSON Schema definitions | `code_agent/tools.py` |
| Unified tool execution | One dispatcher for all model-requested actions | `SafeWorkspace.execute` |
| Provider isolation | Common response types around live and offline providers | `code_agent/providers.py` |
| Codex protocol | Responses output items plus `function_call_output` reinjection | `OpenAIProvider.respond` |
| Permission boundary | Resolved-path containment and sensitive-path denial | `SafeWorkspace._resolve` |
| Restricted execution | Fixed test commands; no arbitrary shell tool | `SafeWorkspace.run_tests` |
| Failure containment | Tool errors are returned to the model instead of crashing the loop | `CodeAgent.run` |
| Bounded autonomy | Configurable maximum iteration count | `CodeAgent.max_iterations` |
| Verification | Test tool plus deterministic final artifact checks | `code_agent/validator.py` |
| Observability | JSONL event transcript and result file | generated `.agent/` directory |

## Simplified agent loop

```text
messages = [structured user request]

repeat up to max_iterations:
    response = model(messages, tool_schemas)
    append response to messages

    for each requested tool:
        validate tool name and arguments
        execute inside the workspace boundary
        append result or safe error to messages

    if finish was requested:
        run deterministic repository validation
        return success only if validation passes
```

## Context engineering

The original Markdown inputs are useful to humans but contain long prose, code
blocks, tables, and multiple PlantUML diagrams. The parser extracts a predictable
JSON representation before the model is called. This improves repeatability and
makes the agent's exact input inspectable in `.agent/architecture.json`.

The documents remain untrusted data. They are wrapped inside an explicit
`<architecture_specification>` section and the system prompt states that their
content cannot override the agent's security rules.

The live provider uses stateless Responses API calls (`store=False`) and requests
encrypted reasoning content so reasoning items can be safely carried into the next
tool-result turn without relying on server-side response storage.

## Tools and permissions

The live model can request only five tools. General shell access was excluded
because it would add disproportionate command-injection risk. File paths are
resolved before use and must remain descendants of the chosen workspace. Existing
symlinks are resolved as part of the same check.

Test execution is deliberately narrow:

- Node repositories run `node --test` directly; model-generated npm scripts are not trusted.
- Python repositories run `python -m unittest discover`.
- Every test subprocess has a timeout.

For a production agent, these controls should be supplemented by an isolated
container, resource limits, command parsing, user approvals, and network policy.

## Verification and stopping

There are three separate safeguards against false completion:

1. The model is instructed to run tests before finishing.
2. The test tool returns its actual process exit code and output.
3. After `finish`, deterministic validation checks the output structure.

The loop also stops after a fixed number of iterations. This controls API cost and
prevents an unsuccessful model from running indefinitely.

## Deliberate simplifications

This assignment implementation does not attempt to reproduce a production coding
agent's streaming UI, context compaction, hooks, multi-agent orchestration, MCP,
Git worktrees, semantic code indexing, or operating-system sandbox. Those are
valuable production features, but the implemented subset is sufficient to show
the fundamental architecture clearly in a small codebase.
