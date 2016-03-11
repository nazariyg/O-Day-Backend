#!/bin/bash -e

src=/home/nazariyg/emma
srcuserhost=nazariyg@emma
srcport=22

dstparent=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
sshkey=/Users/nazariyg/Documents/[Projects]/Emma/[Server]/id_rsa

syncexcl="--exclude=emma_venv --exclude=__pycache__ --exclude=staticroot --exclude=mediaroot --exclude=uwsgi/pid --exclude=uwsgi/uwsgi.log --exclude=.DS_Store --exclude=emma/log"
rsync -az $syncexcl -e "ssh -i $sshkey -p $srcport" $srcuserhost:$src $dstparent
