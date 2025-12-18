# Session Lifecycle

Detailed guide for managing work sessions with beads.

## Phase 1: Initialization

### Check Environment

```bash
# Verify beads is available
which bd

# Check for .beads directory
ls -d .beads 2>/dev/null || echo "No beads in this project"

# Get project prefix (from config)
bd config get id.prefix
```

### Load Current State

```bash
# Tasks currently being worked on
bd list --status in_progress --json

# Available tasks (unblocked)
bd ready --json

# All open tasks
bd list --status open --json
```

### Task Selection Flow

```
┌─────────────────────────────────────┐
│ Session Start                       │
└─────────────────┬───────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ in_progress     │
        │ exists?         │
        └────────┬────────┘
                 │
         ┌───────┴───────┐
         │               │
        YES             NO
         │               │
         ▼               ▼
   ┌───────────┐  ┌─────────────┐
   │ Continue  │  │ Show ready  │
   │ task      │  │ tasks       │
   └───────────┘  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ User picks  │
                  │ task        │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Start task  │
                  │ in_progress │
                  └─────────────┘
```

## Phase 2: Active Work

### Track Progress

Use TodoWrite to break down the beads task:

```
Beads Task: "Implement user auth" (id: abc-123)
├── [ ] Research existing auth patterns
├── [ ] Create auth middleware
├── [ ] Add login endpoint
├── [ ] Add logout endpoint
└── [ ] Write tests
```

### Handle Discoveries

When new work is discovered during implementation:

**Minor subtask (same scope):**
- Add to TodoWrite list
- Complete within current task

**Significant new work:**
```bash
bd create "New discovery" -t task -p 2
bd dep add <new-id> <current-id> --type parent-child
```

**Blocker found:**
```bash
bd create "Blocking issue" -t bug -p 1
bd dep add <current-id> <blocker-id> --type blocked-by
```

### Context Preservation

Maintain in conversation:
- Current task ID
- Task title
- Remaining TodoWrite items
- Any blockers encountered

## Phase 3: Completion

### Verify Completion

Before closing:
1. All TodoWrite items checked
2. Tests pass (if applicable)
3. Code committed (if applicable)

### Close Task

```bash
bd close <id> --reason "Implemented feature X with tests"
bd sync
```

### Transition

After closing:
1. Show updated ready list
2. Suggest next high-priority task
3. Or ask if user wants to continue

## Phase 4: Session End

### Clean State

```bash
# Sync all changes
bd sync

# Verify state
bd list --status in_progress
```

### Summary Format

```
## Сессия завершена

**Выполнено:**
- [x] task-123: Implement user auth

**В процессе:**
- [ ] task-456: Add password reset (60% done)

**Следующие задачи:**
- task-789: Email verification (P1)
- task-012: User profile page (P2)
```

## Phase 5: Handoff Protocol

When transferring work to another developer or AI agent.

### Pre-Handoff Checklist

```
[ ] 1. All code changes committed
[ ] 2. In-progress tasks have continuation issues
[ ] 3. Issues are self-contained (validate with --check-quality)
[ ] 4. bd sync completed
[ ] 5. git push completed
[ ] 6. CLAUDE.md has project context
```

### Creating Continuation Issues

For work-in-progress that spans sessions:

```bash
bd create "Continue: [original task name]" -t task -p 1
bd edit <new-id> --description
```

Use this template for continuation issues:

```markdown
## Summary
Continue work on [original task] — [brief status].

## Progress So Far
- [x] Step 1 completed
- [x] Step 2 completed
- [ ] Step 3 in progress (50%)
- [ ] Step 4 not started

## Current State
- Branch: `feature/xyz`
- Last commit: `abc123` — "WIP: description"
- Files modified: `src/foo.ts`, `src/bar.ts`

## Remaining Work
1. Complete step 3: [specific details]
2. Implement step 4: [specific details]
3. Write tests for new functionality

## Blockers / Notes
- Need clarification on X
- Watch out for Y edge case

## Acceptance Criteria
- [ ] Original criteria from parent task
```

### Handoff Commands

```bash
# 1. Ensure all issues are quality-checked
python3 skills/beads-validation/scripts/validate_beads.py --check-quality

# 2. Close completed work
bd close <completed-id> --reason "Completed"

# 3. Create continuation for WIP
bd create "Continue: task name" -t task -p 1
bd dep add <new-id> <original-id> --type continues

# 4. Sync and push
bd sync
git add . && git commit -m "WIP: handoff state"
git push

# 5. Verify clean state
bd list --status in_progress  # Should show continuation tasks
bd ready                       # Should show available work
```

### For New Developer

When receiving a handoff:

```bash
# 1. Clone and setup
git clone <repo>
cd <project>

# 2. Get context
cat CLAUDE.md                  # Project overview
bd prime                       # Load workflow instructions

# 3. Find work
bd ready                       # Available tasks
bd list --status in_progress   # Ongoing work

# 4. Pick a task
bd show <id>                   # Read full context
bd update <id> --status in_progress

# 5. Start working
# The issue description contains everything needed
```

### Validation Before Handoff

```bash
python3 skills/beads-validation/scripts/validate_beads.py --check-quality --check-deps

# Expected output:
## Beads Quality Check
[PASS] All issues have sufficient description (>100 chars)
[PASS] All issues have required sections
[PASS] No circular dependencies
[PASS] Ready queue has available work

Result: Ready for handoff
```
