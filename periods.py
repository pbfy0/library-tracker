import datetime
import bisect
import threading
from db import Period, db
import cron

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i + n]

def get_current_period(t):
	b = 0
	with pt_lock:
		b = bisect.bisect_right(period_times, t.time())
	if b == 0 or b == len(period_times): return -1
	return b // 2

def get_current_time():
	return datetime.datetime.now()

def update_period_times(tt):
	with db.atomic(), pt_lock:
		period_times[:] = tt
		Period.delete()
		for a, b in chunks(tt, 2):
			Period.create(start_time=a, end_time=b)
	cr.update_ev(get_cron())
cr = None
def load_period_times():
	pt = []
	with db.atomic():
		for i in Period.select():
			pt.append(i.start_time)
			pt.append(i.end_time)
	with pt_lock:
		period_times[:] = pt
	cr = cron.Cron(get_cron())
	cr.start()

def get_cron():
	ret = []
	with pt_lock:
		for _, p in chunks(period_times, 2):
			ret.append((p, on_end))
	return ret

def on_end():
	print('on_period_end')
	for i in on_period_end:
		i()

on_period_end = set()
tt = datetime.time
pt_lock = threading.Lock() # should really be a rwlock...
period_times = []

load_period_times()

#[
#	tt(8,00), tt(8,50),
#	tt(8,55), tt(9,40),
#	tt(9,45), tt(10,42),
#	tt(10,47), tt(11,22),
#	tt(11,27), tt(12,12),
#	tt(12,17), tt(13,2),
#	tt(13,7), tt(13,52),
#	tt(13,57), tt(14,42),
#	tt(14,47), tt(15,32),
#]
