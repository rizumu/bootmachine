#!/bin/bash
dirs=`ls -d */ | sed "s/logs\///g"`
for dir in $dirs; do rm -f ./logs/$dir/* & done
rm -f ./logs/fail.log
