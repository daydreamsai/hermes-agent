---
name: taskmarket-worker
description: Use when Hermes is sourcing, claiming, executing, and submitting paid tasks from Taskmarket or similar agent marketplaces. Treat the market as orchestration and payment, and route actual work to specialized domain skills.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Taskmarket, Marketplace, Paid-Tasks, Routing, Orchestration, Agent-Work]
    related_skills: [hermes-agent-spawning, codex, claude-code]
---

# Taskmarket Worker

Use this skill when Hermes is operating as a market-facing worker that gets paid for completing specialized tasks.

Core principle: **the market skill handles protocol and routing; domain skills handle the actual work.**

Do not turn every marketplace task into this skill. Keep this skill generic and use it to:

- fetch and follow current marketplace instructions
- inspect tasks and decide whether to accept them
- route accepted tasks to the best matching local skill
- enforce reliable execution and submission hygiene
- convert successful paid workflows into improved local skills

## When To Use

Use this skill when the user asks Hermes to:

- work from Taskmarket or another task marketplace
- claim, bid on, or submit paid tasks
- build an autonomous Hermes worker that earns from specialized tasks
- improve Hermes based on marketplace outcomes

Do not use this skill for ordinary coding, research, or design work outside a market context.

## Skill Split

Keep responsibilities separate:

- `taskmarket-worker`: market protocol, setup, claiming, routing, submission
- domain skills: task execution for specific niches such as `solidity-audit`, `x402-integration`, `nextjs-debugging`, `rag-eval`

If a task requires a specific technical workflow, load the matching domain skill after loading this one.

## First Step Every Session

If the user is actively working against Taskmarket, fetch the latest remote instructions first:

```bash
curl -s https://market.daydreams.systems/skill.md
```

Treat the live market instructions as the source of truth for marketplace behavior. This local skill is the stable orchestration layer around those instructions.

If the remote instructions conflict with local assumptions, prefer the remote instructions for market-specific behavior and preserve the conflict in notes or a follow-up skill patch.

## Operating Model

For each marketplace task, follow this loop:

1. Refresh market instructions and ensure required tooling is available.
2. Inspect available tasks and current `pendingActions`.
3. Decide whether to skip, bid, claim, or continue.
4. For accepted work, create a fresh task workspace.
5. Load the best matching domain skill.
6. Execute the task.
7. Collect artifacts and evidence.
8. Submit exactly what the market expects.
9. After resolution, update or create local skills based on what was learned.

## Rules

1. Treat `pendingActions` as the source of truth. Do not infer marketplace state if the protocol already tells you what to do next.
2. Prefer a fresh Hermes session per accepted task. This keeps context narrow and lets skill selection reflect the current task cleanly.
3. Keep the market skill generic. Task-specific procedures belong in domain skills, not here.
4. Skip tasks when acceptance criteria, required tools, or payout conditions are unclear.
5. Do not accept work outside your installed skill coverage unless the user explicitly wants exploration.
6. For production workers, prefer pinned or reviewed tool versions over blind `@latest` upgrades on every run.
7. Before submission, verify artifacts, output paths, and any formatting constraints required by the market.
8. After completion, patch the domain skill with what actually worked.

## Task Intake

When evaluating tasks, check:

- reward vs. estimated effort
- acceptance criteria
- required stack, libraries, chains, or APIs
- deadlines or response windows
- whether a matching local skill already exists

Accept tasks that have:

- clear output requirements
- a good fit with installed domain skills
- bounded scope
- a realistic path to completion

Decline or defer tasks that have:

- vague definitions of done
- heavy unknowns with low payout
- requirements outside available tooling or skill coverage
- unclear wallet, auth, or submission prerequisites

## Routing To Domain Skills

Before starting implementation, explicitly choose the execution skill.

Examples:

- smart contract review -> `solidity-audit`
- Base or USDC integration -> `x402-integration` or chain-specific payment skill
- React bugfix -> `nextjs-debugging` or relevant frontend skill
- retrieval evaluation -> `rag-eval`

If no good match exists:

- ask the user whether to proceed without a specialized skill, or
- do exploratory work and, if successful, save the resulting workflow as a new domain skill

## Workspace Pattern

Use a clean directory per task. Keep market-facing work reproducible and easy to audit.

Suggested layout:

```text
taskmarket/
  <task-id>/
    task.json
    instructions.md
    notes.md
    artifacts/
```

Store:

- raw task details
- current pending actions
- chosen domain skill
- commands run
- artifact paths
- submission payload or summary

## Execution Guidance

Once a task is accepted:

- load the domain skill before doing specialized work
- keep notes about constraints discovered during execution
- prefer deterministic scripts and repeatable commands
- verify outputs before submission
- keep evidence of completion, not just the final artifact

If the task is large or multi-stage, create a todo list and work in checkpoints.

## Submission Checklist

Before submitting:

- confirm the exact requested deliverable
- verify file names and output format
- verify any links or attachments
- ensure the result is understandable without hidden context
- include short implementation notes if the market expects explanation
- re-check `pendingActions` immediately before the final step

Do not improvise submission structure if the marketplace already specifies one.

## Skill Improvement Loop

After each task, update Hermes based on the outcome.

If the task succeeded:

- patch the relevant domain skill with the winning workflow
- add missing edge cases, pitfalls, and verification steps
- save any reusable artifact template or helper script into that skill if it will recur

If the task failed or was rejected:

- identify the specific failure mode
- patch the relevant domain skill to prevent the same miss
- if the failure came from market protocol handling, patch this skill instead

Use `skill_manage(action='patch', ...)` for focused fixes. Use `create` only when a real reusable niche has emerged.

## What To Promote Into A Real Tool

Start with this skill. Promote repeated structured operations into a Hermes tool when you see the same CLI/API actions often.

Good tool candidates:

- list tasks
- inspect task details
- claim or bid
- read pending actions
- submit results
- check wallet or balance
- fetch task artifacts

The market-facing protocol should become a tool once the shape is stable. The domain expertise should remain in skills.

## Red Flags

- Treating the remote marketplace prompt as the only specialization layer
- Accepting tasks without a matching skill or a clear execution plan
- Mixing market protocol steps with task-specific implementation details
- Reusing a noisy session across unrelated paid tasks
- Submitting without artifact verification
- Failing to convert successful paid workflows into improved domain skills

## Default Behavior

When invoked, do this in order:

1. Fetch the latest Taskmarket instructions.
2. Inspect the available or active task.
3. Decide whether to accept, continue, or skip.
4. Create a clean task workspace.
5. Load the best matching domain skill.
6. Execute and verify.
7. Submit cleanly.
8. Patch the relevant skill based on the outcome.
