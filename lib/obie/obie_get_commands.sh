#!/bin/bash
obie_cmd=$(sed -n -e 's/.*<obie>\(.*\)<\/obie>.*/\1/p' <<< $(git log -1 --pretty=%B))
commit_hash=$(git log --pretty=format:'%H' -n 1)

if [[ -z "$obie_cmd" ]]
then
    echo "\$obie_cmd is empty"
else
    echo "\$obie_cmd is NOT empty"

    obie_cmd=$(echo ${obie_cmd//, /,} | tr -s " " .)
    version=$(date '+%Y.%m.%d-%H.%M.%S')
    curl -X POST -u dsirbu:daniel http://localhost:8083/job/obie/buildWithParameters?obie_commands=$obie_cmd\&obie_commit=$commit_hash\&version=$version
fi