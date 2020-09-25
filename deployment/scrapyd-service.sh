#! /bin/bash
#
# Crawler project management backgroud service start script

# Font color
red='\e[1;31m'
green='\e[1;32m'
yellow='\e[1;33m'
blue='\e[1;34m'
nc='\e[0m'

# Configuration of project path log files
prefix=`cd $(dirname $0);pwd`
scrapyd="${prefix%/*}/venv/Scripts/scrapyd"
pidfile="${prefix}/pids/scrapyd.pid"
logfile="${prefix}/logs/scrapyd.log"

# Ensure that logs and pids directory exist
[ ! -d ${prefix}/pids ] && mkdir -p ${prefix}/pids
[ ! -d ${prefix}/logs ] && mkdir -p ${prefix}/logs

options="--pidfile=$pidfile --logfile=$logfile"
#options="--logfile=$logfile"

message(){
    case $1 in
        info)
            printf "${green}INFO${nc}: $2\n";;
        error)
            printf "${red}ERROR${nc}: $2\n";;
        warn)
            printf "${yellow}WARN${nc}: $2\n";;
    esac
}


start(){
    if [ -f $pidfile ];then
        msg='The scrapyd service is already running!'
        message warn "$msg"
        exit 0
    else
        $scrapyd $options 2>&1 &
        rst=$?
    fi

    if [ $rst -eq 0 ];then
        msg="Start scrapyd service Done"
        message info "$msg"
    else
        msg="Start scrapyd service Failed"
        message error "$msg"
    fi
}


stop(){
    if [ -f $pidfile ];then
        cat $pidfile| xargs kill -9 &> /dev/null
        msg="Stop scrapyd service Done"
        rm -f $pidfile
        message info "$msg"
        exit 0
    else
        msg="The scrapyd service has stoped"
        message warn "$msg"
    fi
}


status(){
    netstat -tunpl| grep 6800 &> /dev/null
    if [ -f $pidfile -o $? -eq 0 ];then
        msg="The scrapyd service is running"
    else
        msg="The scrapyd service is stoped"
    fi
}


case "$1" in
    start)
        start;;
    stop)
        stop;;
    restart)
        stop && sleep 1 && start;;
    status)
        status;;
    *)
        msg="Usage: sh $0 start| restart| stop| status"
        message info "$msg"
    ;;
esac
