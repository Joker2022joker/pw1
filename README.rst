====
CPK
====

A (not so) Awesome Password Keeper

Features
=========
* Simplicity
    * CPK is just a CLI user-interface for password storage, cryptography and generation
    * Cryptography functions are delegated to `GnuPG <http://www.gnupg.org/>`_ but you can write backend for your other favorite crypto tool/method
    * Password generating is included for convenience and is configured as a shell command whose stdout is used
* Flexibility
    * you are free to identify resources to your passwords however you want as long as it fits into a graph with typed nodes.
    * Database backend is sqlite but accessed via `sqlalchemy <http://www.sqlalchemy.org/>`_, so any RDBMS is easily possible.
* `XDG <http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html>`_ support


Caveat Emptor
=============
*   Currently only the passwords are encrypted.
    ∴ resource paths are unencrypted

*   The UX is horrible but it works and is only thing I trust right now.

    * manually gitting after each wallet file change

    * manually running echo | xsel -b immediately after the passwd has
      been used

    * some commands take args weirdly (eg set) so I figured it's
      easier to use rm and new at the moment.

Usage
=====
First things first
::

The main idea is that you don't store passwords to websites or whatnot but generically resources, be it website, mail account or your safe in the wall behind a painting.

The format is basicaly::

    $ cpk <command> <resource>
    command = get | set | new | list`
    resource = <node_matcher> [<node_matcher>]`
    node_matcher = <attribute>=<node>`

So your resource identificators are stored as nodes in a graph.
Passwords are stored in the same graph always as a leaf node.

Each node can be assigned an attribute type.
In fact, nodes containing password, MUST be assigned password attribute.
This is because of some sanity checking as it would be very impractical to
treat password like a resource.

CPK must know what attribute name specifies password. That's what config
option `attributes.password` is for. So I'm gonna use name `p`
::

    [attributes]
    password = p

Now lets create the attribute in database
::

    cpk new -a p

And we are ready to store stuff

Save a password for something interesting
::

    echo "p4ssw0rd" | cpk new --stdin something interesting

Use read to prevent the password being written to history file
::

    read i; echo $i | cpk new --stdin foo

If you are creating a new password and have configured a password_generator, you could use just
::

    cpk new something interesting | xsel -b


Now you can get the password back with
::

    cpk get something interesting | xsel -b


For URLs I chose to use
::
    cpk new -a u # for marking nodes as usernames
    cpk get url com domain u=username

As it makes sense to me and will make searching easier. But you are free to
make up your own way.

In case you don't remember the path you used, there is
::

    cpk list urls com example

Which will print you list of children nodes and their attribute type.

When you are specifying a `node_matcher` you don't have to use the full form.
::
    cpk list urls com example u=

Which doesn't really make sense as user node would typically be always followed
by password but it may be handy in other cases.

Installation
=============

::

    git clone
    cd cpk
    python setup.py install
    # copy config.ini to $XDG_CONFIG_HOME/cpk/ from example configs
    # and set up your config


Configuration
=============================
What you need to set up yourself is

* main.password_generator
* attributes.password

the rest should be fine in default

Note, that currently it is designed to work with gnupg with configured
default-recipient-self.


Dependencies
============
* sqlalchemy
* argparse
* `pyxdg <http://www.freedesktop.org/wiki/Software/pyxdg>`_
