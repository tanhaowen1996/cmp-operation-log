#!/bin/bash

WEB_PORT=${WEB_PORT:=8000}
WEB_CONCURRENCY=${WEB_CONCURRENCY:=3}
MAX_REQUESTS=${MAX_REQUESTS:=5000}

cd /app


if [ $# -eq 0 ]; then
  echo "Usage: start.sh [PROCESS_TYPE](server/worker/notification_server)"
else
  PROCESS_TYPE=$1
fi

function start_server() {
    echo "Start server..."

    if [ "$DEBUG" = "1" ]; then
      python manage.py runserver 0.0.0.0:$WEB_PORT
    else
      gunicorn operation_log.asgi \
        -b :$WEB_PORT \
        -k uvicorn.workers.UvicornWorker \
        -w $WEB_CONCURRENCY \
        --max-requests $MAX_REQUESTS
    fi
}

function start_notification_server() {
  echo "Start rabbitmq notification server ..."

  python manage.py notification_server
}


function main() {
  case "$PROCESS_TYPE" in
    "notification_server")
      start_notification_server
      ;;
    *)
      start_server
      ;;
  esac
}

main
