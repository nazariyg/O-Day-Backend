#!/bin/bash -e

sshkey=/Users/nazariyg/Documents/[Projects]/Emma/[Server]/id_rsa

dst=/home/nazariyg/emma
dstuserhost=nazariyg@emma
dstport=22

ssh -i $sshkey -p $dstport $dstuserhost <<EOF
    cd $dst/uwsgi
    . ../emma_venv/bin/activate
    ./re
    deactivate
EOF
