export PORT=5001
date=$(date '+%d%m%Y_%H_%M_%S');
log_file_name="${date}_${PORT}.log"
touch log_file_name
sudo ./SuperStore/bin/gunicorn --timeout=300 --worker-class eventlet -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/$log_file_name --log-level=debug &
#  --reload
# export PORT=5002
# sudo ./SuperStore/bin/gunicorn --timeout=300 --worker-class eventlet -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/devel_logs.txt --log-level=debug &
# export PORT=5003
# sudo ./SuperStore/bin/gunicorn --timeout=300 --worker-class eventlet -w 1 app:app -e PORT=$PORT --bind=127.0.0.1:$PORT --access-logfile logs/devel_logs.txt --log-level=debug &
