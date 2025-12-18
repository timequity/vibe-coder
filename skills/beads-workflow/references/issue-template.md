# Issue Template for Self-Contained Tasks

This template ensures issues contain all context needed for any developer (human or AI) to understand and implement without external references.

## Template

```markdown
## Summary
[What we're doing and why — 1-2 sentences]

## Context
[Why this is needed, what problem it solves, background info]

## Files to Modify
- `path/to/file.ts:123` — what changes
- `path/to/new-file.ts` — new file to create

## Implementation Steps
1. First specific step with details
2. Second step
3. ...

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests pass

## Example (optional)
Before:
```code
// old code
```

After:
```code
// new code
```

## Notes / Gotchas
- Known limitations
- What NOT to do
- Related docs or issues
```

## Required Sections

| Section | Purpose | Required |
|---------|---------|----------|
| Summary | What and why | Yes |
| Context | Background info | For complex tasks |
| Files to Modify | Exact paths | Yes |
| Implementation Steps | How to do it | Yes |
| Acceptance Criteria | Definition of done | Yes |
| Example | Before/after code | When helpful |
| Notes | Gotchas, warnings | When applicable |

## Good vs Bad Examples

### Bad Issue (lacks context)

```markdown
Title: Fix the auth bug

Description: The login doesn't work, fix it.
```

Problems:
- No context about what's broken
- No files mentioned
- No steps to reproduce or fix
- No acceptance criteria

### Good Issue (self-contained)

```markdown
Title: Fix JWT token expiration not being checked on API calls

## Summary
API endpoints accept expired JWT tokens, allowing unauthorized access after logout.

## Context
Security vulnerability reported by user. JWT expiration (`exp` claim) is set correctly
on token creation but not validated in the auth middleware.

## Files to Modify
- `src/middleware/auth.ts:45` — add expiration check in `verifyToken()`
- `src/utils/jwt.ts:12` — add `isExpired()` helper function
- `tests/auth.test.ts` — add test for expired token rejection

## Implementation Steps
1. Add `isExpired(token)` function to `jwt.ts` that checks `exp` claim vs current time
2. Call `isExpired()` in `verifyToken()` middleware before `next()`
3. Return 401 with `{ error: "Token expired" }` if expired
4. Add test case with expired token (set `exp` to past timestamp)

## Acceptance Criteria
- [ ] Expired tokens return 401 status
- [ ] Error message is "Token expired"
- [ ] Valid tokens still work
- [ ] Test covers expiration scenario

## Example
Before (auth.ts:45):
```typescript
const decoded = jwt.verify(token, SECRET);
req.user = decoded;
next();
```

After:
```typescript
const decoded = jwt.verify(token, SECRET);
if (isExpired(decoded)) {
  return res.status(401).json({ error: "Token expired" });
}
req.user = decoded;
next();
```

## Notes
- Don't change token generation — expiration is set correctly there
- Consider adding 5-minute grace period for clock skew (optional)
- Related: AUTH-123 (token refresh feature)
```

## Using bd Rich Fields

Beads supports additional fields beyond description:

```bash
# Edit description (main content)
bd edit <id> --description

# Edit design notes (technical approach)
bd edit <id> --design

# Edit acceptance criteria
bd edit <id> --acceptance-criteria

# Edit notes (gotchas, warnings)
bd edit <id> --notes
```

### When to Use Each Field

| Field | Use For |
|-------|---------|
| `description` | Main content (use template above) |
| `design` | Technical approach, architecture decisions |
| `acceptance_criteria` | Separate checklist if description is long |
| `notes` | Warnings, gotchas, related links |

## Validation

Run quality check before committing:

```bash
python3 skills/beads-validation/scripts/validate_beads.py --check-quality

# Output:
## Beads Quality Check
[PASS] vibe-abc: Summary present, 4/4 sections, 523 chars
[WARN] vibe-xyz: Missing "Files to Modify" section
[FAIL] vibe-123: Description too short (45 chars)
```

## Minimum Requirements

For an issue to pass quality validation:
1. Description length > 100 characters
2. Contains Summary section (or: Overview, Goal, Цель)
3. Contains Files section (or: Файлы, Paths, Изменения)
4. Contains Steps section (or: Implementation, План, Шаги)
5. Contains Criteria section (or: Acceptance, Done when, Готово когда)
