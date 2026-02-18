# Conductor Workflow

## Test Coverage

- Target: **>80%** coverage for new code
- Run tests before marking any task complete
- If no test framework is set up for a module, note it in learnings.md

## Commit Strategy

- **Commit after each task** (not each phase)
- Commit message format: `type(scope): description`
  - Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`
  - Example: `feat(dashboard): add booking card with price delta display`
- Never commit broken code — all tests must pass before committing

## Task Summaries

- Use **Git Notes** to store task implementation summaries
- Record: what was done, any gotchas discovered, and patterns to reuse
- Command: `git notes add -m "summary" <commit-hash>`

## Phase Completion

- Each phase ends with a **manual verification task**
- Format: `Task: Conductor - User Manual Verification '<Phase Name>'`
- Do not mark a phase complete until the user has verified the output

## Definition of Done (per task)

1. Implementation matches the spec
2. Tests written and passing (>80% for touched code)
3. No TypeScript errors (`npm run typecheck`)
4. No lint errors (`npm run lint`)
5. Committed with descriptive message
6. Git note added with task summary

## Track Lifecycle

1. **new** → Work not yet started
2. **in_progress** → Active development
3. **complete** → All tasks done, user verified
4. **archived** → Moved to archive after completion

## Branching

- Work on `main` for personal projects (no PRs required)
- For large tracks: create a feature branch `conductor/<track_id>`
- Merge to main when track is complete and verified
