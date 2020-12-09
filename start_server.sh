sudo /home/ubuntu/SuperStore/SuperStore/bin/gunicorn app:app --bind=0.0.0.0:80 --access-logfile logs/devel_logs.txt --log-level=debug
