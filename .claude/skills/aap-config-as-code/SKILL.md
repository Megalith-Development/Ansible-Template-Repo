---
name: aap-config-as-code
description: Implements Ansible Automation Platform (AAP) configuration as code using the Red Hat CoP collection infra.aap_configuration. Applies best practices for structuring, generating, and maintaining AAP configuration across Controller, Hub, Gateway, and EDA using the dispatch role, dependency-aware ordering, and environment-based organization. Use when working with AAP configuration repositories, YAML-defined platform objects, GitOps patterns for AAP, or when the user references infra.aap_configuration or AAP config as code.
---

# AAP Configuration as Code Skill

Use this skill when working with repositories that manage **Ansible Automation Platform (AAP) as code** with the `infra.aap_configuration` collection from Red Hat Communities of Practice.

This skill is for tasks such as:

- creating or updating AAP configuration stored in YAML
- generating new configuration objects for Controller, Hub, Gateway, or EDA
- restructuring configuration into reusable files
- building or fixing playbooks that apply AAP configuration
- converting older `infra.controller_configuration`, `infra.ah_configuration`, or `infra.eda_configuration` content into the unified `infra.aap_configuration` model
- reviewing a repo for correctness, ordering, naming, and maintainability

## What this collection is

`infra.aap_configuration` is a collection used to configure **AAP 2.5+** as code. It wraps the certified AAP collections and provides roles for:

- Automation Controller
- Automation Hub
- Automation Gateway
- Event-Driven Ansible (EDA)

The recommended entry point is the **`infra.aap_configuration.dispatch`** role, which orchestrates the other roles in dependency-aware order.

## Operating assumptions

When working in an AAP config-as-code repo, assume the following unless the repo clearly does something else:

1. Configuration is expressed as YAML variables.
2. A playbook loads one or more variable files and then includes `infra.aap_configuration.dispatch`.
3. The dispatch role is preferred over manually sequencing many individual roles.
4. Configuration may be split across multiple files and environments.
5. Secrets should not be committed in plaintext.
6. Changes must preserve object dependency order and idempotence.

## Default workflow

### 1. Inspect the repo shape first

Look for:

- `requirements.yml`
- `collections/requirements.yml`
- a playbook like `configure_aap.yml`, `site.yml`, or `apply.yml`
- directories such as:
  - `config/`
  - `configs/`
  - `group_vars/`
  - `host_vars/`
- files containing variables like:
  - `aap_hostname`
  - `aap_username`
  - `aap_password`
  - `aap_token`
  - `aap_validate_certs`
  - `controller_*`
  - `hub_*`
  - `gateway_*`
  - `eda_*`
  - `aap_organizations`
  - `aap_teams`
  - `aap_user_accounts`

### 2. Prefer the dispatch role

When creating or repairing a playbook, prefer this pattern:

```yaml
---
- name: Configure Ansible Automation Platform
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Load configuration files
      ansible.builtin.include_vars:
        dir: configs
        extensions:
          - yml
      tags:
        - always

    - name: Apply AAP configuration
      ansible.builtin.include_role:
        name: infra.aap_configuration.dispatch
```

Only use individual roles when the task is intentionally narrow or the repo already uses that model consistently.

### 3. Keep connection variables centralized

Prefer a single auth file or vault-backed secret source for:

```yaml
aap_hostname: aap.example.com
aap_validate_certs: true
aap_username: admin
aap_password: "{{ vault_aap_password }}"
# or
aap_token: "{{ vault_aap_token }}"
```

Guidelines:

- Prefer token auth where practical.
- Keep cert validation enabled in real environments.
- Do not hardcode credentials in repo-tracked files.
- Preserve the repo’s existing auth pattern unless explicitly asked to migrate it.

### 4. Organize by environment and object type

For larger repos, prefer structures like:

```text
config/
  all/
    organizations.yml
    credential_types.yml
    execution_environments.yml
  dev/
    projects.yml
    inventories.yml
    job_templates.yml
  prod/
    projects.yml
    inventories.yml
    job_templates.yml
```

Use shared files for global objects and environment-specific files for environment-only objects.

### 5. Use wildcard variable aggregation when splitting config

When a repo splits lists across multiple files, prefer wildcard variable aggregation instead of building giant monolithic lists manually.

Example:

```yaml
# config/all/projects.yml
controller_projects_all:
  - name: Common Project
    organization: Default
    scm_type: git
    scm_url: https://github.com/example/common.git

# config/prod/projects.yml
controller_projects_prod:
  - name: Production Project
    organization: Production
    scm_type: git
    scm_url: https://github.com/example/prod.git
```

Then enable aggregation:

```yaml
- name: Apply AAP configuration
  ansible.builtin.include_role:
    name: infra.aap_configuration.dispatch
  vars:
    dispatch_include_wildcard_vars: true
```

### 6. Keep object dependencies in mind

When adding objects, think in this order:

- shared identity and access objects first
- source and runtime dependencies next
- execution objects last

Typical examples:

- organizations before projects and inventories
- credentials before projects, templates, or sync jobs
- projects before job templates and workflows
- Hub registries/repositories before sync actions
- EDA projects and decision environments before rulebook activations

If a change introduces a new dependency, place the data where dispatch can process it in the correct order.

## Service-specific guidance

### Controller

Typical objects include:

- `controller_ad_hoc_commands`
- `controller_ad_hoc_commands_cancel`
- `controller_bulk_hosts`
- `controller_credential_input_sources`
- `controller_credential_types`
- `controller_credentials`
- `controller_execution_environments`
- `controller_groups`
- `controller_host`
- `controller_instance_groups`
- `controller_instances`
- `controller_inventories`
- `controller_inventory_sources`
- `controller_launch_jobs`
- `controller_templates`
- `controller_cancel_jobs`
- `controller_labels`
- `controller_license`
- `controller_notifications`
- `controller_projects`
- `controller_schedules`
- `controller_workflows`

Use Controller for:

- projects and SCM definitions
- inventories and inventory sources
- credentials and credential types
- job templates and workflows
- execution environments assigned to jobs

### Hub

Typical objects include:

- `hub_collections`
- `hub_collection_remotes`
- `hub_collection_repositories`
- `hub_ee_images`
- `hub_ee_registries`
- `hub_ee_repositories`
- `hub_namespaces`
- `hub_custom_collections`

Use Hub for:

- published collections
- execution environment registries and repositories
- namespace ownership and publishing access
- syncing content from remote sources

### Gateway

Typical objects include:

- `aap_applications`
- `gateway_authenticator_maps`
- `gateway_authenticators`
- `aap_organizations`
- `gateway_role_definitions`
- `gateway_role_team_assignments`
- `gateway_role_user_assignments`

Use Gateway for:

- central auth and access patterns
- shared org, user, and team access behavior
- gateway routing and service definitions
- role definitions and assignments

### EDA

Typical objects include:

- `eda_controller_tokens`
- `eda_credential_input_sources`
- `eda_credential_types`
- `eda_credentials`
- `eda_decision_environments`
- `eda_event_streams`
- `eda_projects`
- `eda_rulebook_activations`

Use EDA for:

- rulebook projects
- activation lifecycle
- decision environments
- EDA-specific credentials and integrations

## When to use individual roles

Use an individual role only when one of these is true:

- the user explicitly asked for a single object type
- the repo already applies one role per play
- you are debugging a specific role or variable set
- you want a targeted example

Example:

```yaml
---
- name: Configure only controller projects
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    aap_hostname: aap.example.com
    aap_token: "{{ vault_aap_token }}"
    controller_projects:
      - name: Example Project
        organization: Default
        scm_type: git
        scm_url: https://github.com/example/repo.git

  tasks:
    - name: Configure controller projects
      ansible.builtin.include_role:
        name: infra.aap_configuration.controller_projects
```

## Safe editing rules

When editing an existing repo:

- keep the repo’s current variable naming model unless migration is requested
- do not rename variables just for style
- avoid mixing old collection naming with new unified naming
- avoid adding plaintext secrets
- preserve environment overlays and inheritance patterns
- do not collapse split files unless asked
- do not reorder large lists without a reason
- prefer minimal, reviewable diffs
- keep YAML deterministic and readable

## Migration guidance

The older collections for Controller, Hub, and EDA were consolidated into `infra.aap_configuration`.

When migrating old content:

1. identify the old collection and role names
2. convert to the unified connection variables
3. map old variables to the new role inputs
4. move execution into `infra.aap_configuration.dispatch` where possible
5. test one service area at a time

Do not attempt a broad rename without checking the collection’s conversion guidance and the repo’s current conventions.

## Common implementation patterns

### Minimal project bootstrap

```yaml
collections:
  - name: ansible.platform
    version: ">=2.5.0"
  - name: ansible.hub
    version: ">=1.0.0"
  - name: ansible.controller
    version: ">=4.6.0"
  - name: ansible.eda
    version: ">=2.5.0"
  - name: infra.aap_configuration
```

### Split auth from config

Keep auth in a dedicated file such as `config/all/auth.yml` or an encrypted secret source, and keep object definitions in separate files.

### Enable consolidated error collection

For broad configuration runs, this can help surface all failed roles in one pass:

```yaml
- name: Apply AAP configuration with collected errors
  ansible.builtin.include_role:
    name: infra.aap_configuration.dispatch
  vars:
    aap_configuration_collect_logs: true
```

## Review checklist

Before finishing work, check:

- Does the playbook use `infra.aap_configuration.dispatch` where appropriate?
- Are connection variables present and consistent?
- Are secrets kept out of plaintext?
- Are object lists attached to the correct variables?
- Are organizations, teams, users, credentials, projects, and templates defined in a sensible dependency order?
- Are environment-specific definitions kept separate from shared ones?
- If wildcard aggregation is intended, is `dispatch_include_wildcard_vars: true` present?
- Are changes idempotent and easy to review?

## What to avoid

Avoid these mistakes:

- using `infra.aap_configuration` for AAP 2.4 or earlier without checking compatibility
- mixing old collection examples directly into a new repo
- storing secrets in normal YAML tracked by git
- disabling TLS validation casually in production examples
- creating giant single files when the repo already uses layered config
- bypassing dispatch without a clear reason
- inventing variable names instead of using the collection’s expected list names

## Output style for Claude

When producing changes for an AAP config-as-code repo:

- prefer complete YAML snippets over prose
- show only the files that need to change
- preserve the repo’s indentation and naming style
- explain dependency-sensitive choices briefly
- call out assumptions clearly
- highlight any secrets the user must supply out of band
