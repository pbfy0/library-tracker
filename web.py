from flask import *

from db import *
import periods
import datetime

app = Flask(__name__)

@app.route('/api/<int:sid>/check')
def check(sid):
	per = None
	if 'per' not in request.args:
		t = datetime.datetime.fromtimestamp(int(request.args['ts'])) if 'ts' in request.args else periods.get_current_time()
		per = periods.get_current_period(t)
	else:
		per = int(request.args['per'])
	print(per)
	u = Student.select().where(Student.sid == sid)
	if len(u) == 0: return jsonify(status='NO_STUDENT'), 404
	uu = u[0]
	#print(u, u[0], u[0].grade, u[0].sid, u[0].free_periods, sep='\n')
	fp = [x for x in uu.free_periods if x.period == per]
	#fp = u[0].free_periods.where(FreePeriod.period == per)
	print(fp)
	if len(fp) == 0: return jsonify(status=per_type.NOT_FREE.name)
	return jsonify(status='OK', type=per_type(fp[0].type).name)

@app.route('/api/<int:sid>/sign_in')
def ss(sid):
	return sign_in_h(sid, True)
@app.route('/api/<int:sid>/sign_out')
def so(sid):
	return sign_in_h(sid, False)
def sign_in_h(sid, c_in):
	u = Student.select(Student).where(Student.sid == sid)
	if len(u) == 0: return jsonify(status='NO_STUDENT'), 404
	s = u[0]
	return jsonify(status=sign_in(s, c_in))

def sign_in(s, c_in):
	v = s.last_log is not None and s.last_log.c_in
	if v == c_in: return 'ALREADY'
	with db.atomic():
		s.last_log = LogEntry.create(c_in=c_in, student=s, location=0)
		s.save()
	return 'SUCCESS'

one_second = datetime.timedelta(microseconds=999999)
@app.route('/api/<int:sid>/log')
def s_log(sid):
	u = Student.select(Student).where(Student.sid == sid)
	if len(u) == 0: return jsonify(status='NO_STUDENT'), 404
	uu = u[0]
	q = uu.log_entries
	if 'min_t' in request.args: q = q.where(LogEntry.timestamp >= datetime.datetime.fromtimestamp(int(request.args['min_t'])))
	if 'max_t' in request.args: q = q.where(LogEntry.timestamp <= datetime.datetime.fromtimestamp(int(request.args['max_t'])) + one_second)
	return jsonify(status='OK', log=[dict(ts=int(x.timestamp.timestamp()), c_in=x.c_in) for x in q])

@app.route('/api/log')
def log():
	q = LogEntry.select()
	if 'min_t' in request.args: q = q.where(LogEntry.timestamp >= datetime.datetime.fromtimestamp(int(request.args['min_t'])))
	if 'max_t' in request.args: q = q.where(LogEntry.timestamp <= datetime.datetime.fromtimestamp(int(request.args['max_t'])) + one_second)
	return jsonify(status='OK', log=[dict(sid=x.student_id, ts=int(x.timestamp.timestamp()), c_in=x.c_in) for x in q])

@app.route('/api/signed_in')
def signed_in():
	st = Student.select(Student, LogEntry).join(LogEntry).where(LogEntry.c_in == True)#where(LogEntry.student << .join(LogEntry, on).where(nt.last_log.c_in == True)
	#print(list(st))
	return jsonify(status='OK', signed_in=[dict(sid=x.sid, ts=int(x.last_log.timestamp.timestamp())) for x in st])

@app.route('/api/signout_all')
def sa_handle():
	loc = None
	if 'loc' in request.args: loc = location[request.args['loc']]
	signout_all(loc)
	return jsonify(status='OK')

def signout_all(loc=None):
	st = Student.select(Student, LogEntry).join(LogEntry).where(LogEntry.c_in == True)
	if loc is not None: st = st.where(LogEntry.location == loc)
	for s in st: sign_in(s, False)

def signout_task():
	if Settings.get().auto_sign_out: signout_all()

periods.on_period_end.add(signout_task)
