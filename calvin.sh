#! /bin/bash

echo $1

case $1 in
    'ifconfig')     ssh calvin $1;;
    'interfaces')   ssh calvin netstat -i;;
    'routes')       ssh calvin netstat -r;;
    'df')           ssh calvin $1 -H;;
    'ps')           ssh calvin ps uwax;;
    'password')     ssh calvin cat /etc/passwd;;
esac
