# Ansible Code Review Skill

Comprehensive code review for Ansible content based on industry best practices and repository standards.

## What This Skill Does

Performs multi-layer analysis of Ansible code to ensure quality, maintainability, and production-readiness. The review covers:

### Structural Review
- Role and playbook organization
- Required directories and files
- Proper file naming and structure
- Documentation completeness

### Variable Management
- Variable initialization in `defaults/main.yml`
- Input validation in `tasks/validate.yml`
- Schema definition in `meta/argument_specs.yml`
- Secret management (no hardcoded credentials)

### Task Design
- Descriptive task naming
- FQCN (Fully Qualified Collection Names) usage
- Idempotency patterns
- Appropriate module selection
- Handler usage for state changes

### Data Transformation
- Jinja filter complexity limits
- Python filter plugin recommendations
- Readable data manipulation

### AAP Patterns
- Configuration-as-code compliance
- Dispatch role usage
- Dependency-aware ordering
- Environment separation

### Lint Compliance
- ansible-lint rule validation
- YAML best practices
- Naming conventions
- Style consistency

## When to Use

### Use This Skill When:
- **Before committing** - Review changes before commit
- **During PR review** - Validate code quality before merge
- **Refactoring code** - Ensure improvements maintain standards
- **Adding new content** - Verify new roles/playbooks meet requirements
- **Learning** - Understand best practices through examples

### Do NOT Use When:
- Running production playbooks (this is analysis only)
- Looking for runtime errors (use ansible-playbook --check instead)
- Debugging failed executions (use ansible logs instead)

## Invocation

### Automatic Review (Changed Files)
```bash
/ansible-code-review
```
Reviews all Ansible files modified in git working directory.

### Review Specific Targets
```bash
# Review a specific role
/ansible-code-review roles/webserver

# Review a specific playbook
/ansible-code-review playbooks/site.yml

# Review entire directory
/ansible-code-review roles/

# Review specific file
/ansible-code-review roles/example/tasks/main.yml
```

### Filter by Severity
```bash
# Show only critical issues
/ansible-code-review --severity critical

# Show critical + warnings
/ansible-code-review --severity warning

# Show all findings (default)
/ansible-code-review --severity all
```

### Include ansible-lint
```bash
# Run ansible-lint if available
/ansible-code-review --lint

# Combine with other options
/ansible-code-review roles/example --lint --severity warning
```

## Severity Levels

### [CRITICAL] (Blocks Production)

**Issues that should be addressed before deployment**

Examples:
- Missing `meta/argument_specs.yml` for parameterized roles
- Missing `tasks/validate.yml` for roles accepting external variables
- Hardcoded secrets in tracked files
- `shell`/`command`/`raw` modules without safeguards
- Non-idempotent operations without justification
- Breaking AAP dependency order
- AGENTS.md MUST violations

**Action Required:** MUST fix before merge

**Impact:** Security vulnerabilities, runtime failures, or unpredictable behavior in production

### [WARNING] (Should Fix Before Merge)

**Issues that should be addressed before merging**

Examples:
- Missing `README.md` for roles
- Complex Jinja (>4 filters) without filter plugin
- `shell`/`command` without justification comment
- Not using FQCN for modules
- Deprecated module usage
- Service restarts inline instead of via handlers
- Duplicating role logic in playbooks
- AGENTS.md SHOULD violations

**Action Required:** Strongly recommended to fix

**Impact:** Maintainability issues, technical debt, or non-compliance with standards

### [SUGGESTION] (Improvement Opportunities)

**Opportunities for enhancement**

Examples:
- Better variable naming
- More descriptive task names
- Additional task tags
- Code organization improvements
- Documentation enhancements
- Performance optimizations
- Test coverage recommendations

**Action Required:** Consider for future improvements

**Impact:** Enhanced code quality, better developer experience, or improved performance

## Review Standards

Reviews are based on:

### 📘 AGENTS.md
Repository development standards (authoritative for this project)
- Variable management requirements
- Validation patterns
- Role structure standards
- Task design guidelines
- Data transformation rules

### Red Hat CoP
Industry best practices from Red Hat Communities of Practice
- Source: https://redhat-cop.github.io/automation-good-practices/
- Baseline standard for all Ansible development

### ansible-lint
Automated linting rules from .ansible-lint configuration
- Configured profile (basic, moderate, production, etc.)
- Syntax and style rules
- Deprecated module detection
- YAML formatting standards

### Repository Patterns
Established conventions from existing code
- Role naming patterns
- Directory structure
- Variable organization
- Documentation style

## Output Format

Each review includes:

### Summary Section
```markdown
## Summary
- Files reviewed: X
- Critical issues: X
- Warnings: X
- Suggestions: X
- Overall status: Ready/Needs work/Blocked
```

### [CRITICAL] Issues
Detailed findings with:
- **Location**: Exact file and line number
- **Issue**: Clear problem description
- **Impact**: Why this should be addressed
- **Fix**: Specific remediation steps
- **Code examples**: Bad vs Good
- **Reference**: AGENTS.md section or lint rule

### [WARNING] Items
Detailed findings with:
- **Location**: File and line number
- **Issue**: Problem description
- **Recommendation**: How to improve
- **Example**: Suggested code
- **Reference**: Standard reference

### [SUGGESTION] Items
Improvement opportunities with:
- **Location**: File path
- **Suggestion**: Enhancement opportunity
- **Benefit**: Why this helps

### Review Checklist
Categorized pass/fail marks:
- Role Structure ✓/X
- Variable Management ✓/X
- Task Design ✓/X
- Data Transformation ✓/X
- AAP Patterns ✓/X (if applicable)
- ansible-lint ✓/X

### Next Steps
Prioritized action items:
1. Critical fixes (must do)
2. Warning fixes (should do)
3. Suggestions (nice to have)

### Review Notes
Context information:
- AGENTS.md version
- ansible-lint profile
- Repository compliance level
- Review date and version

## Integration with Development Workflow

### Pre-Commit Review
```bash
# Review staged changes before commit
git add .
/ansible-code-review
```

Use to catch issues before they enter version control.

### Pull Request Review
```bash
# Review entire PR changes
/ansible-code-review
```

Validate all changes before merge to ensure quality standards.

### Refactoring Validation
```bash
# Review specific role after refactoring
/ansible-code-review roles/refactored-role
```

Confirm improvements maintain or enhance code quality.

### Learning and Education
```bash
# Review example role to learn patterns
/ansible-code-review roles/common --severity all
```

Understand best practices through detailed feedback and examples.

## Requirements

### Required
- Access to `/AGENTS.md` (repository standards)
- Ansible content to review (roles, playbooks, tasks)

### Optional but Recommended
- `/.ansible-lint` configuration file
- `ansible-lint` tool installed (for automated linting)
- Git repository (for changed file detection)

### Installing ansible-lint
```bash
# If you want to use --lint flag
pip install ansible-lint
```

## Example Review Output

### Clean Code Example
```markdown
# Ansible Code Review: roles/monitoring

## Summary
- Files reviewed: 15
- Critical issues: 0 [CRITICAL]
- Warnings: 0 [WARNING]
- Suggestions: 2 [SUGGESTION]
- Overall status: ✓ Meets all standards

## Review Checklist ✓

All checks passed! Role follows best practices.

### Role Structure ✓
- [x] Complete directory structure
- [x] meta/argument_specs.yml present and complete
- [x] tasks/validate.yml validates inputs
- [x] README.md well documented

### Variable Management ✓
- [x] All variables in defaults/main.yml
- [x] Proper validation logic
- [x] No hardcoded secrets

### Task Design ✓
- [x] All tasks named with FQCN
- [x] Idempotent design throughout
- [x] Handlers used appropriately

## Suggestions [SUGGESTION]

### Consider adding CI/CD testing
**Benefit**: Automated validation on changes

### Consider molecule tests
**Benefit**: Role testing across multiple platforms

---
Excellent work! This role meets all validation standards.
```

### Issues Found Example
```markdown
# Ansible Code Review: roles/webserver

## Summary
- Files reviewed: 8
- Critical issues: 2 [CRITICAL]
- Warnings: 3 [WARNING]
- Suggestions: 1 [SUGGESTION]
- Overall status: [BLOCKED] Blocked - Fix critical issues

---

## Critical Issues [CRITICAL]

### roles/webserver/meta/ - Missing argument_specs.yml

**Severity**: Critical
**Location**: `roles/webserver/meta/`
**Issue**: Role missing meta/argument_specs.yml file
**Impact**: No schema validation, no IDE support, unclear role contract
**Fix**: Create meta/argument_specs.yml with all role parameters
**Reference**: AGENTS.md § Argument Specs

Example:
```yaml
# roles/webserver/meta/argument_specs.yml
argument_specs:
  main:
    short_description: Webserver configuration role
    options:
      webserver_port:
        type: int
        required: true
        description: Port for webserver to listen on
      webserver_ssl_enabled:
        type: bool
        default: false
        description: Enable SSL/TLS
```

---

### roles/webserver/tasks/deploy.yml:23 - Unsafe shell command

**Severity**: Critical
**Location**: `roles/webserver/tasks/deploy.yml:23`
**Issue**: Shell command without changed_when or safeguards
**Impact**: Cannot detect changes, breaks idempotency tracking
**Fix**: Add changed_when or use copy module
**Reference**: AGENTS.md § Command-Based Tasks

**Current code:**
```yaml
- name: Deploy config
  shell: cp /tmp/nginx.conf /etc/nginx/nginx.conf
```

**Fixed code:**
```yaml
- name: Deploy config
  ansible.builtin.copy:
    src: /tmp/nginx.conf
    dest: /etc/nginx/nginx.conf
    mode: '0644'
    backup: yes
```

---

## Warnings [WARNING]

### roles/webserver/tasks/ - Missing validate.yml

**Severity**: Warning
**Location**: `roles/webserver/tasks/`
**Issue**: No tasks/validate.yml file for input validation
**Recommendation**: Create validation task file
**Reference**: AGENTS.md § Validation Pattern

Example:
```yaml
# roles/webserver/tasks/validate.yml
- name: Validate webserver configuration
  ansible.builtin.assert:
    that:
      - webserver_port is defined
      - webserver_port | int > 0
      - webserver_port | int < 65536
    fail_msg: "webserver_port must be between 1 and 65535"
```

---

## Next Steps

**Priority actions (MUST fix):**
1. Create meta/argument_specs.yml with all role variables
2. Replace shell command at deploy.yml:23 with copy module

**After critical fixes (SHOULD fix):**
3. Add tasks/validate.yml for input validation
4. Add README.md documenting role usage

**Future improvements:**
5. Consider adding tests/ directory with test playbook
```

## Tips for Best Results

### 1. Review Early and Often
Run reviews on small changes frequently rather than large batches.

### 2. Fix Critical Issues First
Always address [CRITICAL] Critical issues before [WARNING] Warnings or [SUGGESTION] Suggestions.

### 3. Use Severity Filtering
Focus on urgent issues first with `--severity critical`.

### 4. Learn from Examples
Pay attention to "bad vs good" code examples in findings.

### 5. Check the Checklist
Use the review checklist as a quick quality indicator.

### 6. Reference AGENTS.md
For detailed context on any finding, reference the cited AGENTS.md section.

### 7. Run ansible-lint
Include `--lint` flag for comprehensive automated checking.

### 8. Review Before Committing
Make code review part of your pre-commit workflow.

## Common Findings Explained

### Missing argument_specs.yml
**Why Critical?** Without schema validation, roles can receive invalid input and fail at runtime. Argument specs provide early validation, IDE support, and clear documentation.

**How to Fix:** Create `meta/argument_specs.yml` defining all role parameters with types, requirements, and descriptions.

### Shell Commands Without Safeguards
**Why Critical?** Without `changed_when`, Ansible can't track task changes, breaking idempotency and handlers. This can cause unintended service restarts or missed configuration updates.

**How to Fix:** Add `changed_when`, `failed_when`, `creates`, or `removes` to all shell/command tasks. Or better, use an appropriate module.

### Missing Validation
**Why Warning?** Without validation in `tasks/validate.yml`, roles fail late with cryptic errors instead of early with clear messages. This makes debugging difficult and wastes time.

**How to Fix:** Create `tasks/validate.yml` using `ansible.builtin.assert` to check all required variables, formats, and relationships.

### Complex Jinja Filters
**Why Warning?** Filter chains >4 become hard to read and maintain. They're difficult to debug and prone to errors.

**How to Fix:** Extract complex Jinja to a Python filter plugin in `filter_plugins/` directory.

### Not Using FQCN
**Why Warning?** Short module names (like `copy`) can be ambiguous. FQCN (`ansible.builtin.copy`) is explicit and prevents namespace collisions.

**How to Fix:** Use fully qualified collection names for all modules.

## Troubleshooting

### "No Ansible files found"
**Cause:** No modified files or target path doesn't contain Ansible content.
**Fix:** Specify a path explicitly: `/ansible-code-review roles/example`

### "ansible-lint not available"
**Cause:** ansible-lint tool not installed.
**Fix:** Install with `pip install ansible-lint` or skip with default review (doesn't require lint)

### Too Many Findings
**Cause:** Legacy code or initial review.
**Fix:** Use `--severity critical` to focus on blocking issues first. Address in phases.

### Conflicting Advice
**Cause:** Edge case or context-specific situation.
**Fix:** Refer to AGENTS.md for authoritative guidance or ask for clarification.

## Further Reading

- **SKILL.md**: Complete implementation guide with detailed review logic
- **references/checklist.md**: Quick reference checklist for manual reviews
- **references/patterns.md**: Common patterns and anti-patterns with examples
- **references/examples.md**: Detailed example review outputs
- **AGENTS.md**: Authoritative development standards for this repository
- **Red Hat CoP**: https://redhat-cop.github.io/automation-good-practices/

## Skill Information

- **Version**: 1.0.0
- **Author**: Megalith Development
- **User-Invocable**: Yes (use `/ansible-code-review`)
- **Auto-Trigger**: Can be configured to run on file changes

## Feedback and Improvements

This skill is designed to help you write better Ansible code. If you find:
- False positives (flagged but shouldn't be)
- False negatives (missed but should be flagged)
- Unclear guidance
- Missing patterns

Please provide feedback to improve the skill for everyone.

---

**Ready to review your code?** Run `/ansible-code-review` to get started!
