from multiprocessing import cpu_count
from os import environ
import sys


def max_workers():
    return cpu_count()


bind = '0.0.0.0:' + "4000"
max_requests = 1000
worker_class = 'gevent'
workers = max_workers()
# workers = 1
accesslog = '-'
errorlog = '-'
access_log_format = "%(t)s %(h)s %(m)s %(U)s %(s)s %(L)ss."
capture_output = True
