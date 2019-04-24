#!/bin/bash

command="$(echo $payload | jq .comment.body | sed -e 's/\"//g')"
commit_hash="$(echo $payload | jq .comment.commit_id | sed -e 's/\"//g')"
set -- $command
if [[ $1 == "obie" ]];
then
  obie_cmd=$(echo ${command//"obie "/} |  sed -e 's/\, /,/g' | tr -s " " .)
  version=$(date '+%Y.%m.%d-%H.%M.%S')
  curl -X POST -u dsirbu:daniel http://localhost:8083/job/obie/buildWithParameters?obie_commands=$obie_cmd\&obie_commit=$commit_hash\&version=$version
fi
