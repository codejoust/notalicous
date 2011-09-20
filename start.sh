#!/bin/bash
close_server(){
  PROC=$(pgrep uwsgi)
  #kill $PROC
  echo "shutting down #$PROC"
}
trap close_server INT
cd /home/ec2-user/projs/notalicous 
killall uwsgi
if [ $? != 0 ]; then
	echo 'Starting Server...'
else
	echo 'restarting server.'
fi

SERV_PATH=../libs/uwsgi/uwsgi-0.9.6.8/uwsgi

if [ "$1" == "loud" ]
then
$SERV_PATH -L --socket /tmp/notalicous.sock --chmod-socket --module notalicous --pythonpath $(pwd)
else
$SERV_PATH -L --socket /tmp/notalicous.sock --chmod-socket --module notalicous --pythonpath $(pwd) -L &> /dev/null&
fi
