# AAP Configuration as Code Skill

A agent skill for working with Ansible Automation Platform (AAP) configuration repositories that use the `infra.aap_configuration` collection from Red Hat Communities of Practice.

## What This Skill Does

This skill provides expert guidance and automation for managing AAP 2.5+ configuration as code. It helps you structure, generate, maintain, and review YAML-based AAP configuration using best practices from the `infra.aap_configuration` collection.

## When to Use This Skill

Invoke this skill when you need to:

- **Create or modify** AAP configuration YAML files
- **Generate** new configuration objects for Controller, Hub, Gateway, or EDA
- **Structure** a new AAP config-as-code repository
- **Build or fix** playbooks that apply AAP configuration
- **Migrate** from older collections (`infra.controller_configuration`, `infra.ah_configuration`, `infra.eda_configuration`) to the unified model
- **Review** existing configuration for correctness, ordering, and maintainability
- **Troubleshoot** configuration issues or dependency ordering problems

## Key Concepts

### The Dispatch Role

The skill strongly favors using the `infra.aap_configuration.dispatch` role as the primary entry point. This role:

- Orchestrates all sub-roles in the correct dependency order
- Handles Controller, Hub, Gateway, and EDA configuration
- Provides wildcard variable aggregation for split configurations
- Offers error collection and centralized logging

### Configuration Structure

The skill promotes:

- **YAML-based configuration** stored in version control
- **Environment separation** (dev/prod/qa) with shared base configs
- **Secret management** using Ansible Vault or external secret managers
- **Dependency-aware ordering** to avoid circular references
- **Idempotent operations** that can be safely re-run

### Supported AAP Components

- **Automation Controller**: projects, inventories, credentials, job templates, workflows
- **Automation Hub**: collections, namespaces, execution environments, registries
- **Automation Gateway**: authenticators, organizations, teams, users, roles, routes
- **Event-Driven Ansible (EDA)**: projects, decision environments, rulebook activations

## Example Usage

### Creating a New AAP Config Repository

```
Create a new AAP config-as-code repository with best practices for managing our production environment
```

### Generating Configuration Objects

```
Add a new Controller job template for deploying our web application to the production inventory
```

### Migrating from Old Collections

```
Convert this playbook from infra.controller_configuration to infra.aap_configuration
```

### Reviewing Configuration

```
Review the AAP config in this repository for dependency issues and best practices
```

### Structuring Multi-Environment Config

```
Reorganize this config to support dev, qa, and prod environments with shared base configuration
```

## What the Skill Provides

### Playbook Patterns

The skill generates playbooks following this preferred pattern:

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

### Directory Structure Guidance

For multi-environment repos:

```
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

### Variable Naming

The skill uses the collection's expected variable names:

- Connection: `aap_hostname`, `aap_token`, `aap_validate_certs`
- Gateway: `gateway_authenticators`, `gateway_role_definitions`
- Hub: `hub_collections`, `hub_ee_registries`, `hub_namespaces`
- Controller: `controller_projects`, `controller_inventories`, `controller_templates`
- EDA: `eda_projects`, `eda_decision_environments`, `eda_rulebook_activations`
- Shared: `aap_organizations`, `aap_teams`, `aap_user_accounts`

## What the Skill Avoids

The skill actively prevents:

- Hardcoding secrets in plaintext YAML files
- Mixing old and new collection patterns
- Bypassing the dispatch role without justification
- Creating configurations that ignore dependency ordering
- Using `aap_validate_certs: false` in production examples
- Over-engineering simple requirements
- Inventing variable names instead of using collection standards

## How to Invoke

The skill is automatically triggered when the agent detects:

- References to `infra.aap_configuration`
- AAP config-as-code repository patterns
- YAML files with AAP configuration variables
- Playbooks using AAP configuration roles

You can also manually invoke it by mentioning "AAP config as code" or "infra.aap_configuration" in your request.

## Requirements

To use configurations generated by this skill, your environment needs:

- **Ansible Automation Platform 2.5+**
- **Collections**:
  - `infra.aap_configuration`
  - `ansible.platform` (>= 2.7.20260615)
  - `ansible.controller` (>= 	4.8.2)
  - `ansible.hub` (>= 1.0.6)
  - `ansible.eda` (>= 2.12.1)

## Version Compatibility

- **AAP 2.5+**: Use `infra.aap_configuration` (recommended)
- **AAP 2.4 and earlier**: The older individual collections may be more appropriate

This skill targets AAP 2.5+ and the unified collection model.

## Further Reading

For detailed implementation guidance, see:

- `SKILL.md`: Complete skill prompt with implementation details
- `reference.md`: Quick reference for variables, roles, and patterns
- [infra.aap_configuration on Galaxy](https://galaxy.ansible.com/ui/repo/published/infra/aap_configuration/)
- [Red Hat Communities of Practice](https://github.com/redhat-cop)

## Support

This skill is maintained as part of the Megalith Ansible Template Repository project. Issues and improvements can be submitted through the repository's issue tracker.