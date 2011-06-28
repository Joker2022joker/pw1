Cooperative Password Keeper
===========================

because it cooperates with other programs and therefore also with the user.
	... umm, and because i couldn't come up with a better name

A "generic" password keeper that offers/requires you to do the encryption,
asking you for password, managing your authenticated session or storing
pictures of cute cats securely is broken by design.

A few notes for start:
	currently, passwords are the only encrypted data in the wallet
	cpk is currently regarded as prototype only and highly experimental
	db schema is very likely to change in the future
	if you do want use cpk, you are advised to use vcs on the wallet after every use of cpk

How does it work?
=================

The idea is essentialy that any password can be attached to a leaf node in
a tree where the path from root node to the leaf node accurately identifies any
kind of resource the password belongs to while making very little assumptions about the
nodes semantic.

Assumptions we do are optional, unobtrusive and configurable (or will be).

It does not do any encryption/decryption by itself. It uses only your existing
infrastructure to do this. However, currently is supported only gnupg.

Fundamental data
================
| What we actually need to store is
|	(resource_id, password) tuple
|
| where
|	password is just a string
|	resource_id
|		may be
|			completely arbitraty id
|			(url,username) tuple
|
|		is n-tuple of strings
|		provides flexibility for unusual use cases as long as they can be represented by a n-tuple

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
| Currently, that's what attributes are for.
|	cpk new -a retrieval_email
|	echo "trojita@blesmrt.net" | cpk set -a retrieval_email url com domain user
|	cpk get -a retrieval_email url com domain user

TODO
====
rename/del command

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

simply rules for accessing args/config

figure out how to encrypt whole db on exit and decrypt the db on start of program and feed the decrypted data into memory db
