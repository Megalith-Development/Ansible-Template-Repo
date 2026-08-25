---
name: ansible-code-review
description: >-
  Performs comprehensive code review of Ansible content (roles, playbooks, tasks,
  variables) based on Red Hat CoP best practices, AGENTS.md standards, ansible-lint
  rules, and established patterns. Reviews role structure, variable management, task
  design, idempotency, AAP patterns, and provides actionable feedback organized by
  severity with clear remediation guidance. Use when reviewing Ansible code, after
  file modifications, or when user requests code review.
argument-hint: "[path] [--severity critical|warning|all] [--lint]"
user-invocable: true
metadata:
  author: Megalith Development
  version: 1.0.0
---

# Ansible Code Review

Performs comprehensive code review of Ansible content based on industry best practices and repository standards.

## Arguments

If `$ARGUMENTS` is provided, parse for:
- Path argument (role, playbook, file, or directory) → review target
- `--severity critical|warning|all` → filter by severity level
- `--lint` → run ansible-lint if available
- `--format markdown|json` → output format (default: markdown)

## Usage

```
/ansible-code-review                          # Review git-changed files
/ansible-code-review roles/example            # Review specific role
/ansible-code-review playbooks/site.yml       # Review specific playbook
/ansible-code-review --severity critical      # Show only critical issues
/ansible-code-review --lint                   # Include ansible-lint execution
```

## Behavior

### Phase 1: Scope Determination

**If path argument provided:**
- Use the specified path as review target
- Detect type: role, playbook, task file, or directory
- Validate path exists

**If no path argument:**
- Run `git status --porcelain` to find modified files
- Filter for Ansible content:
  - Files in `roles/`, `playbooks/`, `tasks/`, `rulebooks/`
  - Files ending in `.yml` or `.yaml`
  - Exclude `.github/`, `devfile.yaml` (per .ansible-lint)
- If no Ansible files changed, ask user to specify target

**Scope categories:**
- **Role**: Full role review (structure, variables, tasks, meta, handlers)
- **Playbook**: Playbook review (structure, role usage, vars, AAP patterns)
- **Task file**: Individual task file review
- **Directory**: Multiple roles/playbooks in specified directory
- **Repository**: Full repository scan

### Phase 2: Context Loading

Read essential context files to build review criteria:

1. **Read `/AGENTS.md`**
   - Load all MUST requirements (critical violations)
   - Load all SHOULD requirements (warnings)
   - Load MAY recommendations (suggestions)
   - Note key patterns: validation, argument_specs, idempotency, roles-as-classes

2. **Read `/.ansible-lint`**
   - Load configured profile (basic, moderate, production, etc.)
   - Note exclude_paths
   - Note warn_list vs error rules

3. **Detect repository patterns**
   - Check for existing roles in `roles/` directory
   - Identify naming conventions
   - Look for `filter_plugins/` directory
   - Check for `aap_config/` directory (AAP config-as-code patterns)

4. **Parse arguments for filters**
   - Extract severity filter (critical, warning, all)
   - Check for --lint flag
   - Note output format preference

### Phase 3: Multi-Layer Review

Execute comprehensive review across six layers:

#### Layer 1: Structural Review

**For Roles:**

Required directories (MUST exist):
- `tasks/` - Task files
- `defaults/` - Default variables
- `meta/` - Role metadata

Recommended directories (SHOULD exist):
- `handlers/` - State change handlers (if service management)
- `vars/` - Role-specific variables
- `templates/` or `files/` - Assets (if deploying configs)

Required files (MUST exist):
- `tasks/main.yml` - Main task file
- `defaults/main.yml` - All variables initialized
- `meta/main.yml` - Role metadata and dependencies
- `meta/argument_specs.yml` - Schema validation and documentation
- `tasks/validate.yml` - Input validation for roles accepting external vars

Recommended files (SHOULD exist):
- `README.md` - Role documentation
- `handlers/main.yml` - If service management tasks exist

**For Playbooks:**

Required elements (MUST exist):
- Clear play name
- Hosts specification
- Proper YAML structure

Recommended patterns (SHOULD exist):
- Use of `import_role` or `include_role` vs duplicating logic
- Thin playbooks (logic in roles, not playbooks)
- Action-specific naming (e.g., `create_resource.yml`, `update_resource.yml`)

**Checklist:**
- [ ] Role/playbook has required directories/structure
- [ ] Required files present (meta/argument_specs.yml, tasks/validate.yml)
- [ ] README.md exists and documents usage
- [ ] File naming follows conventions
- [ ] Directory structure matches template

**Critical Issues:**
- Missing `meta/argument_specs.yml` for roles accepting parameters
- Missing `tasks/validate.yml` for roles accepting external variables

**Warnings:**
- Missing `README.md`
- Missing recommended directories (handlers/ when service tasks present)
- Inconsistent with repository structure

**Suggestions:**
- Consider adding `tests/` directory for molecule tests
- Consider adding example playbooks in `examples/`

#### Layer 2: Variable Management Review

**Variable Initialization:**
- All variables MUST be initialized in `defaults/main.yml`
- Variables MUST be data-only (no embedded logic)
- Variables SHOULD have descriptive names (snake_case)

**Variable Validation:**
- External variables MUST be validated in `tasks/validate.yml`
- Use `ansible.builtin.assert` with clear fail_msg and success_msg
- Validate:
  - Required variables are defined
  - Formats and constraints (e.g., port ranges, valid choices)
  - Relationships between variables
- Fail fast with clear error messages

**Argument Specs:**
- `meta/argument_specs.yml` MUST exist for roles with parameters
- MUST define all entry points (main, and any tasks_from callables)
- MUST declare all required and optional variables with types
- MUST include descriptions for user-facing variables
- SHOULD use appropriate validators (choices, min/max, regex)

**Secret Management:**
- No hardcoded secrets in tracked files (CRITICAL)
- Secrets SHOULD use Ansible Vault or AAP credentials
- Check for patterns like:
  - `password: "abc123"`
  - `api_key: "secret"`
  - `token: "xyz"`
  - Suspicious base64 strings in plain text

**Checklist:**
- [ ] All variables in defaults/main.yml
- [ ] Variables are data-only (no embedded logic)
- [ ] External variables validated in tasks/validate.yml
- [ ] meta/argument_specs.yml exists and complete
- [ ] Argument specs define types and descriptions
- [ ] Argument specs use appropriate validators
- [ ] No hardcoded secrets detected

**Critical Issues:**
- Hardcoded secrets in tracked files
- Missing argument_specs.yml
- Missing validation for required external variables

**Warnings:**
- Missing validation in tasks/validate.yml for roles accepting parameters
- Incomplete argument_specs.yml (missing types or descriptions)
- Poor variable naming (not snake_case, unclear purpose)

**Suggestions:**
- Add more descriptive variable names
- Group related variables in defaults/main.yml with comments
- Consider adding examples in defaults/main.yml comments

#### Layer 3: Task Design Review

**Task Naming:**
- All tasks MUST have descriptive names
- Task names SHOULD describe what's being done, not how
- Task names SHOULD be concise but clear

**Module Selection:**
- All modules MUST use FQCN (Fully Qualified Collection Names)
  - Good: `ansible.builtin.copy`, `ansible.builtin.service`
  - Bad: `copy`, `service`
- Prefer appropriate modules over shell/command
  - Use `ansible.builtin.copy` instead of `shell: cp`
  - Use `ansible.builtin.template` instead of `shell: sed`
  - Use `ansible.builtin.package` instead of `shell: yum install`
  - Use `ansible.builtin.service` instead of `shell: systemctl`

**Shell/Command/Raw Module Usage:**
- DISCOURAGED - must be justified
- MUST include at least one safeguard:
  - `changed_when` - Define when task registers as changed
  - `failed_when` - Define failure conditions
  - `creates` - Skip if file exists
  - `removes` - Skip if file doesn't exist
- MUST include comment explaining why module-based approach not used
- SHOULD register output for debugging

**Idempotency:**
- All tasks MUST aim to be idempotent
- Service restarts SHOULD use handlers with `notify`
- Tasks that change state SHOULD trigger handlers, not inline restarts
- Check mode SHOULD work where possible

**Control Structures:**
- `when` conditions SHOULD be clear and readable
- Prefer `loop` over deprecated `with_items`
- `notify` SHOULD reference handlers for state changes
- `tags` MAY be used for selective execution

**Checklist:**
- [ ] All tasks have descriptive names
- [ ] All modules use FQCN
- [ ] Idempotent design throughout
- [ ] No shell/command/raw OR properly justified with safeguards
- [ ] Handlers used for service restarts
- [ ] Proper use of when, loop, notify, tags
- [ ] No deprecated modules or syntax

**Critical Issues:**
- Tasks without names
- shell/command/raw without safeguards (changed_when, failed_when, creates, removes)
- Non-idempotent operations without justification
- Breaking idempotency patterns

**Warnings:**
- shell/command/raw without justification comment
- Not using FQCN for modules
- Deprecated module usage (with_items vs loop)
- Service restarts inline instead of via handlers
- Unclear or missing when conditions

**Suggestions:**
- More descriptive task names
- Additional tags for selective execution
- Better organization of related tasks

#### Layer 4: Data Transformation Review

**Jinja Filter Usage:**
- Maximum 4 chained filters (except `json_query`)
- `json_query` is allowed for complex data extraction
- Nested logic allowed only if human-readable
- Avoid overly complex one-liners

**Complex Transformations:**
- Complex data restructuring SHOULD use Python filter plugins
- Filter plugins SHOULD be placed in `filter_plugins/` directory
- Filters SHOULD be focused and reusable
- Complex filters SHOULD have unit tests

**When to create filter plugin:**
- Jinja expression has >4 filters (except json_query)
- Logic repeated across multiple files
- Expression difficult to understand or maintain
- Complex data structure transformation needed

**Checklist:**
- [ ] Jinja filter chains ≤ 4 (except json_query)
- [ ] No overly complex nested logic
- [ ] Readable expressions throughout
- [ ] Complex transformations use filter plugins
- [ ] filter_plugins/ directory exists if needed

**Critical Issues:**
- None (this is primarily a maintainability concern)

**Warnings:**
- Jinja filter chains >4 without filter plugin
- Complex nested logic that's hard to read
- Repeated transformation logic (DRY violation)

**Suggestions:**
- Extract complex Jinja to Python filter plugin
- Add unit tests for filter plugins
- Simplify complex expressions

#### Layer 5: AAP Configuration Review

**Detect AAP Patterns:**
- Check for `aap_config/` directory
- Check for `infra.aap_configuration` collection usage
- Check for AAP-related variables (aap_hostname, controller_*, hub_*)

**If AAP config-as-code detected:**

**Dispatch Pattern:**
- SHOULD use `infra.aap_configuration.dispatch` role
- Playbooks SHOULD load vars from `aap_config/` directory
- Variables SHOULD be organized by AAP component (controller/, hub/, eda/, gateway/)

**Connection Variables:**
- MUST define proper connection variables:
  - `aap_hostname` / `controller_hostname`
  - `aap_token` / `controller_token` (from vault/credentials)
- MUST NOT hardcode credentials

**Dependency Ordering:**
- Objects MUST be created in dependency-aware order:
  - Organizations → Credentials → Projects → Inventories → Job Templates
- Understand natural dependencies between AAP objects

**Environment Separation:**
- Multi-environment configs SHOULD use directory structure:
  - `aap_config/dev/`, `aap_config/prod/`, `aap_config/qa/`
- OR use variable prefixes: `dev_`, `prod_`, `qa_`

**For AAP-Targeted Roles:**
- Entry point playbooks SHOULD call roles via import_role/include_role
- Use `tasks_from` for modular role functions
- Keep playbooks thin (expose role functions to AAP Job Templates)

**Checklist:**
- [ ] Uses infra.aap_configuration.dispatch (if AAP config-as-code)
- [ ] Proper connection variables defined
- [ ] Dependency-aware object ordering
- [ ] Environment separation if multi-env
- [ ] No hardcoded credentials
- [ ] Playbooks call roles (not duplicate logic)

**Critical Issues:**
- Hardcoded AAP credentials
- Breaking dependency order (e.g., job template before project)

**Warnings:**
- Not using dispatch role for AAP configuration
- Missing environment separation in multi-env setup
- Duplicating role logic in playbooks

**Suggestions:**
- Consider migrating to infra.aap_configuration if using raw API
- Add environment-based variable organization
- Extract duplicated playbook logic to roles

#### Layer 6: ansible-lint Compliance

**Check for ansible-lint:**
```bash
which ansible-lint
```

**If ansible-lint available and `--lint` flag provided:**
1. Run ansible-lint on target path
2. Parse output for rule violations
3. Map rule IDs to severity levels
4. Integrate into review findings

**If ansible-lint not available, check common patterns:**

**Based on `.ansible-lint` profile (basic):**
- Task names present
- No trailing whitespace in YAML files
- Truthy values consistent (yes/no vs true/false)
- No deprecated modules
- YAML syntax valid
- Proper indentation (2 spaces)
- Naming conventions followed (snake_case for variables)

**ansible-lint severity mapping:**
- Errors → Critical issues
- Warnings → Warnings
- Info → Suggestions

**Checklist:**
- [ ] All tasks named
- [ ] No trailing whitespace
- [ ] Consistent truthy values
- [ ] No deprecated modules
- [ ] Valid YAML syntax
- [ ] Proper indentation
- [ ] Naming conventions followed

**Critical Issues:**
- ansible-lint errors that break execution
- Syntax errors
- Deprecated modules with no alternative

**Warnings:**
- ansible-lint warnings
- Inconsistent truthy values
- Style violations

**Suggestions:**
- ansible-lint info messages
- Style improvements

### Phase 4: Severity Classification

Classify all findings by severity level:

#### Critical [CRITICAL] (Blocks Production)

Issues that should be addressed before deployment:
- Missing `meta/argument_specs.yml` for roles with parameters
- Missing `tasks/validate.yml` for roles accepting external variables
- Hardcoded secrets in tracked files
- shell/command/raw without safeguards (changed_when, failed_when, creates, removes)
- Non-idempotent operations without justification
- Breaking AAP dependency order
- ansible-lint errors that break execution
- AGENTS.md MUST violations

**Action Required:** MUST fix before merge

#### Warning [WARNING] (Should Fix Before Merge)

Issues that should be addressed:
- Missing `README.md` for roles
- Missing recommended directories (handlers/ when service tasks present)
- Complex Jinja (>4 filters) without filter plugin
- shell/command/raw without justification comment
- Not using FQCN for modules
- Deprecated module usage
- Missing task names
- Service restarts inline instead of via handlers
- Not using AAP dispatch pattern for config-as-code
- Duplicating role logic in playbooks
- ansible-lint warnings
- AGENTS.md SHOULD violations

**Action Required:** Strongly recommended to fix

#### Suggestion [SUGGESTION] (Improvement Opportunities)

Opportunities for enhancement:
- Better variable naming
- More descriptive task names
- Additional task tags
- Code organization improvements
- Documentation enhancements
- Performance optimizations
- Test coverage recommendations
- ansible-lint info messages

**Action Required:** Consider for future improvements

### Phase 5: Output Generation

Generate comprehensive markdown review report:

```markdown
# Ansible Code Review: [scope]

## Summary
- **Files reviewed**: X
- **Critical issues** [CRITICAL]: X
- **Warnings** [WARNING]: X
- **Suggestions** [SUGGESTION]: X
- **Overall status**: [Ready/Needs work/Blocked]

---

## Critical Issues [CRITICAL]

### [File/Role/Path] - [Issue Title]

**Severity**: Critical
**Location**: `path/to/file.yml:line` (if line number available)
**Issue**: [Clear description of what's wrong]
**Impact**: [Why this should be addressed]
**Fix**: [Specific remediation steps]
**Reference**: [AGENTS.md section or ansible-lint rule]

**Current code:**
```yaml
# Bad example from actual file
```

**Fixed code:**
```yaml
# Good example showing the fix
```

---

## Warnings [WARNING]

### [File/Role/Path] - [Issue Title]

**Severity**: Warning
**Location**: `path/to/file.yml:line`
**Issue**: [Description of the problem]
**Recommendation**: [How to improve]
**Reference**: [AGENTS.md section or ansible-lint rule]

**Example:**
```yaml
# Suggested improvement
```

---

## Suggestions [SUGGESTION]

### [File/Role/Path] - [Improvement Opportunity]

**Severity**: Suggestion
**Location**: `path/to/file.yml`
**Suggestion**: [Enhancement opportunity]
**Benefit**: [Why this would help]

---

## Review Checklist

### Role Structure ✓/X
- [x] Required directories present (tasks/, defaults/, meta/)
- [x] meta/argument_specs.yml exists and complete
- [ ] tasks/validate.yml present [CRITICAL]
- [x] README.md documented
- [x] Handlers directory (if needed)

### Variable Management ✓/X
- [x] All variables in defaults/main.yml
- [x] Variables are data-only
- [ ] External variables validated in tasks/validate.yml [CRITICAL]
- [x] meta/argument_specs.yml complete
- [x] No hardcoded secrets

### Task Design ✓/X
- [x] All tasks named
- [x] Modules use FQCN
- [x] Idempotent design
- [ ] 1 shell command without safeguards [CRITICAL]
- [x] Handlers used appropriately

### Data Transformation ✓/X
- [x] Jinja filters ≤ 4
- [x] Readable expressions
- [x] No complex nested logic

### AAP Patterns ✓/X (if applicable)
- [x] Uses dispatch role
- [x] Proper connection variables
- [x] Dependency-aware ordering
- [x] Environment separation

### ansible-lint ✓/X
- [x] Profile: basic
- [ ] 2 errors to fix [CRITICAL]
- [ ] 1 warning [WARNING]
- [x] Valid YAML syntax

---

## Next Steps

**Priority actions:**
1. [Most critical fix]
2. [Second priority fix]
3. [Third priority fix]

**After critical fixes:**
- [Warning items to address]
- [Documentation improvements]

**Future improvements:**
- [Suggestions for enhancement]

---

## Review Notes

- **Reviewed against**: AGENTS.md (Megalith Development standards)
- **ansible-lint profile**: basic
- **Repository pattern compliance**: [Yes/Partial/No - with details]
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0
- **Review date**: [Date]

```

### Phase 6: Optional ansible-lint Execution

If `--lint` flag provided OR ansible-lint available:

**Check availability:**
```bash
which ansible-lint
```

**If available, execute:**
```bash
ansible-lint [path]
```

**Parse output:**
- Extract rule violations
- Map rule IDs to severity (error → critical, warning → warning, info → suggestion)
- Provide context from AGENTS.md
- Add fix examples where applicable
- Link to ansible-lint documentation

**Integration:**
- Add ansible-lint findings to appropriate severity sections
- Mark with `[ansible-lint]` prefix
- Include rule ID and description
- Provide remediation guidance

**If not available:**
- Note in output that ansible-lint not run
- Suggest installing: `pip install ansible-lint`
- Perform manual checks for common patterns

## Edge Cases & Special Scenarios

### No Ansible Content Found

If no Ansible files detected:
1. Confirm with user: "No Ansible files found. Is this an Ansible repository?"
2. Offer to review specific path: "Please specify a path to review"
3. Check if files in non-standard locations

### Mixed Content Repository

If repository contains both Ansible and non-Ansible content:
1. Focus review on Ansible portions only
2. Note any integration patterns (e.g., scripts called by Ansible)
3. Check if Ansible follows repository standards

### Legacy Code

If reviewing older code that doesn't meet current standards:
1. Note deviations from current best practices
2. Prioritize fixes by severity (critical first)
3. Suggest incremental improvement path
4. Don't require 100% compliance immediately for legacy code
5. Focus on preventing new violations

### AAP Config-as-Code Repository

If `aap_config/` directory detected:
1. Apply AAP-specific patterns from `/aap-config-as-code` skill
2. Check dispatch usage
3. Verify dependency ordering
4. Validate environment structure
5. Check for proper connection variable usage

### No Git Changes

If `git status` shows no changes and no path specified:
1. Ask user: "No changed files detected. What would you like to review?"
2. Suggest options:
   - Specific role: `/ansible-code-review roles/example`
   - Specific playbook: `/ansible-code-review playbooks/site.yml`
   - Full repository: `/ansible-code-review .`
3. Provide summary statistics only unless detailed review requested

### Severity Filtering

If `--severity` flag provided:
1. Perform full review but filter output
2. `--severity critical`: Show only Critical issues
3. `--severity warning`: Show Critical + Warning
4. `--severity all`: Show all findings (default)
5. Always include summary with all counts

### Empty Review (No Issues)

If no issues found:
1. Celebrate! "Excellent! No issues found."
2. Provide complete checklist with all ✓ marks
3. Note compliance level: "Fully compliant with AGENTS.md standards"
4. Optionally suggest future improvements (if any)
5. Keep output concise and positive

## Review Standards Reference

All reviews based on:
- **AGENTS.md**: Repository development standards (authoritative)
- **Red Hat CoP**: https://redhat-cop.github.io/automation-good-practices/
- **ansible-lint**: Configured rules in `.ansible-lint`
- **Repository Patterns**: Established conventions in roles/, playbooks/

## Success Criteria

A clean review passes when:
1. All required role directories and files present
2. Variables properly initialized and validated
3. Tasks named, using FQCN, idempotent
4. No unjustified shell/command usage
5. Jinja complexity within limits
6. AAP patterns followed (if applicable)
7. ansible-lint clean (if run)
8. No hardcoded secrets
9. Documentation complete

## Output Format Specification

**Issue Template:**
```markdown
### [Location] - [Issue Title]

**Severity**: Critical|Warning|Suggestion
**Location**: `path/to/file.yml:line`
**Issue**: [What is wrong]
**Impact**: [Why it matters] (Critical/Warning)
**Fix**: [How to fix] (Critical/Warning)
**Recommendation**: [How to improve] (Warning/Suggestion)
**Benefit**: [Why improve] (Suggestion)
**Reference**: [AGENTS.md § Section or ansible-lint rule]

[Code example if applicable]
```

**Checklist Format:**
```markdown
### Category ✓/X
- [x] Passing check
- [ ] Failing check [CRITICAL] (Critical)
- [ ] Failing check [WARNING] (Warning)
- [x] Passing check
```

## Implementation Notes

- Read files using Read tool, not Bash cat commands
- Use Glob to find Ansible files: `**/*.yml` in relevant directories
- Parse YAML files to extract task names, module usage, variables
- Cross-reference findings against AGENTS.md requirements
- Provide specific line numbers when available
- Include both "bad" and "good" code examples
- Keep output actionable and specific
- Group related findings together
- Prioritize by severity
- Be encouraging when code is clean

## Inspiration & References
Adapted from [@leogallego](https://github.com/leogallego) [Ansible AI Skills] (https://github.com/leogallego/claude-ansible-skills)