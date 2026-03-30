# autogroups/backends/winbind.py
import subprocess
import logging
import shutil

logger = logging.getLogger("autogroups.backends.winbind")

class WinbindBackend:
    """
    Backend using 'wbinfo' to query Winbind daemon.
    """
    def __init__(self):
        self.wbinfo_path = shutil.which("wbinfo")
        if not self.wbinfo_path:
            logger.debug("wbinfo not found. Backend disabled.")
            self.active = False
            return

        if self._check_ping():
            logger.debug("Winbind connection established.")
            self.active = True
        else:
            logger.warning("winbindd not responding.")
            self.active = False

    def _check_ping(self):
        try:
            subprocess.run([self.wbinfo_path, "-p"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_group_members(self, group_query):
        if not self.active:
            return set()

        group_name = group_query.lstrip('@')
        users = set()

        try:
            # Output format: group:*:GID:user1,user2...
            result = subprocess.run(
                [self.wbinfo_path, f"--group-info={group_name}"],
                check=True, capture_output=True, text=True
            )
            
            output = result.stdout.strip()
            if output:
                parts = output.split(':')
                if len(parts) >= 4 and parts[3]:
                    members = parts[3].split(',')
                    for member in members:
                        users.add(member.strip())
            
            return users
        except subprocess.CalledProcessError:
            logger.debug(f"AD Group '{group_name}' not found.")
            return users
        except Exception as e:
            logger.error(f"Error resolving AD group '{group_name}': {e}")
            return users

    def resolve_user(self, username):
        if not self.active:
            return False

        try:
            subprocess.run(
                [self.wbinfo_path, "-n", username],
                check=True, capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
