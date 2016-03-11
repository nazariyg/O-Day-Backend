#!/bin/bash -e

srcparent=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
sshkey=/Users/nazariyg/Documents/[Projects]/Emma/[Server]/id_rsa

dst=/home/nazariyg/emma
dstuserhost=nazariyg@emma
dstport=22

$srcparent/[Push].command

ssh -i $sshkey -p $dstport -t $dstuserhost "cd $dst ; echo '. ~/.bashrc ; . s ; rm tmpbashrc ; clear' > tmpbashrc ; /bin/bash --rcfile tmpbashrc"

$srcparent/[Pull].command
