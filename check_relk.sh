#!/bin/bash -l
#check for elasticsearch, web front end, indexer, and shipper, redis

service_error=0
services_in_error=""
elastic_search=$(curl -s localhost:9200/_cluster/health?pretty | grep status | grep green | wc -l)
es_queue=$(curl -s localhost:9200/_cluster/pending_tasks?pretty | grep -e tasks -e priority | wc -l)
redis=$(ps awwux | grep redis-server | grep -v grep | wc -l)
indexer=$(ps awwux | grep logstash | grep indexer.conf | grep -v grep | wc -l)
shipper=$(ps awwux | grep logstash | grep shipper.conf | grep -v grep | wc -l)
kibana=$(ps awwux | grep kibana | grep -v grep | wc -l)
env > /home/nrpe/myenv.txt
for system in "redis" "indexer" "shipper" "elastic_search" "es_queue" "kibana"; do
 if [ ${!system} -ne 1 ]; then
    service_error=1    
    services_in_error="$services_in_error $system"
 fi
done

if [ $service_error -ne 0 ]; then
   echo "CRITICAL: RELK stack error with:$services_in_error"
   exit 2
else
   echo "OK: RELK stack appears to be fine"
   exit 0
fi
echo "WARNING: RELK stack, something is wrong with this nrpe script"
exit 1

