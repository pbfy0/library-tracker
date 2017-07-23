import threading
import queue
import bisect
import atexit
import os
import weakref

import datetime

class _bisect_key:
	def __init__(self, val, k):
		self.val = val
		self.k = k
	def __getitem__(self, idx):
		return self.k(self.val[idx])
	def __len__(self):
		return len(self.val)
def _fix_qi(qi, day):
	return [datetime.datetime.combine(day, qi[0]), qi[1]]

class Cron:
	instances = weakref.WeakSet()
	@staticmethod
	def on_time_change():
		for i in Cron.instances:
			i.time_change = True
			i.ev.set()
	def __init__(self, ev):
		self.q = queue.Queue()
		self.ev = threading.Event()
		self.thread = None
		self._update_ev(ev)
		self.exit = False
		self.time_change = False
		Cron.instances.add(self)
	def update_ev(self, ev):
		a = self.thread is not None and self.thread.is_alive()
		if a: self.stop()
		self.clear_queue()
		self._update_ev(ev)
		if a: self.start()
	def clear_queue(self):
		while True:
			try:
				self.q.get(block=False)
			except queue.Empty:
				break
	def _update_ev(self, ev=None):
		if ev is None: ev = self.ev_l
		self.ev_l = ev
		st = datetime.datetime.now().time()
		idx = bisect.bisect(_bisect_key(ev, lambda x: x[0]), st)
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(1)
		for i in range(idx, len(ev)): self.q.put(_fix_qi(ev[i], today))
		for i in range(idx): self.q.put(_fix_qi(ev[i], tomorrow))
	def _thr(self):
		prev_t = None
		while True:
			nx = self.q.get()
			if nx[0] != prev_t:
				td = nx[0] - datetime.datetime.now()
				print('waiting for', td.total_seconds())
				if self.ev.wait(max(td.total_seconds(), 0)):
					self.ev.clear()
					if self.time_change:
						self.time_change = False
						self.clear_queue()
						self._update_ev()
						continue
					if self.exit:
						self.exit = False
						break
				prev_t = nx[0]
			nx[1]()
			nx[0] = datetime.datetime.combine(nx[0].date() + datetime.timedelta(1), nx[0].time())
			self.q.put(nx)
		self.ev.clear()
	def stop(self):
		self.exit = True
		self.ev.set()
		self.thread.join()
		atexit.unregister(self.stop)
	def start(self):
		self.thread = threading.Thread(target=self._thr, daemon=True)
		self.thread.start()
		atexit.register(self.stop)

if os.name == 'nt':
	import win_tctrack
	win_tctrack.start_monitor_thread(Cron.on_time_change)
