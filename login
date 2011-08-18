#!/bin/bash

instance_list=`euca-describe-instances | grep ^INSTANCE | grep running`
count=`echo "${instance_list}" | wc -l`
host=`echo "${instance_list}" | cut -f4`

if [ $count -eq "1" ]; then
  echo Connecting to ubuntu@$host
  ssh ubuntu@$host
else
  echo $host
fi

