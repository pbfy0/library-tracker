from db import *
import csv
import sys
import re
import periods

mm={'LUNCH': per_type.LUNCH.value, 'STUDY PERIOD': per_type.STUDY_HALL.value}
pt = [
	tt(8,00), tt(8,50),
	tt(8,55), tt(9,40),
	tt(9,45), tt(10,42),
	tt(10,47), tt(11,22),
	tt(11,27), tt(12,12),
	tt(12,17), tt(13,2),
	tt(13,7), tt(13,52),
	tt(13,57), tt(14,42),
	tt(14,47), tt(15,32),
]

periods.update_period_times(pt)

with open(sys.argv[1], 'r', newline='') as csv_f:
	reader = csv.reader(csv_f)
	first_row = list(next(reader))
	frv = {v: k for k, v in enumerate(first_row)}
	seen_sids = set()
	for row in reader:
		sid = int(row[frv['Student_ID']])
		grade = int(row[frv['Grade']])
		us = None
		cycds = 0
		for cd in row[frv['StudentSchedule_CycleDays']].split(','):
			cycds |= 1<<(int(cd) - 1)
		sem = re.match('Semester (\d+)', row[frv['Term']]).group(1)
		with db.atomic():
			try:
				us = Student.get(Student.sid == sid)
				if sid not in seen_sids:
					FreePeriod.delete().where(FreePeriod.student == us).execute()
					seen_sids.add(sid)
				if us.grade != grade: us.grade = grade
			except p.DoesNotExist:
				us = Student.create(sid=sid, grade=grade)
			#print(us.id, cycds)
			FreePeriod.create(student=us, period=int(row[frv['Period']]), cycle_days=cycds, semester=int(sem), type=mm[row[frv['Course_Name']]])
