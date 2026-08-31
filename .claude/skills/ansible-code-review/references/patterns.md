# Ansible Patterns and Anti-Patterns

Common patterns (good) and anti-patterns (bad) found in Ansible code, with examples and explanations.

## Table of Contents

- [Role Structure Patterns](#role-structure-patterns)
- [Variable Management Patterns](#variable-management-patterns)
- [Task Design Patterns](#task-design-patterns)
- [Module Selection Patterns](#module-selection-patterns)
- [Idempotency Patterns](#idempotency-patterns)
- [Data Transformation Patterns](#data-transformation-patterns)
- [AAP Configuration Patterns](#aap-configuration-patterns)
- [Playbook Patterns](#playbook-patterns)
- [Pattern Detection Rules](#pattern-detection-rules)

---

## Role Structure Patterns

### ✓ Good Pattern: Complete Role Structure

```
roles/webserver/
  tasks/
    main.yml        # Orchestrates imports
    validate.yml    # Validates inputs
    install.yml     # Installation tasks
    configure.yml   # Configuration tasks
    service.yml     # Service management
  defaults/main.yml # All variables initialized
  meta/
    main.yml
    argument_specs.yml  # Schema validation
  handlers/
    main.yml        # Service restart handlers
  templates/
    nginx.conf.j2
  README.md         # Role documentation
```

**Why Good:**
- Complete directory structure
- Clear separation of concerns
- Modular task files
- Proper validation and documentation
- Schema defined in argument_specs.yml

### X Anti-Pattern: Incomplete Role Structure

```
roles/webserver/
  tasks/
    main.yml        # All 500 lines of tasks in one file
  defaults/main.yml
  # Missing: meta/argument_specs.yml
  # Missing: tasks/validate.yml
  # Missing: handlers/
  # Missing: README.md
```

**Why Bad:**
- No input validation
- No schema definition
- No documentation
- Poor maintainability (one huge file)

---

## Variable Management Patterns

### ✓ Good Pattern: Proper Variable Initialization and Validation

**defaults/main.yml:**
```yaml
---
# Webserver configuration
webserver_port: 80
webserver_ssl_enabled: false
webserver_ssl_port: 443
webserver_document_root: /var/www/html

# Service configuration
webserver_service_name: nginx
webserver_service_state: started
webserver_service_enabled: true
```

**tasks/validate.yml:**
```yaml
---
- name: Validate webserver configuration
  ansible.builtin.assert:
    that:
      - webserver_port is defined
      - webserver_port | int > 0
      - webserver_port | int < 65536
      - webserver_document_root is defined
      - webserver_document_root | length > 0
    fail_msg: "Invalid webserver configuration"
    success_msg: "Webserver configuration validated successfully"
```

**meta/argument_specs.yml:**
```yaml
---
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
      webserver_ssl_port:
        type: int
        default: 443
        description: SSL port (if SSL enabled)
      webserver_document_root:
        type: str
        required: true
        description: Web root directory path
```

**Why Good:**
- All variables initialized with sensible defaults
- Input validation with clear error messages
- Schema defined with types and descriptions
- User-facing variables documented

### X Anti-Pattern: No Validation or Schema

**defaults/main.yml:**
```yaml
---
# Incomplete defaults
port: 80
# Missing: many other variables
```

**No tasks/validate.yml**
**No meta/argument_specs.yml**

**tasks/main.yml:**
```yaml
---
- name: Configure webserver
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  # Will fail cryptically if ssl_enabled not defined
```

**Why Bad:**
- Missing validation fails late with unclear errors
- No schema means no IDE support
- Variables not initialized (runtime errors)
- Poor developer experience

---

## Task Design Patterns

### ✓ Good Pattern: Descriptive Task Names with FQCN

```yaml
---
- name: Install nginx web server
  ansible.builtin.package:
    name: nginx
    state: present

- name: Deploy nginx configuration from template
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
    owner: root
    group: root
  notify: Reload nginx

- name: Ensure nginx service is running and enabled
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: yes
```

**Why Good:**
- Descriptive task names (what, not how)
- FQCN used for all modules
- Proper handler usage (notify)
- Idempotent module selection

### X Anti-Pattern: Unclear Names, No FQCN, Inline Restarts

```yaml
---
- name: Install
  package:  # No FQCN
    name: nginx

- name: Copy config
  copy:  # Vague name, no FQCN
    src: nginx.conf
    dest: /etc/nginx/nginx.conf

- name: Restart
  service:  # Inline restart, not via handler
    name: nginx
    state: restarted
```

**Why Bad:**
- Vague task names
- No FQCN (potential namespace collisions)
- Inline service restart (not idempotent)
- No handler usage

---

## Module Selection Patterns

### ✓ Good Pattern: Use Appropriate Modules

```yaml
---
# Good: Use copy module
- name: Deploy configuration file
  ansible.builtin.copy:
    src: app.conf
    dest: /etc/app/app.conf
    mode: '0644'
    owner: root
    group: root

# Good: Use template module
- name: Deploy templated configuration
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/app/app.conf
    mode: '0644'

# Good: Use package module
- name: Install required packages
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - openssl

# Good: Use service module
- name: Ensure service is running
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: yes

# Good: Use file module
- name: Create directory
  ansible.builtin.file:
    path: /var/www/html
    state: directory
    mode: '0755'
```

**Why Good:**
- Uses appropriate modules for each task
- Idempotent and reliable
- Clear intent
- Proper error handling

### X Anti-Pattern: Shell Commands Instead of Modules

```yaml
---
# Bad: Shell instead of copy
- name: Copy file
  shell: cp /tmp/app.conf /etc/app/app.conf

# Bad: Shell instead of template
- name: Update config
  shell: sed -i 's/PORT/8080/' /etc/app/app.conf

# Bad: Shell instead of package
- name: Install packages
  shell: yum install -y nginx openssl

# Bad: Shell instead of service
- name: Start service
  shell: systemctl start nginx && systemctl enable nginx

# Bad: Shell instead of file
- name: Create directory
  shell: mkdir -p /var/www/html && chmod 755 /var/www/html
```

**Why Bad:**
- Not idempotent (runs every time)
- No change detection
- Error-prone
- Platform-dependent
- No proper module features (backup, validation, etc.)

---

## Idempotency Patterns

### ✓ Good Pattern: Idempotent Design with Handlers

```yaml
---
# tasks/main.yml
- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    mode: '0644'
  notify: Reload nginx

- name: Deploy SSL certificate
  ansible.builtin.copy:
    src: server.crt
    dest: /etc/nginx/ssl/server.crt
    mode: '0600'
  notify: Reload nginx

# handlers/main.yml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

**Why Good:**
- Config changes notify handler
- Handler runs once at end (even if multiple notifies)
- Reload only when actually changed
- Idempotent (safe to run multiple times)

### ✓ Good Pattern: Justified Shell with Safeguards

```yaml
---
# Justified use case: No module exists for this operation
- name: Generate SSL certificate with OpenSSL
  ansible.builtin.command: >
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem
    -days 365 -nodes -subj "/CN=example.com"
  args:
    creates: /etc/ssl/private/cert.pem  # Skip if file exists
  # Justification: No ansible module for openssl certificate generation
  # Using creates to ensure idempotency
```

**Why Good:**
- Justification comment explains why
- `creates` ensures idempotency
- Clear purpose

### X Anti-Pattern: Non-Idempotent Operations

```yaml
---
# Bad: Always restarts service
- name: Restart nginx
  ansible.builtin.service:
    name: nginx
    state: restarted  # Always restarts!

# Bad: Shell without safeguards
- name: Configure app
  shell: echo "CONFIG=value" >> /etc/app.conf
  # Appends every run! Not idempotent!

# Bad: Command without changed_when
- name: Update database
  command: /usr/bin/update-db.sh
  # No way to detect if changes occurred
```

**Why Bad:**
- Always shows as changed
- Service restarts unnecessarily
- Config accumulates duplicate lines
- No idempotency safeguards

---

## Data Transformation Patterns

### ✓ Good Pattern: Simple Jinja Filters

```yaml
---
- name: Set application environment
  ansible.builtin.set_fact:
    app_env: "{{ environment | default('dev') | upper }}"

- name: Set configuration values
  ansible.builtin.set_fact:
    config_values: "{{ base_config | combine(override_config) }}"

- name: Extract user names
  ansible.builtin.set_fact:
    user_names: "{{ users | map(attribute='name') | list }}"
```

**Why Good:**
- Clear and readable
- ≤4 filters (within limits)
- Simple transformations
- Easy to understand

### ✓ Good Pattern: Filter Plugin for Complex Logic

**filter_plugins/custom_transforms.py:**
```python
def restructure_inventory(inventory_data):
    """
    Complex data restructuring that would be unreadable in Jinja.
    Transforms nested inventory structure into flat host list.
    """
    result = []
    for group, hosts in inventory_data.items():
        for host in hosts:
            result.append({
                'hostname': host['name'],
                'ip': host['ansible_host'],
                'group': group
            })
    return result

class FilterModule:
    def filters(self):
        return {
            'restructure_inventory': restructure_inventory
        }
```

**Usage:**
```yaml
---
- name: Transform inventory data
  ansible.builtin.set_fact:
    flat_inventory: "{{ inventory_data | restructure_inventory }}"
```

**Why Good:**
- Complex logic in Python (readable, testable)
- Simple usage in playbook
- Reusable across roles
- Can include unit tests

### X Anti-Pattern: Complex Jinja One-Liners

```yaml
---
# Bad: Too many filters, unreadable
- name: Complex transformation
  ansible.builtin.set_fact:
    result: "{{ data | default({}) | dict2items | map('combine', {'new_key': 'value'}) | selectattr('enabled', 'equalto', true) | map(attribute='name') | list | sort | unique }}"
    # 8 filters! Impossible to debug, hard to understand
```

**Why Bad:**
- Too many filters (>4 limit)
- Difficult to read and maintain
- Hard to debug when it fails
- Should be a filter plugin

---

## AAP Configuration Patterns

### ✓ Good Pattern: AAP Configuration as Code with Dispatch

**playbooks/configure_aap.yml:**
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

**aap_config/controller/organizations.yml:**
```yaml
---
controller_organizations:
  - name: Engineering
    description: Engineering organization
    galaxy_credentials:
      - Ansible Galaxy

  - name: Operations
    description: Operations organization
```

**aap_config/controller/credentials.yml:**
```yaml
---
controller_credentials:
  - name: GitHub SCM
    organization: Engineering
    credential_type: Source Control
    inputs:
      username: "{{ vault_github_username }}"
      password: "{{ vault_github_token }}"
```

**Why Good:**
- Uses dispatch role (recommended pattern)
- Configuration as YAML data
- Dependency-aware ordering (orgs before credentials)
- Secrets from vault

### X Anti-Pattern: Raw API Calls, Wrong Order

```yaml
---
- name: Configure AAP (bad way)
  hosts: localhost
  tasks:
    # Bad: Creating job template before project exists
    - name: Create job template
      ansible.builtin.uri:
        url: "https://aap.example.com/api/v2/job_templates/"
        method: POST
        user: admin
        password: "hardcoded_password"  # CRITICAL: Hardcoded secret!
        body_format: json
        body:
          name: Deploy App
          project: 5  # Hardcoded ID, fragile
          inventory: 3
      # Will fail if project doesn't exist (dependency order wrong)

    # Bad: Raw API instead of using dispatch
    - name: Create project
      ansible.builtin.uri:
        url: "https://aap.example.com/api/v2/projects/"
        # ... lots of manual API work
```

**Why Bad:**
- Hardcoded credentials (CRITICAL security issue)
- Wrong dependency order (job template before project)
- Raw API calls (not config-as-code pattern)
- Fragile (hardcoded IDs)
- Not using recommended dispatch pattern

---

## Playbook Patterns

### ✓ Good Pattern: Thin Playbook Using Roles

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

**Why Good:**
- Thin playbook (logic in role)
- Clear purpose
- Reusable role
- Suitable for AAP Job Template

### ✓ Good Pattern: Modular Role Functions

```yaml
---
- name: Create ServiceNow incident
  hosts: localhost
  gather_facts: false

  tasks:
    - name: Create incident in ServiceNow
      ansible.builtin.import_role:
        name: servicenow_incident
        tasks_from: create
```

**Why Good:**
- Uses tasks_from for specific function
- Exposes role "public API"
- Clear action (create)
- Composable

### X Anti-Pattern: Duplicating Role Logic in Playbook

```yaml
---
- name: Deploy web application
  hosts: webservers
  become: yes

  tasks:
    # Bad: 50+ tasks duplicating what should be in a role
    - name: Install packages
      ansible.builtin.package:
        name:
          - nginx
          - python3
          - git

    - name: Create app user
      ansible.builtin.user:
        name: webapp
        system: yes

    - name: Clone repository
      ansible.builtin.git:
        repo: https://github.com/example/app.git
        dest: /opt/webapp

    # ... 47 more tasks that should be in a role
```

**Why Bad:**
- Duplicates logic that should be in role
- Not reusable
- Difficult to maintain
- Violates separation of concerns

---

## Pattern Detection Rules

### When to Create Filter Plugin

Consider creating a custom filter plugin if:

1. **Filter Count Exceeded**
   - Jinja expression has >4 filters (except `json_query`)
   - Example: `{{ data | default({}) | dict2items | map(...) | select(...) | list | sort }}`

2. **Logic Repeated Across Files**
   - Same transformation used in multiple roles/playbooks
   - Should be centralized in `filter_plugins/`

3. **Expression Difficult to Understand**
   - Takes more than 5 seconds to understand
   - Requires inline comment to explain
   - Nested logic that's hard to follow

4. **Complex Data Structure Transformation**
   - Restructuring nested dictionaries
   - Flattening or pivoting data
   - Complex aggregations

5. **Logic Requires Python Libraries**
   - Needs regex, datetime, or other Python stdlib
   - Requires custom algorithms
   - Complex business logic

**Action**: Move to Python filter plugin

### When to Use Shell/Command

Shell/command/raw modules are justified when:

1. **No Appropriate Module Exists**
   - Functionality not available in any Ansible module
   - Third-party tool without Ansible integration
   - Example: `openssl` certificate operations

2. **Module Doesn't Support Required Operation**
   - Module exists but missing needed feature
   - Documented module limitation
   - Example: Complex `awk` text processing

3. **Performance-Critical Operation**
   - Module too slow for use case
   - Documented benchmarking showing need
   - Approved exception

4. **One-Time Migration Task**
   - Temporary task for migration
   - Clearly marked as temporary
   - Plan to remove documented

**Required Safeguards:**
- Justification comment explaining why
- `changed_when` to detect changes accurately
- `failed_when` OR `creates`/`removes` for idempotency
- Consider `check_mode: no` if not check-safe

**Example:**
```yaml
- name: Generate custom SSL certificate with specific parameters
  ansible.builtin.command: >
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem
    -days 365 -nodes -subj "/CN=example.com"
  args:
    creates: /etc/ssl/private/cert.pem
  # Justification: No ansible module supports this specific openssl operation
  # Using creates to ensure idempotency
```

### When to Add Validation

Add `tasks/validate.yml` when role:

1. **Accepts External Variables**
   - From inventory
   - From surveys (AAP)
   - From extra vars
   - From upstream role outputs

2. **Has Complex Variable Requirements**
   - Variables with format constraints
   - Variables with relationship dependencies
   - Variables with business logic validation

3. **Can Fail Cryptically Without Validation**
   - Late failures with unclear error messages
   - Runtime errors that could be caught early
   - Invalid configuration causing service failures

**Example Validation:**
```yaml
---
- name: Validate database configuration
  ansible.builtin.assert:
    that:
      - db_host is defined
      - db_host | length > 0
      - db_port is defined
      - db_port | int >= 1024
      - db_port | int <= 65535
      - db_name is defined
      - db_name is match('^[a-zA-Z][a-zA-Z0-9_]*$')
      - db_user is defined
      - db_password is defined
      - db_password | length >= 12
    fail_msg: "Database configuration validation failed. Check all required variables."
    success_msg: "Database configuration validated successfully."
```

---

## Summary

**Good Patterns:**
- Complete role structure with all required files
- Proper variable initialization, validation, and schema
- Descriptive task names with FQCN
- Appropriate module selection
- Idempotent design with handlers
- Simple Jinja or Python filter plugins
- AAP config-as-code with dispatch
- Thin playbooks using roles

**Anti-Patterns:**
- Incomplete role structure
- No validation or schema
- Shell commands instead of modules
- Non-idempotent operations
- Complex unreadable Jinja
- Raw AAP API calls
- Hardcoded secrets
- Duplicating role logic in playbooks

**Detection Rules:**
- Create filter plugin when: >4 filters, complex logic, or repeated transformations
- Use shell/command only when: justified, with safeguards, and commented
- Add validation when: accepting external vars or complex requirements

For complete standards, see **AGENTS.md** and **Red Hat CoP best practices**.
