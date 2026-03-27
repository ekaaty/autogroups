# Autogroups

A declarative system group synchronization engine for Linux workstations. 

Autogroups ensures that local system groups match a desired state defined in YAML files. It is designed for environments that mix local administration with Active Directory (via Winbind/Samba).

## Features
* **Declarative Configuration:** Define group memberships in simple YAML files under `/etc/autogroups/groups.d/`.
* **Hybrid Backends:** Supports local users/groups and Active Directory (via Samba/Winbind) out of the box.
* **Optional Dependencies:** Winbind support is optional; the core engine runs on any standard Linux distro if Samba bindings are missing.
* **Idempotency:** Ensures the system group state matches your policy exactly—adding missing users and removing unauthorized ones.

## Installation

### 1. Requirements
* Python 3.6+
* `PyYAML`
* `samba` (optional, for Active Directory support)

### 2. Install the Package
From the root of the repository, run:
```bash
pip install .
