import peewee as p
from enum import Enum
import datetime

db = p.SqliteDatabase('tracker.db')

class per_type(Enum):
	NOT_FREE = 0
	STUDY_HALL = 1
	LUNCH = 2
	FREE_PERIOD = 3

class location(Enum):
	LIBRARY = 1

class _Model(p.Model):
	class Meta:
		database = db

deferred_log = p.DeferredRelation()
class Student(_Model):
	sid = p.BigIntegerField(primary_key=True)
	grade = p.SmallIntegerField()
	last_log = p.ForeignKeyField(deferred_log, null=True)
	def __repr__(self):
		return 'Student(sid={}, grade={}, last_log={})'.format(self.sid, self.grade, self.last_log.id)

class FreePeriod(_Model):
	student = p.ForeignKeyField(Student, related_name='free_periods')
	period = p.SmallIntegerField()
	cycle_days = p.SmallIntegerField()
	semester = p.SmallIntegerField()
	type = p.SmallIntegerField()
	def __repr__(self):
		return 'FreePeriod(student={}, period={}, cycle_days={:08b}, semester={}, type={})'.format(self.student, self.period, self.cycle_days, self.semester, per_type(self.type).name)

class LogEntry(_Model):
	student = p.ForeignKeyField(Student, related_name='log_entries')
	timestamp = p.DateTimeField(default=datetime.datetime.now)
	c_in = p.BooleanField()
	location = p.SmallIntegerField(null=True)
	def __repr__(self):
		return 'LogEntry(student={}, timestamp={}, c_in={}, location={})'.format(self.student, self.timestamp, self.c_in, self.location)

class Period(_Model):
	start_time = p.TimeField()
	end_time = p.TimeField()
	def __repr__(self):
		return 'Period(start_time={}, end_time={})'.format(self.start_time, self.end_time)

class Settings(_Model):
	auto_sign_out = p.BooleanField(default=True)
	

deferred_log.set_model(LogEntry)

db.connect()
db.create_tables((Student, FreePeriod, LogEntry, Period, Settings), True)

if len(Settings.select()) == 0:
	Settings.create()
