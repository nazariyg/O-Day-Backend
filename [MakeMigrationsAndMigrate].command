#!/bin/bash -e

srcparent=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
sshkey=/Users/nazariyg/Documents/[Projects]/Emma/[Server]/id_rsa

dst=/home/nazariyg/emma
dstuserhost=nazariyg@emma
dstport=22

$srcparent/[Push].command

ssh -i $sshkey -p $dstport $dstuserhost <<EOF
    cd $dst
    . emma_venv/bin/activate
    python manage.py makemigrations && python manage.py migrate
    deactivate
EOF

$srcparent/[Pull].command
