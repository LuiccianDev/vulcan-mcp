---
trigger: always_on
description: pstack per-role model choices for Antigravity CLI (Gemini)
---
# pstack model configuration (Antigravity CLI)
# defaults: 2
# budget: large (xhigh)
feature, refactoring: gemini-4-hydrogen-high (invoke_subagent: inherit)
bug-fix: gemini-4-hydrogen-high (invoke_subagent: inherit)
perf-issue: gemini-4-hydrogen-high (invoke_subagent: pro)
hillclimb: gemini-4-hydrogen-xhigh (invoke_subagent: pro)
judgment and prose: gemini-4-hydrogen-high (invoke_subagent: inherit)
hardest tasks: gemini-4-hydrogen-xhigh (invoke_subagent: pro)
reflect tooling: gemini-3.8-flash-high (invoke_subagent: flash)
reflect judgment, divergent, synthesizer: gemini-4-hydrogen-high (invoke_subagent: pro)
arena runners: gemini-4-hydrogen-xhigh, gemini-4-hydrogen-high, gemini-3.8-flash-high
arena cross-judge pool: claude-opus-5-5-high, gemini-4-hydrogen-xhigh
swarm workers: gemini-3.8-flash-high
architect runners: gemini-4-hydrogen-xhigh, gemini-4-hydrogen-high, gemini-3.8-flash-high
interrogate reviewers: gemini-4-hydrogen-xhigh, gemini-3.8-flash-high
