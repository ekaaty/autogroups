import grp
import pwd
import logging

logger = logging.getLogger("autogroups.backends.local")

class LocalBackend:
    """Backend for resolving users and groups from /etc/passwd and /etc/group."""

    def get_group_members(self, group_name):
        """Returns the list of members for a local group (removes @ prefix)."""
        clean_name = group_name.lstrip('@')
        try:
            group_info = grp.getgrnam(clean_name)
            return group_info.gr_mem
        except KeyError:
            logger.warning(f"Local group '{clean_name}' not found.")
            return []

    def resolve_user(self, username):
        """Checks if a user exists in the local /etc/passwd."""
        try:
            pwd.getpwnam(username)
            return True
        except KeyError:
            return False
