from .query_utils import *
from .blacklist_queries import *
from .ip_queries import *
from .user_queries import *
from .table_queries import *
from .uploads_queries import *
from .request_queries import *

# The shared manager singletons used to be constructed at import time, which
# meant ``import abstract_queries`` immediately read JSON/YAML config off disk
# (and, transitively, could reach for the database) before the caller did
# anything. They are now built lazily on first access via PEP 562 so importing
# the package is cheap and side-effect free. The public names are unchanged.
_LAZY_MANAGERS = {
    "USER_IP_MGR": UserIPManager,
    "BLACKLIST_MGR": BlacklistManager,
    "TABLE_MGR": TableManager,
    "UPLOAD_MGR": UploadManager,
    "USER_MGR": UserManager,
}
_manager_cache = {}


def __getattr__(name):
    factory = _LAZY_MANAGERS.get(name)
    if factory is not None:
        if name not in _manager_cache:
            _manager_cache[name] = factory()
        return _manager_cache[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals()) + list(_LAZY_MANAGERS))
