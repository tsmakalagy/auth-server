#!/bin/sh
# wait-for.sh

set -- "$@"
timeout=15
waitfor=$1
shift
cmd="$@"

until nc -z "$waitfor" || [ $timeout -eq 0 ]; do
  echo "waiting for $waitfor, $timeout remaining"
  timeout=$((timeout-1))
  sleep 1
done

if [ $timeout -eq 0 ]; then
  echo "timeout waiting for $waitfor"
  exit 1
fi

exec $cmd