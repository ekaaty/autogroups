# autogroups/backends/winbind.py
from samba.samdb import SamDB
from samba.auth import system_session
from samba.ndr import ndr_unpack
from samba.dcerpc import security
import ldb
import logging

# Standard logging configuration for the winbind backend
logger = logging.getLogger("autogroups.backends.winbind")

class WinbindBackend:
    """
    Backend using Samba's internal Python bindings (samba.samdb).
    Directly accesses the local SAM database to resolve AD users and groups.
    """
    def __init__(self):
        try:
            # Uses the system session (requires root privileges to access secrets.ldb)
            self.lp = None # Will automatically load the default smb.conf
            self.samdb = SamDB(session_info=system_session(), url="default")
            logger.debug("Samba SamDB connection established successfully.")
        except Exception as e:
            logger.error(f"Could not initialize SamDB connection: {e}")
            self.samdb = None

    def get_group_members(self, group_query):
        """
        Resolves group members using sAMAccountNames from the AD.
        Handles @group_name syntax and expands direct members.
        """
        if not self.samdb:
            return set()

        # Remove the @ prefix used in YAML policies
        group_name = group_query.lstrip('@')
        users = set()

        try:
            # Search for the group object in the default naming context
            search_filter = f"(&(objectClass=group)(sAMAccountName={group_name}))"
            res = self.samdb.search(base=self.samdb.get_default_dn(),
                                    scope=ldb.SCOPE_SUBTREE,
                                    expression=search_filter,
                                    attrs=["member"])

            if not res:
                logger.warning(f"AD Group '{group_name}' not found in the directory.")
                return users

            # Iterate over the 'member' attribute which contains Distinguished Names (DNs)
            for member_dn in res[0].get("member", []):
                # Fetch the sAMAccountName and objectClass for each member DN
                member_res = self.samdb.search(base=member_dn,
                                               scope=ldb.SCOPE_BASE,
                                               attrs=["sAMAccountName", "objectClass"])

                if member_res:
                    # LDB returns values as bytes. We decode 'objectClass' to strings for comparison.
                    object_classes = [oc.decode('utf-8') for oc in member_res[0]["objectClass"]]

                    # Ensure we are only adding users (skipping nested groups or computers for now)
                    if 'user' in object_classes:
                        # Decode sAMAccountName to avoid b'username' prefix and quotes
                        username = member_res[0]["sAMAccountName"][0].decode('utf-8')
                        users.add(username)

            return users

        except Exception as e:
            logger.error(f"Error while resolving AD group members for '{group_name}': {e}")
            return users

    def resolve_user(self, username):
        """
        Validates if a specific sAMAccountName exists in the Active Directory.
        Used for explicit user entries in YAML policies.
        """
        if not self.samdb:
            return False

        try:
            # Search for a user object with the matching sAMAccountName
            res = self.samdb.search(base=self.samdb.get_default_dn(),
                                    scope=ldb.SCOPE_SUBTREE,
                                    expression=f"(&(objectClass=user)(sAMAccountName={username}))",
                                    attrs=["sAMAccountName"])
            return len(res) > 0
        except Exception as e:
            logger.error(f"Error while resolving user '{username}': {e}")
            return False
