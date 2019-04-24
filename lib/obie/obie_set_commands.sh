#!/bin/bash

IFS=',' read -ra str <<< "$1"
touch ./obie/lib/obie/commands.in
for obie_cmd in "${str[@]}";
do
    echo $obie_cmd >> ./obie/lib/obie/commands.in
done
