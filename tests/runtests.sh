#!/bin/bash
# estimated time to complete the tests is 30 minutes

cmd='fab bootmachine'
dirs=`ls -d */ | sed "s/logs\///g"`

# activate the bootmachine testing virtualenv
source ~/.virtualenvs/bootmachine/bin/activate

# run `fab bootmachine` in parallel for each and save the output in a log file
# sleep in between each call to avoid api abuse
for dir in $dirs; do
  mkdir -p logs/$dir
  sleep 7
  $activate && cd ./$dir && $cmd > ../logs/"$dir"bootmachine_`date +%H%M%S`.log &
done

# add the build names that didn't finish to fail log
# by finding the most recent build outputs that do not contain the success text
match='all servers are fully provisioned.'
for dir in $dirs; do
  lastlogfile=$(find ./logs/$dir -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
  if [ ! -z "(grep '$match' $lastlogfile -q)" ]; then
    echo $lastlogfile >> ./logs/fail.log
  fi
done
