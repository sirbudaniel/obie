#!/bin/bash
public_ip="localhost:8083"

# $1 jenkins username, $2 jenkins password
obie_trigger_url="http://$1:$2@${public_ip}/createItem?name=obie_trigger"
curl -s -XPOST $obie_trigger_url --data-binary @obie_trigger_config.xml -H "Content-Type:text/xml"

obie_url="http://$1:$2@${public_ip}/createItem?name=obie"
curl -s -XPOST $obie_url --data-binary @obie_config.xml -H "Content-Type:text/xml"
