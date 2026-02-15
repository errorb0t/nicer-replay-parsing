# You can safely ignore this file. It's expected by heroprotocol

import importlib.util
import os


def find_module(name, path):
    """
    Mimics imp.find_module() behavior using importlib.
    Returns (file, pathname, description) tuple.
    """
    spec = importlib.util.find_spec(name, path[0])

    if spec is None:
        raise ImportError(f"No module named '{name}'")

    # Get the file path
    pathname = spec.origin

    # Determine the description tuple (suffix, mode, type)
    # Types: PY_SOURCE=1, PY_COMPILED=2, C_EXTENSION=3, PKG_DIRECTORY=5
    if spec.origin is None:
        # Built-in or frozen module
        description = ("", "", 6)  # IMP_HOOK or similar
        file_obj = None
    elif spec.origin.endswith(".py"):
        description = (".py", "r", 1)  # PY_SOURCE
        file_obj = open(pathname, "r")
    elif spec.origin.endswith(".pyc"):
        description = (".pyc", "rb", 2)  # PY_COMPILED
        file_obj = open(pathname, "rb")
    elif spec.origin.endswith((".so", ".pyd", ".dll")):
        description = (os.path.splitext(pathname)[1], "rb", 3)  # C_EXTENSION
        file_obj = open(pathname, "rb")
    elif spec.submodule_search_locations is not None:
        # Package directory
        description = ("", "", 5)  # PKG_DIRECTORY
        file_obj = None
        pathname = spec.submodule_search_locations[0]
    else:
        # Fallback
        description = ("", "", 1)
        file_obj = None

    return (file_obj, pathname, description)
