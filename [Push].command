#!/bin/bash -e

srcparent=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
src=$srcparent/emma
sshkey=/Users/nazariyg/Documents/[Projects]/Emma/[Server]/id_rsa

dstparent=/home/nazariyg
dst=/home/nazariyg/emma
dstuserhost=nazariyg@emma
dstport=22
dstuserown=nazariyg

syncexcl="--exclude=emma_venv --exclude=__pycache__ --exclude=staticroot --exclude=mediaroot --exclude=uwsgi/pid --exclude=uwsgi/uwsgi.log --exclude=.DS_Store --exclude=emma/log"
rsync -az $syncexcl --delete -e "ssh -i $sshkey -p $dstport" $src $dstuserhost:$dstparent

# findexcl="-not -path '*emma_venv*' -and -not -path '*uwsgi*' -and -not -path '*mediaroot*'"
# ssh -i $sshkey -p $dstport $dstuserhost <<EOF
#     chown -R $dstuserown:$dstuserown $dst
#     find $dst $findexcl -type d -print0 | xargs -0 chmod 755
#     find $dst $findexcl -type f -print0 | xargs -0 chmod 644
#     chmod u+x $dst/s $dst/u
# EOF
