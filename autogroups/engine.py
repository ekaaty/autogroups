import os
import yaml
import logging
import grp           # Required for local group lookups
import subprocess    # Required for system commands (usermod, gpasswd)
from .backends.local import LocalBackend

logger = logging.getLogger("autogroups.engine")

class AutogroupsEngine:
    """
    Main orchestration engine for Autogroups.
    It parses YAML definitions and synchronizes system groups.
    """
    def __init__(self, config_dir="/etc/autogroups/groups.d/"):
        self.config_dir = config_dir

        # Initialize backends
        self.local = LocalBackend()

        # Attempt to load Winbind/Samba backend optionally
        self.winbind = None
        try:
            from .backends.winbind import WinbindBackend
            self.winbind = WinbindBackend()
            if not self.winbind.samdb:
                self.winbind = None # Backend loaded but DB connection failed
        except (ImportError, Exception) as e:
            logger.warning(f"Winbind backend disabled or not available: {e}")

    def get_policy_files(self):
        """Returns a list of all .yml files in the config directory."""
        if not os.path.exists(self.config_dir):
            logger.error(f"Config directory {self.config_dir} not found.")
            return []
        return [f for f in os.listdir(self.config_dir) if f.endswith('.yml')]

    def process_group_policy(self, group_name, policy_data):
        """
        Processes a single group policy against all backends.
        Returns a set of users that should belong to this group.
        """
        allowed_users = set()

        for entry in policy_data:
            backend_type = entry.get('backend')
            members = entry.get('members', [])

            if backend_type == 'winbind':
                # Protection: check if winbind backend is actually available
                if not self.winbind:
                    logger.error(f"Policy for '{group_name}' requires winbind, but it's unavailable.")
                    continue

                # Use the Samba/Winbind backend to resolve members
                for member in members:
                    if member.startswith('@'):
                        allowed_users.update(self.winbind.get_group_members(member))
                    else:
                        if self.winbind.resolve_user(member):
                            allowed_users.add(member)

            elif backend_type == 'local':
                # Use the local /etc/group backend
                for member in members:
                    if member.startswith('@'):
                        allowed_users.update(self.local.get_group_members(member))
                    else:
                        if self.local.resolve_user(member):
                            allowed_users.add(member)

        return allowed_users

    def sync(self, dry_run=False):
        """
        Iterates over all policies and applies changes to the system.
        Accepts dry_run argument from CLI.
        """
        for policy_file in self.get_policy_files():
            path = os.path.join(self.config_dir, policy_file)
            target_group = os.path.splitext(policy_file)[0]

            if not os.path.exists(path):
                continue

            with open(path, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    policy_data = data.get(target_group, [])
                    target_users = self.process_group_policy(target_group, policy_data)
                    self._apply_to_system(target_group, target_users, dry_run=dry_run)
                except yaml.YAMLError as e:
                    logger.error(f"Failed to parse {policy_file}: {e}")

    def _apply_to_system(self, group_name, target_users, dry_run=False):
        """
        Reconciles the local system group state with the target_users set.
        """
        try:
            # 1. Ensure the local group exists
            try:
                current_group = grp.getgrnam(group_name)
                current_members = set(current_group.gr_mem)
            except KeyError:
                if dry_run:
                    logger.info(f"[DRY-RUN] Would create system group '{group_name}'")
                    current_members = set()
                else:
                    logger.info(f"Group '{group_name}' does not exist. Creating...")
                    subprocess.run(['groupadd', '-r', group_name], check=True)
                    current_members = set()

            # 2. Calculate differences
            to_add = target_users - current_members
            to_remove = current_members - target_users

            # 3. Handle Dry Run logging
            if dry_run:
                for user in to_add:
                    logger.info(f"[DRY-RUN] Would add user '{user}' to group '{group_name}'")
                for user in to_remove:
                    logger.info(f"[DRY-RUN] Would remove user '{user}' from group '{group_name}'")
                return

            # 4. Apply additions
            for user in to_add:
                try:
                    subprocess.run(['id', user], capture_output=True, check=True)
                    subprocess.run(['usermod', '-aG', group_name, user], check=True)
                    logger.info(f"Added user '{user}' to group '{group_name}'.")
                except subprocess.CalledProcessError:
                    logger.warning(f"User '{user}' not found by system. Skipping addition.")

            # 5. Apply removals
            for user in to_remove:
                try:
                    subprocess.run(['gpasswd', '-d', user, group_name], check=True)
                    logger.info(f"Removed user '{user}' from group '{group_name}'.")
                except subprocess.CalledProcessError:
                    logger.error(f"Failed to remove user '{user}' from group '{group_name}'.")

        except Exception as e:
            logger.error(f"Critical error syncing group '{group_name}': {e}")
