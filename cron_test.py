import datetime
import cron
q = [((datetime.datetime.now() + datetime.timedelta(seconds=5)).time(), lambda: print('abc')), ((datetime.datetime.now() + datetime.timedelta(seconds=10)).time(), lambda: print('def'))]
c = cron.Cron(q); c.start()
import time
time.sleep(100)
