"""
core/paths.py — Project Root Path Resolver
All modules use this to resolve file paths relative to the project root,
regardless of which subdirectory the module lives in.
"""
import os

# Project root = parent directory of core/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*parts):
    """Returns absolute path relative to project root."""
    return os.path.join(PROJECT_ROOT, *parts)
