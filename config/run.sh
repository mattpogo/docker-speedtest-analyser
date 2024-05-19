#!/usr/bin/env bash
echo "Starting run.sh"

cat /var/www/html/config/crontab.default > /var/www/html/config/crontab

if [[ ${CRONJOB_SCHEDULE} && ${CRONJOB_SCHEDULE-x} ]]; then
    echo "using cron schedule " ${CRONJOB_SCHEDULE}
    sed -i "s;0 \* \* \* \*;${CRONJOB_SCHEDULE};g" /var/www/html/config/crontab
elif [[ ${CRONJOB_ITERATION} && ${CRONJOB_ITERATION-x} ]]; then
    echo "using cron iteration " ${CRONJOB_ITERATION}
    sed -i "s;0;*/${CRONJOB_ITERATION};g" /var/www/html/config/crontab
fi
crontab /var/www/html/config/crontab

echo "Starting Cronjob"
crond -l 2 -f &

echo "Starting nginx"
exec nginx -g "daemon off;"

exit 0;