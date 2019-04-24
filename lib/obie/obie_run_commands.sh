#!/bin/bash

while read command;
do
    set -- ${command//./ }
    obie $2 config write
    obie $2 terraform $1 $3

done < /src/obie/lib/obie/commands.in