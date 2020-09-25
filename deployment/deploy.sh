#! /bin/bash
#
# The crawler project is deployed to the crawler
# management service script

prefix=`cd $(dirname $0);pwd`
config_file="${prefix%/*}/scrapy.cfg"
project_name=`sed -n '/^project.*$/p' $config_file |awk '{print $NF}'`

# Modify configuration file
sed -i 's/^#.*6800\/$/url=http:\/\/localhost:6800\//g' $config_file
sed -i 's/^\[deploy\]$/\[deploy:localhost\]/g' $config_file

# Deploying reptiles to management tools
pid1=`ps aux|grep scrapy|grep -v grep|awk '{print $2}'`
pid2=`cat ${prefix}/pids/scrapyd.pid`

if [ $pid1 -eq $pid2 ];then
    scrapyd-deploy localhost -p $project_name
else
    echo "scrapyd service not started"
fi
