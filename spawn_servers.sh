export PORT=5001
sudo ./SuperStore/bin/gunicorn  -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/devel_logs.txt --log-level=debug &
export PORT=5002
sudo ./SuperStore/bin/gunicorn  -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/devel_logs.txt --log-level=debug &
export PORT=5003
sudo ./SuperStore/bin/gunicorn  -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/devel_logs.txt --log-level=debug &
