mkdir logs
sudo ./SuperStore/bin/gunicorn -w 1 app:app --bind=0.0.0.0:80 --access-logfile logs/devel_logs.txt --log-level=debug &
