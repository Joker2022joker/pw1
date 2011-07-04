Cooperative Password Keeper
===========================

because it cooperates with other programs and therefore also with the user.
	... umm, and because i couldn't come up with a better name

A "generic" password keeper that offers/requires you to do the encryption,
asking you for password, managing your authenticated session or storing
pictures of cute cats securely is broken by design.

A few notes for start:
	currently, node paths and attributes names are not encrypted in the wallet
	cpk is currently regarded as prototype only and highly experimental
	if you do want use cpk, you are advised to use vcs on the wallet after every use of cpk and check model.py for incompatible changes

How does it work?
=================

The idea is essentialy that any password can be attached to node in
a graph where the path from root node to the leaf node accurately identifies any
kind of resource the password belongs to while letting you care about the nodes semantics

It does not do any encryption/decryption by itself. It uses only your existing
infrastructure to do this. However, currently is supported only gnupg.

Fundamental data
================

| Basicly we need to store (resource_id,password)
|   where
|       resource_id = 1*n ( Node )
|
| Node = (type, name)
|   where
|       name = ALPHA | DIGIT
|       type = Attribute.id
|   
| Attribute = (name,type)
|    where
|       name = ALPHA | DIGIT
|       short_name = ALPHA | DIGIT
|       type = "chained" | "additional" ;
|           ; chained may follow each other
|           ; additional must occur only once on a path
|           ; this may be completely replaced with parent type restrictions
|
|   can be eg.
|       chained = [arbitrary_resource,domain]
|       additional = [user,scheme,attribute]
|
| Then we can have graphs
|   arbitrary_resource -> arbitratry_resource -> password
|   arbitrary_resource -> domain -> domain -> domain -> scheme -> user -> password


So how do you use it?
=====================

| To generate and store a new password for something interesting
|	cpk new something interesting
|
| You say, you already have a password?
| just follow with a
|	echo "password" | cpk set something interesting
| or use
|	echo "password" | cpk new --stdin something interesting
| instead
|
| How about an url?
| It really doesnt matter, the resource_id can be arbitrary. However, for forward
| compatibility with a planned formfiller it is a good idea to have urls in a common
| "namespace" and keep in one format, like so
|	cpk get url com domain username
|
| But I have multiple accounts there!
|	cpk get url com domain other_username
|
| I also want to store information about how to retrieve the password just in case.
|	cpk new -a retrieval_email
|	echo "trojita@blesmrt.net" | cpk new --stdin url com domain user retrieval_email=
|	cpk get url com domain user retrieval_email=

DEPENDENCIES
============
| py-gnupg ( http://py-gnupg.sourceforge.net/ )
| sqlalchemy ( http://py-gnupg.sourceforge.net/ ) developed on 0.6
| argparse ( http://pypi.python.org/pypi/argparse )
| pyxdg ( http://www.freedesktop.org/wiki/Software/pyxdg )

TODO
====
Use DFS for the first ordered part and BFS for the second unordered

Passwords of different strengths could be generated
    eg. some passwords is good to remember well
    
    this would require having Attributes Inheration and configurable Value Generator per Attribute

automatic aliasing
    eg. lets consider graph
        org1 - "urls" - domain1
        org2 - "urls" - domain2

    then we want to have automatic aliases
        urls - domain1 -> org1 - urls domain1
        urls - domain2 -> org2 - urls domain2

move/rename/del command

paths aliasing
	eg. path "url com example www john_doe" can also be accessed with path "iana ldap john_doe"

tab-completion on node paths

node globbing

after_save hook
	for commiting changes with dvcs?
		which in this case would probably be better use a nosql db in a file

integration with browser form-fillers
	not really part of _this_ project

handle copy-pasting
	using external utility like xsel will do for a while but is unsafe
	find a way how to handle this with cpk itself

lock memory against swapping
	kinda moot on encrypted swap

write unit/integration tests

use fixtures in tests instead of realying on their order

figure out how to encrypt whole db on exit and decrypt the db on start of program and feed the decrypted data into memory db

Try to use a graph lib for the heavy work [1]_

Implementation notes, drafts, etc
==================================
aliases
    special attribute alias that does not manifest in the entered path, it only points to another node
    or type of an edge
        so edge could be 
            default:   child follows parent
            alias:      parent points to child which should be used as for next lower neighbor lookup
    update: actually there is probably no need to do anything complicated, just create an edge

attributes could be restricted to be allowed only to follow certain types of attributes
    eg. most attributes cant follow password but attribute eg. "comment" could

Sources
=======
.. [1] http://wiki.python.org/moin/PythonGraphApi

