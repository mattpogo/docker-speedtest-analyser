#!/usr/bin/env bash
echo "Starting run.sh"

cat /var/www/html/config/crontab.default > /var/www/html/config/crontab

if [[ ${CRONJOB_SCHEDULE} && ${CRONJOB_SCHEDULE-x} ]]; then
    echo "using cron schedule"
    sed -i -e "s;0 \* \* \* \*;${CRONJOB_SCHEDULE};g" /var/www/html/config/crontab
elif [[ ${CRONJOB_ITERATION} && ${CRONJOB_ITERATION-x} ]]; then
    echo "using cron iteration"
    sed -i -e "s/0/*\/${CRONJOB_ITERATION}/g" /var/www/html/config/crontab
fi
cat /var/www/html/config/crontab
crontab /var/www/html/config/crontab

echo "Starting Cronjob"
crond -l 0 -f >/dev/null 2>&1 &

echo "Starting nginx"
exec nginx -g "daemon off;"

exit 0;