#!/bin/bash

usage() {
    echo "Usage: ./run_monitor.sh monitor_interval monitor_period"
    echo "       ---"
    echo "       [monitor_interval < monitor_period] should be satisfied"
    exit 1
}

if [ $# != 2 ] || ! [[ $1 =~ ^[0-9]+$ ]] ||  ! [[ $2 =~ ^[0-9]+$ ]] || [[ $1 -gt $2 ]] ; then
   usage
fi

interval=$1
times=$(( $2/$1 + 1))

run_at=$(date +"%Y-%m-%d_%H-%M-%S")
sub_ws=$(dirname "$0")
run_path=${sub_ws}/run_${run_at}

mkdir ${run_path}

echo -n "Password for ssh: "
read -s password

ln -fhs ${run_path} newest_run
