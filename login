#!/bin/bash

instance_list=`euca-describe-instances | grep ^INSTANCE | grep running`
count=`echo "${instance_list}" | wc -l`

if [ $count -eq "1" ]; then
  host=`echo "${instance_list}" | cut -f4`
  echo Connecting to ubuntu@$host
  ssh ubuntu@$host
fi

