"""Regressions for unauthenticated C2 API input hardening."""

import base64
import os
from pathlib import Path

from buildyourownbotnet.core.path_safety import is_safe_username, safe_filename
from buildyourownbotnet.models import Session
from ..conftest import app_client, new_user, login, cleanup

OUTPUT_DIR = Path(os.path.abspath('buildyourownbotnet/output'))


def _upload(client, owner, filename):
	return client.post('/api/file/add', data={
		'data': base64.b64encode(b'marker'),
		'type': 'txt',
		'owner': owner,
		'module': 'upload',
		'session': base64.b64encode(b'1.2.3.4'),
		'filename': filename,
	})


def test_file_upload_rejects_absolute_and_traversal_names(app_client, new_user):
	login(app_client, new_user.username, 'test_password')
	for name in ('/tmp/pwned', '../../../config.py', '..', '../modules/util.py'):
		res = _upload(app_client, new_user.username, name)
		assert res.status_code == 400
	assert not Path('/tmp/pwned').exists()


def test_file_upload_requires_existing_owner(app_client, new_user):
	login(app_client, new_user.username, 'test_password')
	assert _upload(app_client, '../etc', 'safe.txt').status_code == 400


def test_payload_generation_rejects_shell_metacharacters(app_client, new_user):
	login(app_client, new_user.username, 'test_password')
	res = app_client.post('/api/payload/generate', data={
		'format': 'exe',
		'operating_system': 'win;touch /tmp/pwned;#',
		'architecture': 'amd64',
	}, follow_redirects=True)
	assert res.status_code == 200
	assert b'Invalid operating system or architecture' in res.data


def test_username_validation_rejects_path_components():
	assert is_safe_username('test_user')
	assert not is_safe_username('../etc')
	assert not is_safe_username('a/b')
	assert not is_safe_username('a..b')


def test_safe_filename_strips_separators():
	assert safe_filename('/tmp/evil.txt') is None
	assert safe_filename('../config.py') is None
	assert safe_filename('..') is None
	assert safe_filename('note.txt') == 'note.txt'
	assert safe_filename('a' * 200) is None
	assert len(safe_filename('a' * 34)) == 34


def test_session_endpoint_rejects_unknown_owner_and_bad_uid(app_client, new_user):
	assert app_client.post('/api/session/new', json={
		'owner': '../etc', 'public_ip': '1.2.3.4'
	}).status_code == 400
	assert app_client.post('/api/session/new', json={
		'owner': new_user.username, 'uid': '../../etc/passwd'
	}).status_code == 400


def test_session_endpoint_caps_sessions_per_owner(app_client, new_user):
	from buildyourownbotnet import c2  # noqa: F401 - ensure app state initialized
	for index in range(101):
		uid = f'{index:032x}'
		res = app_client.post('/api/session/new', json={
			'owner': new_user.username, 'uid': uid, 'public_ip': '1.2.3.4'
		})
		if index < 100:
			assert res.status_code == 200
		else:
			assert res.status_code == 429
	assert Session.query.filter_by(owner=new_user.username).count() == 100
