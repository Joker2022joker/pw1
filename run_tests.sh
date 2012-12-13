#! /bin/sh

if [ "$1" = "-k" ]; then
	export KEEP_XDG="1"
fi

cd `dirname $0`
nosetests --all-modules
