#!/bin/bash

instance_list=`euca-describe-instances | grep ^INSTANCE | grep running`
count=`echo "${instance_list}" | wc -l`
hosts=`echo "${instance_list}" | cut -f4`

for host in $hosts
do
  echo Connecting to ubuntu@$host
  ssh ubuntu@$host
  break
done

