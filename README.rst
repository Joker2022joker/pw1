====
CPK
====

An Awesome Password Keeper

Features
=========
* CPK itself is just a simple python CLI user-interface for password storage, encryption and generation
* Password encrypting with your favorite encryption method
* Password generating with your favorite generator
* That's right, it doesn't care about shit. Just configure your backends


Configuration
===============
TODO

Usage
=====
To generate and store a new password for something interesting
::

    cpk new something interesting

You say, you already have a password?
just follow with a
::

    echo "password" | cpk set something interesting

or use
::

    echo "password" | cpk new --stdin something interesting

instead

How about an url?
It really doesnt matter, the resource_id can be arbitrary. However, for forward
compatibility with a planned formfiller it is a good idea to have urls in a common
"namespace" and keep in one format, like so
::

    cpk get url com domain username

But I have multiple accounts there!
::

    cpk get url com domain other_username

I also want to store information about how to retrieve the password just in case.
::

    cpk new -a retrieval_email
    echo "trojita@blesmrt.net" | cpk new --stdin url com domain user retrieval_email=
    cpk get url com domain user retrieval_email=

Installation
=============
::
    git clone
    cd cpk
    python setup.py install
    # copy config.ini to $XDG_CONFIG_HOME/cpk/ from example configs
    # and set up your config

what you need to configure
-----------------------------
* main.password_generator
* attributes.password
* the rest should be fine in default

Note, that currently it is designed to work with gnupg with configured
default-recipient-self


Dependencies
============
* py-gnupg ( http://py-gnupg.sourceforge.net/ )
* sqlalchemy ( http://py-gnupg.sourceforge.net/ ) developed on 0.6
* argparse ( http://pypi.python.org/pypi/argparse )
* pyxdg ( http://www.freedesktop.org/wiki/Software/pyxdg )

Tests
========
* You need an environment with installed cpk itself as the acceptance tests operates on the installed executable
* *The tests must be run on testing user* as it uses XDG as in normal operation
* The user needs to have prepared ~/.gnupg directory. For noninteractivity with prepared key without passord and configured default-recipient-self

You can prepare this by eg.
::

    virtualenv ~/.cpkenv
    source ~/cpkenv/bin/activate
    python setup.py install


* Then just execute run_tests.sh # $PWD agnostic
