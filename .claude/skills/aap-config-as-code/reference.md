# AAP Configuration as Code Reference

A concise reference for working with the `infra.aap_configuration` collection.

## Scope

Use this reference for **AAP 2.5+** repositories built around the unified `infra.aap_configuration` collection.

For AAP 2.4 and earlier, the older collections may still be the safer model.

## Core idea

The collection configures AAP through **Ansible variables + roles**.

Preferred execution model:

1. load variables
2. include `infra.aap_configuration.dispatch`
3. let dispatch execute service roles in dependency-aware order

## Required collections

Typical requirements file:

```yaml
---
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

## Connection variables

Common top-level connection variables:

```yaml
aap_hostname: aap.example.com
aap_validate_certs: true

# one auth pattern
aap_username: admin
aap_password: "{{ vault_aap_password }}"

# or token auth
aap_token: "{{ vault_aap_token }}"
```

Notes:

- prefer token auth when practical
- keep `aap_validate_certs: true` for real environments
- store secrets in Ansible Vault or another secret source

## Preferred playbook pattern

```yaml
---
- name: Configure AAP
  hosts: localhost
  connection: local
  gather_facts: false

  tasks:
    - name: Load vars
      ansible.builtin.include_vars:
        dir: configs
        extensions:
          - yml
      tags:
        - always

    - name: Run dispatch
      ansible.builtin.include_role:
        name: infra.aap_configuration.dispatch
```

## Dispatch role controls

### Main control list

`aap_configuration_dispatcher_roles`

The meta list used by dispatch to determine which roles to run.

### Exclude selected roles

`aap_configuration_dispatcher_exclude_roles`

Example:

```yaml
aap_configuration_dispatcher_exclude_roles:
  - controller_inventory_source_update
  - hub_ee_registry_index
```

### Merge wildcard variables

`dispatch_include_wildcard_vars: true`

Use when you split lists into environment- or purpose-specific variables such as:

- `controller_projects_all`
- `controller_projects_dev`
- `controller_projects_prod`

These can be merged into the base variable:

- `controller_projects`

### Collect errors instead of failing fast

```yaml
aap_configuration_collect_logs: true
```

Useful for large runs where you want a summary of role failures at the end.

## Dispatch execution model

The collection’s getting started guide describes this default high-level order:

1. Gateway configuration
2. Hub configuration
3. Controller configuration
4. EDA configuration

That ordering matters because many objects depend on earlier ones.

## Shared object variables

These variables are reused across service areas:

```yaml
aap_organizations:
aap_teams:
aap_user_accounts:
aap_applications:
```

Use them for shared identity and access objects where the collection expects them.

## Gateway reference

Common Gateway variables:

```yaml
gateway_authenticators:
gateway_authenticator_maps:
gateway_settings:
gateway_applications:
gateway_http_ports:
gateway_service_clusters:
gateway_service_keys:
gateway_service_nodes:
gateway_services:
gateway_role_definitions:
gateway_role_team_assignments:
gateway_role_user_assignments:
gateway_routes:
```

Shared variables used by Gateway roles:

```yaml
aap_organizations:
aap_teams:
aap_user_accounts:
```

Common Gateway tags from dispatch:

- `authenticators`
- `authenticator_maps`
- `settings`
- `organizations`
- `applications`
- `http_ports`
- `service_clusters`
- `service_keys`
- `service_nodes`
- `services`
- `teams`
- `users`
- `role_definitions`
- `role_team_assignments`
- `role_user_assignments`
- `routes`

## Hub reference

Common Hub variables:

```yaml
hub_namespaces:
hub_collections:
hub_ee_registries:
hub_ee_repositories:
hub_ee_repository_sync:
hub_ee_images:
hub_collection_remotes:
hub_collection_repositories:
```

Common Hub tags from dispatch include:

- `namespaces`
- `collections`
- `registries`
- `repos`
- `reposync`
- `images`
- `registry`
- `ee_indices`
- `regsync`
- `collectionremote`

Use Hub for namespaces, collections, remotes, repositories, execution environment content, and registry sync actions.

## Controller reference

Common Controller variables include:

```yaml
controller_credential_types:
controller_credentials:
controller_projects:
controller_inventories:
controller_templates:
```

Other common Controller object families often found in repos:

```yaml
controller_execution_environments:
controller_instance_groups:
controller_inventory_sources:
controller_hosts:
controller_groups:
controller_schedules:
controller_workflows:
controller_notifications:
controller_settings:
```

Common Controller tags from dispatch include:

- `settings`
- `credentials`
- `projects`
- `inventories`
- `hosts`
- `job_templates`
- `workflows`
- `schedules`

Use Controller for projects, inventories, credentials, templates, workflows, schedules, and related runtime objects.

## EDA reference

Common EDA object families:

```yaml
eda_credentials:
eda_projects:
eda_decision_environments:
eda_rulebook_activations:
```

Use EDA for event-driven automation assets and activation lifecycle.

## Example object snippets

### Organizations

```yaml
aap_organizations:
  - name: Infrastructure
    description: Infrastructure Team Organization
```

### Controller credentials

```yaml
controller_credentials:
  - name: GitHub Access Token
    organization: Infrastructure
    credential_type: Source Control
    inputs:
      username: git-user
      password: "{{ vault_github_token }}"
```

### Controller projects

```yaml
controller_projects:
  - name: Infrastructure Playbooks
    organization: Infrastructure
    scm_type: git
    scm_url: https://github.com/yourorg/infra-playbooks.git
    scm_credential: GitHub Access Token
    scm_update_on_launch: true
    scm_delete_on_update: true
```

### Controller inventory

```yaml
controller_inventories:
  - name: Production Inventory
    organization: Infrastructure
    description: Production servers inventory
```

### Controller job template

```yaml
controller_templates:
  - name: Deploy Web Application
    organization: Infrastructure
    project: Infrastructure Playbooks
    playbook: deploy_webapp.yml
    inventory: Production Inventory
    credentials:
      - GitHub Access Token
    ask_variables_on_launch: true
```

### Hub namespace

```yaml
hub_namespaces:
  - name: my_organization
    description: My organization's namespace
    groups:
      - name: admins
        roles:
          - namespace_owner
```

### Hub registry

```yaml
hub_ee_registries:
  - name: quay_registry
    url: https://quay.io
    username: myuser
    password: "{{ vault_quay_password }}"
```

## Environment layout patterns

A good multi-environment layout often looks like:

```text
config/
  all/
    auth.yml
    organizations.yml
    credential_types.yml
  dev/
    projects.yml
    inventories.yml
    job_templates.yml
  prod/
    projects.yml
    inventories.yml
    job_templates.yml
```

Rules of thumb:

- shared objects go in `all/`
- environment-only objects go in `dev/`, `qa/`, `prod/`, and so on
- keep secrets separate from regular object files

## Secret handling

Preferred approaches:

- Ansible Vault encrypted vars
- environment-specific secret files
- external secret manager integrated into playbook execution

Do not:

- commit plaintext passwords or tokens
- duplicate secrets across many object files
- hide secrets inside examples without labeling them as placeholders

## Migration notes

Older collections:

- `infra.controller_configuration`
- `infra.ah_configuration`
- `infra.eda_configuration`

Unified replacement:

- `infra.aap_configuration`

Migration expectations:

- role names changed
- variables changed
- connection model was standardized
- Gateway support was added to the unified collection

## Review heuristics

When reviewing a repo or patch, check for:

- correct use of `infra.aap_configuration.dispatch`
- expected variable names instead of invented ones
- separation of shared and environment-specific config
- secrets kept out of tracked plaintext
- dependency-aware object definitions
- minimal, idempotent changes
- no accidental mixing of old and new collection patterns

## Common mistakes

- using the unified collection against older AAP versions without checking compatibility
- adding new objects under the wrong variable name
- putting Controller objects under Hub or Gateway data structures
- bypassing dispatch for broad repo-wide configuration
- forgetting `dispatch_include_wildcard_vars: true` when relying on split wildcard lists
- using `aap_validate_certs: false` as a permanent setting
- storing passwords directly in normal YAML

## Quick decision guide

Use `dispatch` when:

- configuring multiple object families
- building a standard repo
- applying full environment config
- you want correct dependency ordering by default

Use an individual role when:

- targeting one object type only
- debugging a specific role
- making a narrow example
- the repo already uses single-role plays consistently

## Output conventions for generated changes

When generating repo changes:

- preserve existing file layout
- prefer exact YAML patches
- minimize speculative fields
- keep names stable
- mark placeholders clearly
- call out user-supplied secrets explicitly
