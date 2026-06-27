import psycopg,logging,warnings,traceback,os,yaml,logging
from psycopg import sql, connect
from psycopg.rows import dict_row
from abstract_database import *
from flask import Request
from typing import *
from datetime import datetime

import threading as _threading  # noqa: E402
def get_logger_callable(logger, level="info"):
    if logger is None:
        return None
    elif isinstance(logger, logging.Logger):
        return getattr(logger, level.lower(), None)
    elif callable(logger) and hasattr(logger, "__self__") and isinstance(logger.__self__, logging.Logger):
        return logger
    else:
        return None


def _find_caller_frame_index():
    """
    Return the index in inspect.stack() of the first frame
    that’s not in this module or the logging stdlib.
    """
    for idx, frame_info in enumerate(inspect.stack()):
        fn = frame_info.filename
        if not fn.endswith("logging_utils.py") and "logging" not in os.path.basename(fn):
            return idx
    return 0  # fallback

def get_caller_info():
    """
    Returns (caller_path, caller_idx).
    caller_idx is the index into inspect.stack() where the call came from.
    """
    idx = _find_caller_frame_index()
    frame = inspect.stack()[idx]
    return frame.filename, idx

def print_or_log(message, logger=True, level="info"):
    # 1) grab both the path and the numeric index
    caller_path, caller_idx = get_caller_info()

    # 2) decide which logger object to use
    if logger is True:
        bpName = os.path.splitext(os.path.basename(caller_path))[0]
        logger = get_logFile(bpName)

    # 3) pick the right logging method
    log_callable = get_logger_callable(logger, level=level)
    if log_callable:
        # pass the integer stacklevel = caller_idx + 1
        log_callable(message, stacklevel=caller_idx + 1)
    else:
        print(message)

def initialize_call_log(value=None,
                        data=None,
                        logMsg=None,
                        log_level=None):
    """
    Inspect the stack to find the first caller *outside* this module,
    then log its function name and file path.
    """
    # Grab the current stack
    stack = inspect.stack()
    caller_name = "<unknown>"
    caller_path = "<unknown>"
    log_level = log_level or 'info'
    try:
        # Starting at index=1 to skip initialize_call_log itself
        for frame_info in stack[1:]:
            modname = frame_info.frame.f_globals.get("__name__", "")
            # Skip over frames in your logging modules:
            if not modname.startswith("abstract_utilities.log_utils") \
               and not modname.startswith("abstract_flask.request_utils") \
               and not modname.startswith("logging"):
                caller_name = frame_info.function
                caller_path = frame_info.filename
                break
    finally:
        # Avoid reference cycles
        del stack

    logMsg = logMsg or "initializing"
    full_message = (
        f"{logMsg}\n"
        f"calling_function: {caller_name}\n"
        f"path: {caller_path}\n"
        f"data: {data}"
    )

    print_or_log(full_message,level=log_level)
class SingletonMeta(type):
    """Thread-safe singleton metaclass: one instance per class."""

    _instances: dict = {}
    _lock = _threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
def make_list(obj, commaparse=True):
    """
    Convert ``obj`` to a list.

    - A comma-containing string is split on commas (unless ``commaparse`` is False).
    - sets and tuples become lists.
    - lists are returned unchanged.
    - anything else is wrapped in a single-element list.
    """
    if isinstance(obj, str):
        if ',' in obj and commaparse is True:
            obj = obj.split(',')
    if isinstance(obj, (set, tuple)):
        return list(obj)
    if isinstance(obj, list):
        return obj
    return [obj]
_json_logger = logging.getLogger(__name__)
def validate_file_path(file_path, is_read=False):
    if file_path and isinstance(file_path, str):
        if os.path.isfile(file_path) or os.path.isdir(file_path):
            return file_path
        if not is_read:
            dirname = os.path.dirname(file_path)
            if os.path.isdir(dirname):
                return file_path


def get_file_path(*args, is_read=False, **kwargs):
    args = list(args)
    for file_path in args:
        if validate_file_path(file_path, is_read=is_read):
            return file_path
    for file_path in list(kwargs.values()):
        if validate_file_path(file_path, is_read=is_read):
            return file_path
def _output_read_write_error(e, function_name, file_path, valid_file_path=None, data=None, is_read=False):
    error_text = f"Error in {function_name};{e}\nFile path: {file_path} "
    if valid_file_path is None:
        error_text += f"\nValid File path: {valid_file_path} "
    if not is_read:
        error_text += f"\nData: {data} "
    _json_logger.error(error_text)
def _read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
def safe_read_from_json(file_path, *args, **kwargs):
    """Read and return JSON content from ``file_path`` (None on failure)."""
    is_read = True
    valid_file_path = get_file_path(file_path, *args, is_read=is_read, **kwargs)
    if valid_file_path:
        file_path = valid_file_path
    try:
        return _read_json(file_path)
    except Exception as e:
        _output_read_write_error(e, 'safe_read_from_json', file_path, valid_file_path, is_read=is_read)
        return None
