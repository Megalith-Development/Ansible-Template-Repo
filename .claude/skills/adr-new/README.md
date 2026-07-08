# ADR New Skill

A Claude Code skill for creating Architecture Decision Records (ADRs) with guided workflows, consistency checking, and automatic linking to Decision Records (DRs).

## What This Skill Does

This skill provides an interactive or quick workflow for documenting architectural decisions in a standardized format. It creates ADR files, maintains an index, validates consistency with existing architecture, and optionally links to originating Decision Records.

## When to Use This Skill

Invoke this skill when you need to:

- **Document** a finalized architecture decision
- **Record** a choice between multiple options ("we decided to use X")
- **Formalize** a decision from a concluded Discussion Record (DR)
- **Capture** architectural choices made during development
- **Create** a formal record after resolving an architectural question

**Do NOT use this skill for:**
- Capturing questions or open discussions (use `dr-new` instead)
- Reviewing existing ADRs (use `sdlc-status` instead)
- General documentation

## Invocation Methods

### Interactive Mode
```
/adr-new
```
Guided prompts walk you through all sections of the ADR.

### Quick Mode with Title
```
/adr-new "Decision Title"
```
Skips title prompt, continues with interactive questions.

### From Decision Record
```
/adr-new --from-dr DR-008
```
Pre-fills context, options, and decision from a decided DR.

### With Status
```
/adr-new "Decision Title" --status accepted
```
Sets the initial status (proposed or accepted).

### Combined Parameters
```
/adr-new "gRPC over REST" --from-dr DR-015 --status accepted
```

## What the Skill Provides

### Structured ADR Creation

The skill guides you through capturing:

1. **Decision Title**: Clear, concise statement of what was decided
2. **Context**: Why this decision is needed, including constraints and drivers
3. **Options Considered**: At least 2 alternatives with pros/cons for each
4. **Decision**: Which option was chosen and why
5. **Consequences**: Positive, negative, and neutral outcomes
6. **Status**: Proposed or Accepted
7. **Implementation Notes**: Optional guidance for implementing the decision
8. **Related ADRs**: Links to related or superseded decisions
9. **References**: Link to originating DR if applicable

### Consistency Checking

Before creating the ADR, the skill performs two critical checks:

#### Architectural Invariants Check
Reads `AGENTS.md` to verify the decision doesn't contradict established architectural invariants without proper superseding.

```
⚠ This ADR modifies architectural invariant [N]: [name]

This requires:
1. Explicit "Supersedes" or "Amends" reference
2. Update to AGENTS.md after acceptance
3. Human approval — invariant changes cannot be auto-accepted
```

#### Existing ADR Consistency
Reads `.sdlc/adrs/README.md` to check for:
- Conflicts with accepted ADRs
- Potential duplicates
- Decisions that should be explicitly referenced

```
⚠ This ADR contradicts ADR-012 without superseding it.

Either:
1. Add "Supersedes: ADR-012"
2. Modify to be compatible
3. Explain why both can coexist
```

### Automatic Numbering

The skill scans existing ADRs and automatically assigns the next sequential number.

### Index Maintenance

Automatically updates `.sdlc/adrs/README.md` with:
- New entry in the ADR table
- Changelog entry with creation date
- Maintains numerical order

### DR Linking

If created from a Decision Record:
- Links ADR to originating DR in references
- Updates DR with ADR reference
- Maintains bidirectional traceability

## ADR File Format

Created ADRs follow this structure:

```markdown
# ADR-NNN: [Title]

**Status**: Proposed | Accepted | Superseded | Deprecated
**Date**: YYYY-MM-DD

## Context

[Why this decision is needed, including constraints and drivers]

## Decision Drivers

- [Key factor 1]
- [Key factor 2]

## Options Considered

### Option 1: [Name]

[Description]

**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]

### Option 2: [Name]

[Similar structure]

## Decision

We will use [chosen option] because [rationale].

### Why Not Chosen

- **Option X**: [Reason for rejection]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Cost 1]
- [Cost 2]

### Neutral
- [Side effect 1]

## Implementation Notes

[Optional guidance for implementing this decision]

## Related Decisions

- [ADR-NNN](ADR-NNN-title.md): [Relationship description]

## References

- [DR-NNN](../drs/DR-NNN-title.md): Originating discussion

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| YYYY-MM-DD | [Name] | Initial decision |
```

## Flexible Input Parsing

The skill accepts freeform input for options:

### Compact Format
```
Redis: In-memory cache with TTL
+ Fast, built-in expiration
- Extra container

Memcached: Distributed cache
+ Simple, lightweight
- No persistence
```

### Structured Format
```
Option 1: Redis
Pros: Fast, TTL support
Cons: Extra container

Option 2: Memcached
Pros: Simple, lightweight
Cons: No persistence
```

Both are parsed into standardized ADR sections.

## Status Values

- **Proposed**: Decision documented but awaiting review/approval
- **Accepted**: Decision approved and active
- **Superseded**: Replaced by a newer ADR
- **Deprecated**: No longer recommended but not formally replaced

## File Naming Convention

Files are named: `ADR-NNN-title-slug.md`

- **NNN**: Sequential number (padded to 3 digits)
- **title-slug**: 3-5 lowercase words with hyphens

Example: `ADR-014-redis-session-cache.md`

## From-DR Workflow

When using `--from-dr DR-NNN`:

1. Reads the specified Decision Record
2. Extracts context, options, decision, and rationale
3. Shows summary for confirmation
4. User can accept or modify
5. Creates ADR with pre-filled content
6. Automatically links ADR ↔ DR

This streamlines the process of formalizing decisions from team discussions.

## Edge Cases

| Situation | Handling |
|-----------|----------|
| Fewer than 2 options | Prompts for at least one more option |
| DR not found | Warns and continues without pre-fill |
| DR not yet decided | Warns that DR is still open |
| No consequences listed | Records "To be determined" |
| Modifies invariant | Requires explicit acknowledgment |
| Contradicts existing ADR | Requires resolution before creation |

## Directory Structure

ADRs are stored in:
```
.sdlc/
  adrs/
    README.md              # Index of all ADRs
    ADR-001-first-decision.md
    ADR-002-second-decision.md
    ...
```

## When to Use Proposed vs Accepted

- **Proposed**: Use when the decision needs team review, approval, or stakeholder sign-off
- **Accepted**: Use when you have authority to make the decision or it's already been approved

The skill defaults to "Proposed" to encourage review, but you can specify `--status accepted` for decisions that don't require additional approval.

## Integration with Other Skills

- **dr-new**: Create Decision Records for questions → resolve them → use `/adr-new --from-dr` to formalize
- **sdlc-status**: Review all ADRs and their current status
- **simplify**: Can suggest when architectural decisions should be documented as ADRs

## Best Practices

1. **Require multiple options**: The skill enforces documenting at least 2 alternatives to show you considered trade-offs
2. **Be specific in consequences**: Use +/- prefixes to clearly categorize impacts
3. **Link related decisions**: Reference ADRs that are superseded, related, or build on this decision
4. **Add implementation notes**: Provide guidance for developers who will implement the decision
5. **Keep title concise**: 3-7 words that clearly state what was decided
6. **Document the "why not"**: Explain why rejected options weren't chosen

## Example Usage Scenarios

### After a Team Decision
```
User: We decided to use PostgreSQL for the main database instead of MongoDB
/adr-new "PostgreSQL for Main Database"
```

### Formalizing a Discussion
```
User: /adr-new --from-dr DR-023
```

### Quick Documentation
```
User: /adr-new "Use gRPC for microservices" --status accepted
```

### During Architecture Design
```
User: We've been discussing caching strategies. Let me document this decision.
/adr-new
```

## Output

Upon successful creation:
```
Done!
- Created: ADR-014-redis-session-cache.md
- Status: Proposed
- Updated: .sdlc/adrs/README.md
- Linked to: DR-008

Next: Share for review, then update status to Accepted
```

## Requirements

- `.sdlc/adrs/` directory must exist
- `AGENTS.md` should exist for invariant checking
- If using `--from-dr`, the Decision Record must exist

## Further Reading

- `SKILL.md`: Complete skill prompt with implementation details
- `references/adr-new-example.md`: Example interactive sessions
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard

## Support

This skill is maintained as part of the Megalith Ansible Template Repository project. Issues and improvements can be submitted through the repository's issue tracker.
