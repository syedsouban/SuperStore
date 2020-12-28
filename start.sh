<<<<<<< HEAD
date=$(date '+%Y-%m-%d')
if [ ! -d ./logs/ ] 
then
    mkdir -p logs
fi

sudo ./SuperStore/bin/gunicorn app:app -w 2 --bind=0.0.0.0:80 --access-logfile ./logs/$date.txt --log-level=debug &
=======
mkdir logs
sudo ./SuperStore/bin/gunicorn --worker-class eventlet -w 1 app:app --bind=0.0.0.0:8080 --access-logfile logs/devel_logs.txt --log-level=debug &
>>>>>>> dev
