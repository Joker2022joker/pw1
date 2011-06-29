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

DEPENDENCIES
============
| py-gnupg ( http://py-gnupg.sourceforge.net/ )
| sqlalchemy ( http://py-gnupg.sourceforge.net/ ) developed on 0.6
| argparse ( http://pypi.python.org/pypi/argparse )
| pyxdg ( http://www.freedesktop.org/wiki/Software/pyxdg )

Implementation notes
====================
get -a
    may specify target attribute we are looking for so it can be used regardless of attribute

aliases
    special attribute alias that does not manifest in the entered path, it only points to another node
    or type of an edge
        so edge could be 
            default:   child follows parent
            alias:      parent points to child which should be used as for next lower neighbor lookup

attributes could be restricted to be allowed only to follow certain types of attributes
    eg. most attributes cant follow password but attribute eg. "comment" could

TODO
====
automatic aliasing
    eg. lets consider graph
        org1 - "urls" - domain1
        org2 - "urls" - domain2

    then we want to have automatic aliases
        urls - domain1 -> org1 - urls domain1
        urls - domain2 -> org2 - urls domain2

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
