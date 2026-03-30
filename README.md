# Autogroups

A declarative system group synchronization engine for Linux workstations. 

Autogroups ensures that local system groups match a desired state defined in YAML files.
It is designed for environments that mix local and remote users/groups databases, for example when authenticating through
an Active Directory (via Winbind/Samba).

## Features
* **Declarative Configuration:** Define group memberships in simple YAML files under `/etc/autogroups/groups.d/`.
* **Hybrid Backends:** Supports local users/groups and Active Directory (via Samba/Winbind) out of the box.
* **Idempotency:** Ensures the system group state matches your policy exactly - adding missing users and removing unauthorized ones.
* **Optional Dependencies:** The core engine runs on any standard Linux distro. The follow backends are supported:
  * Local (/etc/passwd and /etc/group files)
  * Winbind (Active Directory)

## Installation

### 1. Requirements
* Python 3.6+
* `PyYAML`
* `winbind` (optional, for Active Directory support)

### 2. Install the Package
From the root of the repository, run:

```shell
pip install .
```

## Configuration

Create a group file, for example `printadmin.yml`, under `/etc/autogroups/groups.d/`:

```yaml
printadmin:
  - backend: winbind
    members: 
      - "@Print Operators"
      - "administrator"
  - backend: local
    members: "@wheel"
```
