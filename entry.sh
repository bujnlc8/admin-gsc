#!/bin/sh
gunicorn --preload -w 1 -b 0.0.0.0:5000 snow.wsgi:app -t 60 -k gevent --worker-connections 100  --error-logfile /log/snow_sys.log --access-logfile /log/http.log --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" "%(T)s" "%(D)s" "%(L)s"'
