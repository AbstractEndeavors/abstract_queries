from ..imports import datetime, List, Dict
from ..query_utils import *
from abstract_utilities import SingletonMeta


class UserIPManager(BaseQueryManager):

    """Manages CRUD operations for the user_ips table."""

    def __init__(self, logs_on: bool = False):
        if not hasattr(self, "initialized") or self.logs_on != logs_on:
            self.initialized = True
            self.filename = "userIpQueries"
            self.basename = f"{self.filename}.json"
            self.logs_on = logs_on
            self.ip_history: Dict[str, List[Dict]] = {}
            super().__init__(self.filename, logs_on=logs_on)

    # -----------------------------------------------------
    # internal utilities
    # -----------------------------------------------------

    def _log(self):
        if self.logs_on:
            initialize_call_log()

    # -----------------------------------------------------
    # user_ip CRUD
    # -----------------------------------------------------

    def select_user_ip(self, user_id: int, ip: str):
        """Check if a user IP record exists."""
        self._log()
        return select_rows(self._query_select_user_ip, user_id, ip)

    def update_user_ip(self, user_id: int, ip: str):
        """Update last_seen and increment hit_count."""
        self._log()
        insert_query(
            self._query_update_user_ip,
            datetime.utcnow(),
            user_id,
            ip
        )

    def insert_user_ip(self, user_id: int, ip: str):
        """Insert a new user_ip row."""
        self._log()
        insert_query(self._query_insert_user_ip, user_id, ip)

    def log_user_ip(self, user_id: int, ip: str):
        """Insert or update a user_ip record."""
        self._log()

        if self.select_user_ip(user_id, ip):
            self.update_user_ip(user_id, ip)
        else:
            self.insert_user_ip(user_id, ip)

    # -----------------------------------------------------
    # user lookup by IP
    # -----------------------------------------------------

    def select_user_by_ip(self, ip: str):
        """Retrieve users associated with an IP."""
        self._log()

        ip = str(ip)

        if ip in self.ip_history:
            return self.ip_history[ip]

        result = select_rows(self._query_select_user_by_ip, ip)
        self.ip_history[ip] = result

        return result

    def get_user_by_ip(self, ip: str):
        """Public interface."""
        return self.select_user_by_ip(ip)
