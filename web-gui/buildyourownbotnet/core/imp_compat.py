"""Minimal ``imp`` compatibility helpers for Python 3.12+.

The stdlib ``imp`` module was removed in Python 3.12.  The remote loader only
used three of its helpers, all of which map directly to ``importlib`` /
``types`` primitives.
"""

import importlib.machinery
import threading
import types

_lock = threading.RLock()


def find_module(name, path=None):
    """Return ``(file, filename, description)`` for a locally available module.

    Raises ImportError when the module cannot be found, matching ``imp.find_module``.
    """
    spec = importlib.machinery.PathFinder.find_spec(name, path)
    if spec is None:
        raise ImportError("No module named %s" % name)
    return (None, spec.origin, None)


def acquire_lock():
    _lock.acquire()


def release_lock():
    _lock.release()


def new_module(name):
    return types.ModuleType(name)
