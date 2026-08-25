# Ansible Code Review Checklist

Quick reference for manual code reviews. Use this checklist to verify Ansible content meets repository standards.

## Role Structure

### Required Directories
- [ ] `tasks/` directory exists
- [ ] `defaults/` directory exists
- [ ] `meta/` directory exists

### Recommended Directories
- [ ] `handlers/` directory (if service management tasks)
- [ ] `vars/` directory (for internal role variables)
- [ ] `templates/` or `files/` directory (if deploying configs)
- [ ] `tests/` directory (for molecule tests)

### Required Files
- [ ] `tasks/main.yml` exists
- [ ] `defaults/main.yml` exists and contains all variables
- [ ] `meta/main.yml` exists with proper galaxy_info
- [ ] `meta/argument_specs.yml` exists with complete specs
- [ ] `tasks/validate.yml` exists (for roles accepting external vars)

### Recommended Files
- [ ] `README.md` documents role purpose and usage
- [ ] `handlers/main.yml` (if state changes occur)
- [ ] Example playbook in role or `examples/` directory

### File Naming
- [ ] Task files use clear, action-based names (install.yml, configure.yml, service.yml)
- [ ] Template files end in `.j2`
- [ ] Variable files follow purpose-based naming

---

## Variable Management

### Initialization
- [ ] All variables initialized in `defaults/main.yml`
- [ ] Variables are data-only (no embedded logic)
- [ ] Variables use clear, descriptive names (snake_case)
- [ ] Related variables grouped with comments
- [ ] Default values are sensible and safe

### Validation
- [ ] External variables validated in `tasks/validate.yml`
- [ ] Validation uses `ansible.builtin.assert`
- [ ] Assert statements have clear `fail_msg`
- [ ] Assert statements have informative `success_msg`
- [ ] Required variables checked for defined status
- [ ] Format constraints validated (e.g., port ranges, valid choices)
- [ ] Relationship checks between variables
- [ ] Validation fails fast with clear error messages

### Argument Specs
- [ ] `meta/argument_specs.yml` exists
- [ ] All entry points defined (main, and any tasks_from callables)
- [ ] All required variables declared
- [ ] All optional variables declared with defaults
- [ ] Variable types specified (str, int, bool, list, dict, etc.)
- [ ] Descriptions provided for user-facing variables
- [ ] Appropriate validators used:
  - [ ] `choices` for enumerated values
  - [ ] `min` / `max` for numeric ranges
  - [ ] `regex` for format validation
  - [ ] `required` for mandatory parameters

### Secret Management
- [ ] No hardcoded passwords in tracked files
- [ ] No hardcoded API keys or tokens
- [ ] No hardcoded credentials of any kind
- [ ] Secrets use Ansible Vault or AAP credentials
- [ ] No suspicious base64-encoded strings in plain text
- [ ] Sensitive variables clearly marked (e.g., `no_log: true`)

---

## Task Design

### Naming
- [ ] All tasks have descriptive names
- [ ] Task names describe what's being done, not how
- [ ] Task names are concise but clear
- [ ] Consistent naming style across all tasks

### Module Selection
- [ ] All modules use FQCN (Fully Qualified Collection Names)
  - Good: `ansible.builtin.copy`, `ansible.builtin.service`
  - Bad: `copy`, `service`
- [ ] Appropriate modules used instead of shell/command:
  - [ ] `ansible.builtin.copy` instead of `shell: cp`
  - [ ] `ansible.builtin.template` instead of `shell: sed`
  - [ ] `ansible.builtin.package` instead of `shell: yum install`
  - [ ] `ansible.builtin.service` instead of `shell: systemctl`
  - [ ] `ansible.builtin.file` instead of `shell: mkdir`
  - [ ] `ansible.builtin.lineinfile` instead of `shell: echo >>`

### Shell/Command/Raw Module Usage
- [ ] Usage is justified (no appropriate module exists)
- [ ] Includes justification comment explaining why
- [ ] Has `changed_when` defined
- [ ] Has `failed_when` OR `creates` / `removes`
- [ ] Registers output for debugging
- [ ] Uses `args.creates` or `args.removes` when appropriate

### Idempotency
- [ ] All tasks aim to be idempotent
- [ ] Tasks can be run multiple times safely
- [ ] State changes trigger handlers, not inline actions
- [ ] Service restarts use handlers with `notify`
- [ ] Check mode (`--check`) works where possible

### Control Structures
- [ ] `when` conditions are clear and readable
- [ ] Uses `loop` instead of deprecated `with_items`
- [ ] `notify` references handlers for state changes
- [ ] `tags` applied for selective execution (if needed)
- [ ] `become` used appropriately (not globally unless necessary)
- [ ] `delegate_to` used correctly (if needed)

### Error Handling
- [ ] `failed_when` used for custom failure conditions
- [ ] `changed_when` used for accurate change detection
- [ ] `ignore_errors` used sparingly and justified
- [ ] `block` / `rescue` used for error recovery (if needed)

### No Deprecated Syntax
- [ ] No deprecated modules (check ansible-lint output)
- [ ] Uses `loop` instead of `with_*` (except with_fileglob)
- [ ] No bare variables in `when` conditions (use `is defined`)
- [ ] Uses `true`/`false` or `yes`/`no` consistently (not mixed)

---

## Data Transformation

### Jinja Filter Usage
- [ ] Jinja filter chains ≤ 4 (except `json_query`)
- [ ] `json_query` used for complex data extraction
- [ ] No overly complex nested logic
- [ ] Expressions are readable and maintainable
- [ ] No complex one-liners that obscure intent

### Complex Transformations
- [ ] Complex data restructuring uses Python filter plugins
- [ ] Filter plugins located in `filter_plugins/` directory
- [ ] Filters are focused and reusable
- [ ] Filter names are clear and descriptive
- [ ] Complex filters have unit tests (recommended)

### When to Create Filter Plugin
Consider creating a filter plugin if:
- [ ] Jinja expression has >4 filters (except json_query)
- [ ] Logic is repeated across multiple files
- [ ] Expression is difficult to understand or maintain
- [ ] Complex data structure transformation is needed
- [ ] Logic requires Python libraries or complex operations

---

## AAP Patterns (if applicable)

### AAP Configuration as Code
- [ ] Uses `infra.aap_configuration.dispatch` role (if config-as-code)
- [ ] Configuration files in `aap_config/` directory
- [ ] Variables organized by AAP component:
  - [ ] `aap_config/controller/` for Controller objects
  - [ ] `aap_config/hub/` for Hub objects
  - [ ] `aap_config/eda/` for EDA objects
  - [ ] `aap_config/gateway/` for Gateway objects

### Connection Variables
- [ ] Proper connection variables defined:
  - [ ] `aap_hostname` or `controller_hostname`
  - [ ] `aap_token` or `controller_token`
  - [ ] `aap_validate_certs` or `controller_validate_certs`
- [ ] Connection credentials NOT hardcoded
- [ ] Credentials use AAP credentials or Ansible Vault

### Dependency Ordering
- [ ] Objects created in dependency-aware order:
  1. Organizations
  2. Credentials
  3. Projects
  4. Inventories
  5. Job Templates
  6. Workflow Job Templates
- [ ] Understand natural dependencies between AAP objects
- [ ] Parent objects created before children

### Environment Separation
- [ ] Multi-environment configs use directory structure OR variable prefixes
- [ ] Clear separation between dev/prod/qa environments
- [ ] Environment-specific variables clearly marked
- [ ] Wildcard variable aggregation used appropriately

### AAP-Targeted Roles
- [ ] Entry point playbooks call roles via `import_role` / `include_role`
- [ ] Uses `tasks_from` for modular role functions
- [ ] Playbooks are thin (expose role functions to AAP Job Templates)
- [ ] Playbook names describe operations (create_*, update_*, service_*)
- [ ] No duplication of role logic in playbooks

---

## Documentation

### Role Documentation
- [ ] `README.md` exists and is complete
- [ ] README explains role purpose
- [ ] README shows usage examples
- [ ] README lists all variables with descriptions
- [ ] README documents requirements/dependencies
- [ ] README includes example playbook

### Code Comments
- [ ] Complex tasks have explanatory comments
- [ ] Shell/command usage justified with comments
- [ ] Non-obvious logic explained
- [ ] TODO/FIXME items tracked (if any)

### Argument Specs
- [ ] All variables have descriptions in `argument_specs.yml`
- [ ] Descriptions are clear and user-friendly
- [ ] Examples provided where helpful
- [ ] Constraints documented

---

## ansible-lint Compliance

### Syntax and Structure
- [ ] No YAML syntax errors
- [ ] Proper indentation (2 spaces)
- [ ] No trailing whitespace
- [ ] Consistent YAML formatting
- [ ] No tabs (spaces only)

### Modules and Tasks
- [ ] All tasks have names
- [ ] No deprecated modules
- [ ] No bare variables (use `{{ }}`)
- [ ] Proper FQCN usage
- [ ] No risky file permissions (e.g., `mode: "0777"`)

### Variables and Values
- [ ] Consistent truthy values (yes/no or true/false, not mixed)
- [ ] Variable names follow conventions (snake_case)
- [ ] No leading underscores in variable names
- [ ] No dots in variable names
- [ ] Boolean values properly quoted or unquoted

### Best Practices
- [ ] No command modules without changed_when
- [ ] No raw modules without justification
- [ ] Proper use of `become`
- [ ] No `ignore_errors` without justification
- [ ] Handlers only notified, not directly called

---

## Playbook-Specific Checks

### Structure
- [ ] Clear play names
- [ ] Proper hosts specification
- [ ] `gather_facts` set appropriately (true/false)
- [ ] Proper YAML structure

### Role Usage
- [ ] Uses `import_role` or `include_role` vs duplicating logic
- [ ] Playbooks are thin (logic in roles, not playbooks)
- [ ] Clear task organization
- [ ] Role dependencies in playbook vs meta/main.yml

### Variables
- [ ] Variables defined appropriately (play vars vs inventory)
- [ ] No variable name collisions
- [ ] Precedence understood and used correctly

### AAP Integration
- [ ] Action-specific naming (e.g., `create_resource.yml`)
- [ ] Suitable for AAP Job Template targeting
- [ ] Uses `tasks_from` when calling modular role functions

---

## Testing and Validation

### Syntax Checks
- [ ] Passes `ansible-playbook --syntax-check`
- [ ] Passes `yamllint` (if configured)
- [ ] Passes `ansible-lint` (if configured)

### Check Mode
- [ ] Runs in check mode (`--check`) without errors
- [ ] Check mode provides useful information
- [ ] Tasks marked with `check_mode: no` only when necessary

### Test Playbooks
- [ ] Role includes test playbook in `tests/` or `molecule/`
- [ ] Tests cover key scenarios
- [ ] Tests are idempotent

---

## Security Checks

### Secrets
- [ ] No hardcoded secrets
- [ ] Sensitive data uses Ansible Vault
- [ ] `no_log: true` on tasks handling secrets
- [ ] Credentials from AAP credential store (if AAP)

### File Permissions
- [ ] Appropriate file permissions (not overly permissive)
- [ ] Avoid `mode: "0777"` or `mode: "0666"`
- [ ] Use minimal necessary permissions

### Command Injection
- [ ] Shell commands properly escaped
- [ ] User input validated before use in commands
- [ ] Avoid string interpolation in shell commands

---

## Quick Pass/Fail Reference

### Automatic FAIL if:
- [CRITICAL] Missing `meta/argument_specs.yml` (for parameterized roles)
- [CRITICAL] Missing `tasks/validate.yml` (for roles accepting external vars)
- [CRITICAL] Hardcoded secrets found
- [CRITICAL] shell/command/raw without safeguards
- [CRITICAL] Non-idempotent operations without justification
- [CRITICAL] ansible-lint errors

### Strong WARNING if:
- [WARNING] Missing `README.md`
- [WARNING] Complex Jinja (>4 filters) without filter plugin
- [WARNING] shell/command without justification comment
- [WARNING] Not using FQCN
- [WARNING] Deprecated modules
- [WARNING] Missing task names

### SUGGESTION for:
- [SUGGESTION] Better variable naming
- [SUGGESTION] More descriptive task names
- [SUGGESTION] Additional tags
- [SUGGESTION] Documentation enhancements
- [SUGGESTION] Test coverage

---

## Summary

Use this checklist to ensure your Ansible content meets quality standards. For detailed guidance on any item, refer to:

- **SKILL.md**: Complete review logic and workflows
- **AGENTS.md**: Authoritative development standards
- **patterns.md**: Common patterns and anti-patterns
- **examples.md**: Example review outputs

**Target**: All required items checked, most recommended items checked, no critical issues.
