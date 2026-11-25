"""Validation helpers for operator-controlled and bot-controlled path inputs."""

import os
import re
from pathlib import Path

_USERNAME_RE = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]{0,15}$')


def is_safe_username(username):
	"""Usernames become directory names; reject separators and dot segments."""
	return (
		isinstance(username, str)
		and bool(_USERNAME_RE.fullmatch(username))
		and '..' not in username
	)


def safe_filename(filename, max_length=34):
	"""Reduce an uploaded name to a single, safe path component."""
	if not isinstance(filename, str):
		return None
	if '/' in filename or '\\' in filename or '..' in filename:
		return None
	name = filename.strip()
	if not name or name in ('.', '..') or len(name) > max_length:
		return None
	if any(ord(char) < 32 or ord(char) == 127 for char in name):
		return None
	return name


def contained_user_dir(output_root, username):
	"""Return ``output_root/username``, refusing traversal and symlink escapes."""
	if not is_safe_username(username):
		raise ValueError('invalid username')
	root = Path(output_root).resolve()
	path = (root / username).resolve()
	if path.parent != root:
		raise ValueError('user directory escapes output root')
	return path
