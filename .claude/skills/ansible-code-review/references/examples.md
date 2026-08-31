# Example Code Review Outputs

Real-world examples of code review outputs showing different scenarios and findings.

## Table of Contents

- [Example 1: Role with Multiple Issues](#example-1-role-with-multiple-issues)
- [Example 2: Playbook with Duplicate Logic](#example-2-playbook-with-duplicate-logic)
- [Example 3: Clean Role (No Issues)](#example-3-clean-role-no-issues)
- [Example 4: AAP Configuration Review](#example-4-aap-configuration-review)
- [Example 5: Quick Review (Critical Only)](#example-5-quick-review-critical-only)

---

## Example 1: Role with Multiple Issues

### Scenario
Reviewing a webserver role that has several common issues including missing validation, unsafe shell commands, and poor documentation.

### Command
```bash
/ansible-code-review roles/webserver
```

### Output

```markdown
# Ansible Code Review: roles/webserver

## Summary
- **Files reviewed**: 8
- **Critical issues** [CRITICAL]: 2
- **Warnings** [WARNING]: 4
- **Suggestions** [SUGGESTION]: 2
- **Overall status**: [BLOCKED] **Blocked** - Fix critical issues before deployment

---

## Critical Issues [CRITICAL]

### roles/webserver/meta/ - Missing argument_specs.yml

**Severity**: Critical
**Location**: `roles/webserver/meta/`
**Issue**: Role missing meta/argument_specs.yml file
**Impact**: No schema validation, no IDE support, unclear role contract. External consumers cannot validate inputs before execution, leading to late failures with cryptic errors.
**Fix**: Create meta/argument_specs.yml with all role parameters
**Reference**: AGENTS.md § Argument Specs

**Example structure:**
```yaml
# roles/webserver/meta/argument_specs.yml
---
argument_specs:
  main:
    short_description: Webserver installation and configuration role
    options:
      webserver_port:
        type: int
        required: true
        description: Port for webserver to listen on
        default: 80
      webserver_ssl_enabled:
        type: bool
        default: false
        description: Enable SSL/TLS for webserver
      webserver_ssl_port:
        type: int
        default: 443
        description: SSL port (if SSL enabled)
      webserver_document_root:
        type: str
        required: true
        description: Web root directory path
        default: /var/www/html
      webserver_service_name:
        type: str
        required: false
        description: Service name for webserver
        default: nginx
```

---

### roles/webserver/tasks/deploy.yml:23 - Unsafe shell command

**Severity**: Critical
**Location**: `roles/webserver/tasks/deploy.yml:23`
**Issue**: Shell command without changed_when or safeguards
**Impact**: Cannot detect changes, breaks idempotency tracking. Task always shows as "changed" even when no actual changes occur. Handlers may trigger unnecessarily, causing service restarts.
**Fix**: Add changed_when or use copy module instead
**Reference**: AGENTS.md § Command-Based Tasks

**Current code:**
```yaml
- name: Deploy config
  shell: cp /tmp/nginx.conf /etc/nginx/nginx.conf
```

**Fixed option 1 (use appropriate module):**
```yaml
- name: Deploy nginx configuration
  ansible.builtin.copy:
    src: /tmp/nginx.conf
    dest: /etc/nginx/nginx.conf
    mode: '0644'
    owner: root
    group: root
    backup: yes
  notify: Reload nginx
```

**Fixed option 2 (if shell required, add safeguards):**
```yaml
- name: Deploy config
  ansible.builtin.shell: cp /tmp/nginx.conf /etc/nginx/nginx.conf
  args:
    creates: /etc/nginx/nginx.conf
  changed_when: false
  # Justification: [explain why copy module cannot be used]
```

---

## Warnings [WARNING]

### roles/webserver/tasks/ - Missing validate.yml

**Severity**: Warning
**Location**: `roles/webserver/tasks/`
**Issue**: No tasks/validate.yml file for input validation
**Recommendation**: Create validation task file to check external variables
**Reference**: AGENTS.md § Validation Pattern

**Why this matters:**
Without validation, the role fails late with cryptic error messages instead of early with clear guidance. This makes debugging difficult and wastes time.

**Example validation file:**
```yaml
# roles/webserver/tasks/validate.yml
---
- name: Validate webserver configuration
  ansible.builtin.assert:
    that:
      - webserver_port is defined
      - webserver_port | int > 0
      - webserver_port | int < 65536
      - webserver_document_root is defined
      - webserver_document_root | length > 0
      - webserver_service_name is defined
    fail_msg: |
      Webserver configuration validation failed.
      Required variables: webserver_port, webserver_document_root, webserver_service_name
    success_msg: "Webserver configuration validated successfully"
```

---

### roles/webserver/ - Missing README.md

**Severity**: Warning
**Location**: `roles/webserver/`
**Issue**: Role has no README.md documentation
**Recommendation**: Create README.md documenting role purpose, variables, and usage
**Reference**: AGENTS.md § Repository Documentation

**Example README structure:**
```markdown
# Webserver Role

Installs and configures nginx webserver.

## Requirements

- Target: RHEL/CentOS 8+
- Privileges: sudo/become required

## Role Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `webserver_port` | Yes | 80 | HTTP port |
| `webserver_ssl_enabled` | No | false | Enable SSL |
| `webserver_document_root` | Yes | /var/www/html | Web root |

## Example Playbook

\`\`\`yaml
- hosts: webservers
  roles:
    - role: webserver
      webserver_port: 8080
      webserver_document_root: /opt/webapp
\`\`\`

## License

MIT
```

---

### roles/webserver/tasks/main.yml:15 - Not using FQCN

**Severity**: Warning
**Location**: `roles/webserver/tasks/main.yml:15`
**Issue**: Module 'package' should use FQCN 'ansible.builtin.package'
**Recommendation**: Use Fully Qualified Collection Name for all modules
**Reference**: AGENTS.md § Task Design

**Current:**
```yaml
- name: Install nginx
  package:  # No FQCN
    name: nginx
```

**Fixed:**
```yaml
- name: Install nginx web server
  ansible.builtin.package:  # With FQCN
    name: nginx
    state: present
```

**Why FQCN matters:**
- Explicit and unambiguous
- Prevents namespace collisions
- Required for ansible-lint compliance
- Improves code clarity

---

### roles/webserver/tasks/service.yml:8 - Inline service restart

**Severity**: Warning
**Location**: `roles/webserver/tasks/service.yml:8`
**Issue**: Service restarted inline instead of via handler
**Recommendation**: Use handler with notify for idempotency
**Reference**: AGENTS.md § Idempotency

**Current:**
```yaml
- name: Update config
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf

- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted  # Always restarts!
```

**Fixed:**
```yaml
# In tasks/main.yml
- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: Reload nginx

# In handlers/main.yml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded  # Only when notified
```

---

## Suggestions [SUGGESTION]

### roles/webserver/defaults/main.yml - Consider grouping variables

**Severity**: Suggestion
**Location**: `roles/webserver/defaults/main.yml`
**Suggestion**: Group related variables with comments for better organization
**Benefit**: Improves readability and maintainability, makes it easier to find and understand related configuration

**Current:**
```yaml
---
webserver_port: 80
webserver_ssl_enabled: false
webserver_ssl_port: 443
webserver_document_root: /var/www/html
webserver_service_name: nginx
webserver_service_state: started
```

**Suggested:**
```yaml
---
# Network configuration
webserver_port: 80
webserver_ssl_enabled: false
webserver_ssl_port: 443

# Service configuration
webserver_service_name: nginx
webserver_service_state: started
webserver_service_enabled: true

# Application configuration
webserver_document_root: /var/www/html
webserver_user: nginx
webserver_group: nginx
```

---

### roles/webserver/ - Consider adding molecule tests

**Severity**: Suggestion
**Location**: `roles/webserver/`
**Suggestion**: Add molecule test framework for automated role testing
**Benefit**: Automated testing across multiple platforms, catch issues before production, improve confidence in changes

**Example structure:**
```
roles/webserver/
  molecule/
    default/
      molecule.yml
      converge.yml
      verify.yml
```

---

## Review Checklist

### Role Structure ✓/X
- [x] Required directories present (tasks/, defaults/, meta/)
- [ ] meta/argument_specs.yml exists and complete [CRITICAL]
- [ ] tasks/validate.yml present [WARNING]
- [ ] README.md documented [WARNING]
- [x] Handlers directory exists
- [x] Templates directory exists

### Variable Management ✓/X
- [x] All variables in defaults/main.yml
- [x] Variables are data-only
- [ ] External variables validated in tasks/validate.yml [WARNING]
- [ ] meta/argument_specs.yml complete [CRITICAL]
- [x] No hardcoded secrets

### Task Design ✓/X
- [x] All tasks named
- [ ] Modules use FQCN [WARNING]
- [x] Generally idempotent design
- [ ] 1 shell command without safeguards [CRITICAL]
- [ ] Service restart inline instead of handler [WARNING]

### Data Transformation ✓/X
- [x] Jinja filters ≤ 4
- [x] Readable expressions
- [x] No complex nested logic

### AAP Patterns ✓/X
- [N/A] Not an AAP configuration role

### ansible-lint ✓/X
- [x] Profile: basic
- [ ] ansible-lint not run (--lint flag not provided)
- [x] Valid YAML syntax (manual check)

---

## Next Steps

**Priority actions (MUST fix before deployment):**
1. Create `meta/argument_specs.yml` with all role variables and types
2. Replace shell command at `deploy.yml:23` with `ansible.builtin.copy` module

**After critical fixes (SHOULD fix before merge):**
3. Add `tasks/validate.yml` for input validation
4. Create `README.md` documenting role usage and variables
5. Update all modules to use FQCN (ansible.builtin.*)
6. Move service restart to handler with notify pattern

**Future improvements (consider for next iteration):**
7. Group variables in defaults/main.yml with comments
8. Add molecule tests for automated testing

---

## Review Notes

- **Reviewed against**: AGENTS.md (Megalith Development standards)
- **ansible-lint profile**: basic (from .ansible-lint)
- **Repository pattern compliance**: Partial - missing validation and documentation
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0
- **Review date**: 2026-08-24

**Recommendation**: Address 2 critical issues before deployment. The role is structurally sound but needs validation and documentation improvements for production use.
```

---

## Example 2: Playbook with Duplicate Logic

### Scenario
Reviewing a playbook that duplicates role logic instead of using roles properly.

### Command
```bash
/ansible-code-review playbooks/deploy_app.yml
```

### Output

```markdown
# Ansible Code Review: playbooks/deploy_app.yml

## Summary
- **Files reviewed**: 1
- **Critical issues** [CRITICAL]: 0
- **Warnings** [WARNING]: 1
- **Suggestions** [SUGGESTION]: 1
- **Overall status**: [WARNING] **Needs improvement** - Refactor recommended

---

## Warnings [WARNING]

### playbooks/deploy_app.yml:10-65 - Duplicate role logic in playbook

**Severity**: Warning
**Location**: `playbooks/deploy_app.yml:10-65`
**Issue**: Playbook contains 55+ tasks duplicating functionality that should be in a role
**Recommendation**: Extract tasks to a role and call via import_role
**Reference**: AGENTS.md § Role Calling Pattern

**Why this matters:**
- Not reusable across playbooks
- Difficult to maintain and test
- Violates separation of concerns
- Cannot be called from AAP with tasks_from

**Current approach (anti-pattern):**
```yaml
---
- name: Deploy web application
  hosts: webservers
  become: yes
  tasks:
    - name: Install packages
      ansible.builtin.package:
        name:
          - nginx
          - python3-pip
          - git
          - postgresql-client

    - name: Create application user
      ansible.builtin.user:
        name: webapp
        system: yes
        home: /opt/webapp

    - name: Clone application repository
      ansible.builtin.git:
        repo: https://github.com/example/webapp.git
        dest: /opt/webapp/app

    # ... 52 more tasks ...
```

**Recommended approach:**
```yaml
---
- name: Deploy web application
  hosts: webservers
  become: yes
  tasks:
    - name: Deploy web application
      ansible.builtin.import_role:
        name: deploy_webapp
```

**Create role:** `roles/deploy_webapp/`

This provides:
- ✓ Reusability across playbooks
- ✓ Easier testing with molecule
- ✓ Better organization and maintainability
- ✓ Can be called from AAP with specific tasks_from

---

## Suggestions [SUGGESTION]

### playbooks/deploy_app.yml:5 - Consider renaming playbook

**Severity**: Suggestion
**Location**: `playbooks/deploy_app.yml:5`
**Suggestion**: Rename playbook to match AAP convention (e.g., `create_deploy_webapp.yml`)
**Benefit**: Clearer purpose for AAP Job Templates, follows repository naming pattern

**Current:** `deploy_app.yml`
**Suggested:** `create_deploy_webapp.yml` or `service_deploy_webapp.yml`

---

## Review Checklist

### Playbook Structure ✓/X
- [x] Clear play name
- [x] Proper hosts specification
- [x] Valid YAML structure
- [ ] Uses roles instead of duplicating logic [WARNING]

### Task Design ✓/X
- [x] All tasks named
- [x] Modules use FQCN
- [x] Idempotent design

---

## Next Steps

**Recommended actions:**
1. Extract 55+ tasks to `roles/deploy_webapp/`
2. Update playbook to call role via import_role
3. Consider renaming playbook for AAP convention
4. Add role documentation (README.md)
5. Add meta/argument_specs.yml to new role

---

## Review Notes

- **Reviewed against**: AGENTS.md (Megalith Development standards)
- **ansible-lint**: Not run (--lint flag not provided)
- **Repository pattern compliance**: Partial - playbook should use role pattern
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0

**Recommendation**: Refactor to use role pattern for better maintainability and reusability.
```

---

## Example 3: Clean Role (No Issues)

### Scenario
Reviewing a well-structured role that follows all best practices.

### Command
```bash
/ansible-code-review roles/monitoring
```

### Output

```markdown
# Ansible Code Review: roles/monitoring

## Summary
- **Files reviewed**: 15
- **Critical issues** [CRITICAL]: 0
- **Warnings** [WARNING]: 0
- **Suggestions** [SUGGESTION]: 2
- **Overall status**: ✓ **Excellent** - Meets all standards!

---

## Review Checklist ✓

**All checks passed!** This role follows best practices and meets all validation standards.

### Role Structure ✓
- [x] Complete directory structure
- [x] tasks/ with modular organization (main, validate, install, configure, service)
- [x] defaults/main.yml with all variables initialized
- [x] meta/main.yml properly configured
- [x] meta/argument_specs.yml present and complete
- [x] tasks/validate.yml validates external inputs
- [x] README.md well documented with examples
- [x] handlers/main.yml for service management

### Variable Management ✓
- [x] All variables initialized in defaults/main.yml
- [x] Variables are data-only
- [x] External variables validated in tasks/validate.yml
- [x] meta/argument_specs.yml defines all variables with types and descriptions
- [x] Appropriate validators used (choices, ranges)
- [x] No hardcoded secrets

### Task Design ✓
- [x] All tasks have descriptive names
- [x] All modules use FQCN (ansible.builtin.*)
- [x] Idempotent design throughout
- [x] No unjustified shell/command usage
- [x] Handlers used for service restarts
- [x] Proper use of when, loop, notify, tags

### Data Transformation ✓
- [x] Jinja filters ≤ 4 (clean and readable)
- [x] No complex nested logic
- [x] Clear variable expressions

### Documentation ✓
- [x] README.md complete with:
  - Role purpose and requirements
  - Variable documentation
  - Usage examples
  - Dependencies listed
  - License information
- [x] Tasks have clear names explaining purpose
- [x] Complex logic includes comments

### ansible-lint ✓
- [x] Valid YAML syntax
- [x] No deprecated modules
- [x] Consistent naming conventions
- [x] Proper indentation

---

## Suggestions [SUGGESTION]

### Consider adding integration tests

**Severity**: Suggestion
**Location**: `roles/monitoring/`
**Suggestion**: Add molecule integration tests for multiple platforms
**Benefit**: Automated testing across different OS versions, catch platform-specific issues

**Example:**
```
roles/monitoring/
  molecule/
    default/
      molecule.yml      # Test configuration
      converge.yml      # Test playbook
      verify.yml        # Verification tests
```

---

### Consider adding example playbooks

**Severity**: Suggestion
**Location**: `roles/monitoring/`
**Suggestion**: Add examples/ directory with common use case playbooks
**Benefit**: Helps users get started quickly, documents real-world usage patterns

**Example:**
```
roles/monitoring/
  examples/
    basic-monitoring.yml
    advanced-monitoring.yml
    multi-tier-monitoring.yml
```

---

## Highlights

### Excellent Practices Observed

**1. Comprehensive Validation**
```yaml
# tasks/validate.yml
- name: Validate monitoring configuration
  ansible.builtin.assert:
    that:
      - monitoring_port is defined
      - monitoring_port | int >= 1024
      - monitoring_port | int <= 65535
      - monitoring_data_retention | int > 0
      - monitoring_alert_email is match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    fail_msg: "Monitoring configuration validation failed"
    success_msg: "Monitoring configuration validated"
```

**2. Complete Argument Specs**
```yaml
# meta/argument_specs.yml
argument_specs:
  main:
    short_description: Monitoring system installation and configuration
    options:
      monitoring_port:
        type: int
        required: true
        description: Monitoring web interface port
      monitoring_data_retention:
        type: int
        default: 30
        description: Days to retain monitoring data
      monitoring_alert_email:
        type: str
        required: true
        description: Email address for alerts
```

**3. Modular Task Organization**
```
tasks/
  main.yml        # Orchestrates all imports
  validate.yml    # Input validation
  install.yml     # Package installation
  configure.yml   # Configuration deployment
  service.yml     # Service management
```

**4. Proper Handler Usage**
```yaml
# Tasks notify handlers
- name: Deploy monitoring configuration
  ansible.builtin.template:
    src: monitoring.conf.j2
    dest: /etc/monitoring/monitoring.conf
  notify: Restart monitoring service

# Handlers handle restarts
- name: Restart monitoring service
  ansible.builtin.service:
    name: monitoring
    state: restarted
```

---

## Review Notes

- **Reviewed against**: AGENTS.md (Megalith Development standards)
- **ansible-lint profile**: basic (from .ansible-lint)
- **Repository pattern compliance**: ✓ Full compliance
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0
- **Review date**: 2026-08-24

**Overall Assessment:**
Excellent work! This role demonstrates mastery of Ansible best practices. The code is clean, well-documented, properly validated, and meets all validation standards. The suggestions provided are minor enhancements that would make an already-great role even better.

**Key Strengths:**
- Complete validation and schema definition
- Modular and maintainable structure
- Comprehensive documentation
- Idempotent and reliable design
- No security issues

**Suitable for:**
- ✓ Deployment consideration
- ✓ Sharing as reference implementation
- ✓ Use in AAP Job Templates

Keep up the great work! 
```

---

## Example 4: AAP Configuration Review

### Scenario
Reviewing AAP configuration-as-code implementation.

### Command
```bash
/ansible-code-review playbooks/configure_aap.yml
```

### Output

```markdown
# Ansible Code Review: playbooks/configure_aap.yml

## Summary
- **Files reviewed**: 1 playbook + 5 config files
- **Critical issues** [CRITICAL]: 0
- **Warnings** [WARNING]: 0
- **Suggestions** [SUGGESTION]: 1
- **Overall status**: ✓ **Excellent** - Follows AAP config-as-code best practices

---

## Review Checklist ✓

### AAP Configuration Patterns ✓
- [x] Uses infra.aap_configuration.dispatch role
- [x] Configuration files in aap_config/ directory
- [x] Proper connection variables defined
- [x] Dependency-aware object ordering
- [x] No hardcoded credentials
- [x] Environment separation structure ready

### Playbook Structure ✓
- [x] Clear play name
- [x] Proper hosts (localhost)
- [x] Uses include_vars for config loading
- [x] Uses include_role for dispatch
- [x] Thin playbook (config in separate files)

---

## Highlights

**Excellent AAP Config-as-Code Implementation**

**Playbook Structure:**
```yaml
---
- name: Configure Ansible Automation Platform
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Load AAP configuration variables
      ansible.builtin.include_vars:
        dir: ../aap_config
        extensions:
          - yml
          - yaml

    - name: Apply AAP configuration
      ansible.builtin.include_role:
        name: infra.aap_configuration.dispatch
```

**Configuration Structure:**
```
aap_config/
  controller/
    organizations.yml          # Organizations first (dependency order)
    credentials.yml            # Then credentials
    projects.yml               # Then projects
    inventories.yml            # Then inventories
    job_templates.yml          # Finally job templates
  eda/
    rulebook_activations.yml
```

**Proper Dependency Ordering:**
1. Organizations → 2. Credentials → 3. Projects → 4. Inventories → 5. Job Templates

**Secret Management:**
- Connection credentials from environment/vault
- No hardcoded secrets in config files
- Uses {{ vault_* }} variables

---

## Suggestions [SUGGESTION]

### Consider environment separation

**Severity**: Suggestion
**Location**: `aap_config/`
**Suggestion**: Organize configuration by environment (dev/prod/qa) for multi-environment deployments
**Benefit**: Clearer separation, easier environment-specific configuration management

**Current:**
```
aap_config/
  controller/
    organizations.yml
    credentials.yml
```

**Suggested for multi-environment:**
```
aap_config/
  dev/
    controller/
      organizations.yml
      credentials.yml
  prod/
    controller/
      organizations.yml
      credentials.yml
  qa/
    controller/
      organizations.yml
      credentials.yml
```

**Or use variable prefixes:**
```yaml
# aap_config/controller/organizations.yml
dev_controller_organizations:
  - name: Dev Engineering

prod_controller_organizations:
  - name: Prod Engineering
```

---

## Review Notes

- **Reviewed against**: AGENTS.md § AAP Configuration as Code
- **Pattern**: infra.aap_configuration.dispatch (recommended)
- **Repository pattern compliance**: ✓ Full compliance
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0

**Overall Assessment:**
Excellent AAP configuration-as-code implementation! Follows all recommended patterns from the aap-config-as-code skill. Uses dispatch role, proper dependency ordering, and good secret management.

**Suitable for:**
- ✓ Multi-environment AAP deployment
- ✓ Configuration versioning and CI/CD
- ✓ Team collaboration on AAP config
```

---

## Example 5: Quick Review (Critical Only)

### Scenario
Quick review focusing only on blocking issues.

### Command
```bash
/ansible-code-review roles/database --severity critical
```

### Output

```markdown
# Ansible Code Review: roles/database
**Severity Filter**: Critical only

## Summary
- **Files reviewed**: 7
- **Critical issues** [CRITICAL]: 1
- **Overall status**: [BLOCKED] **Blocked** - Fix critical issue before deployment

---

## Critical Issues [CRITICAL]

### roles/database/defaults/main.yml:15 - Hardcoded database password

**Severity**: Critical
**Location**: `roles/database/defaults/main.yml:15`
**Issue**: Database password hardcoded in defaults file
**Impact**: SECURITY VIOLATION - Credentials in version control, accessible to anyone with repository access
**Fix**: Move to Ansible Vault or AAP credentials immediately
**Reference**: AGENTS.md § Variable Management, Security Best Practices

**Current code:**
```yaml
---
db_host: localhost
db_port: 5432
db_name: production
db_user: admin
db_password: "SuperSecret123!"  # [CRITICAL] CRITICAL: Hardcoded secret
```

**Fixed code:**
```yaml
---
db_host: localhost
db_port: 5432
db_name: production
db_user: admin
db_password: "{{ vault_db_password }}"  # From vault or AAP credential
```

**Steps to fix:**

1. **Remove hardcoded password from defaults/main.yml**
2. **Create vault file:**
   ```bash
   ansible-vault create group_vars/all/vault.yml
   ```
3. **Add password to vault:**
   ```yaml
   vault_db_password: "SuperSecret123!"
   ```
4. **Update defaults to reference vault variable:**
   ```yaml
   db_password: "{{ vault_db_password }}"
   ```

**For AAP:**
- Create credential of type "Machine" or custom type
- Reference in Job Template
- No vault file needed (AAP manages credentials)

---

## Next Steps

**CRITICAL - Must fix immediately:**
1. Remove hardcoded password from `defaults/main.yml:15`
2. Move to Ansible Vault or AAP credential store
3. Verify password removed from git history: `git log -p -- defaults/main.yml`
4. Consider rotating the password (now exposed in version control)

**After fix:**
- Run full review: `/ansible-code-review roles/database`

---

## Review Notes

- **Severity filter**: Critical only (use `--severity all` for complete review)
- **Security issue detected**: Yes - hardcoded credentials
- **Reviewed by**: Claude Code ansible-code-review skill v1.0.0

[WARNING] **WARNING**: This repository may contain exposed credentials in git history. Consider:
- Rotating the exposed password immediately
- Reviewing git history: `git log -p -- defaults/main.yml`
- Using tools like `git-secrets` or `truffleHog` to scan for other exposed secrets
```

---

## Summary

These examples demonstrate:

1. **Multi-issue role review** - Shows critical, warnings, and suggestions with detailed remediation
2. **Playbook anti-pattern** - Identifies duplicate logic and recommends role extraction
3. **Clean code recognition** - Celebrates excellent implementation with positive feedback
4. **AAP configuration** - Validates config-as-code patterns and best practices
5. **Filtered review** - Focuses on critical blocking issues for quick triage

**Key Takeaways:**
- Reviews are detailed and actionable
- Code examples show bad vs good patterns
- Severity classification helps prioritize fixes
- Positive feedback when code is excellent
- References to AGENTS.md and standards for context
- Clear next steps for remediation

For more examples and patterns, see:
- **SKILL.md**: Complete review logic
- **patterns.md**: Common patterns and anti-patterns
- **checklist.md**: Quick reference checklist
