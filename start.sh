date=$(date '+%Y-%m-%d')
if [ ! -d ./logs/ ] 
then
    mkdir -p logs
fi

sudo ./SuperStore/bin/gunicorn app:app -w 2 --bind=0.0.0.0:80 --access-logfile ./logs/$date.txt --log-level=debug &
