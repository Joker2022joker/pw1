Roadmap
========
Interfaces
------------
*	readline (fs like - ls, mkdir, mv), (suprsedes tab-completion)
*	FUSE fs (supersedes readline?)
*	ncurses (mc like?)
*	argv - non-interactive (current)

	*	consistency (see `Command Types`_)
		same things, usage depends on context
		::

			nodes, filters
			attributes, node types

*	node globbing

storage
-------
* XML file

	* this way, we get simple full one-time en/decryption
	* our attributes would map nicely on xml attribute(s)

	* node access/search may use xml utilities (so nothing to learn, besides the xml path/query/whatnot)

* SQLite

	* `full encryption` will require graph traversal

backends
--------
*	provide a way to re-encrypt all data
	rationale: encryption key changes

*	full encryption

	* what is the cost of doing so? (see `storage`)

*	searching [1]_

	* DFS/BFS might be switched based on attribute type, benefits?

*	multiple password generators
	rationale: some passwords is good to remember well

Data model
------------
*	paths aliasing
	rationale: resources sharing passwords, SSO

*	after_save hook
	rationale: commiting changes with dvcs

*	attribute relations
	rationale: eg. password attribute can not be followed by any further node (maybe a comment could)


Inter-program communication
---------------------------
*	claim X selection (copypasta)
	rationale: make sure password can be pasted once only

Features
----------
*	network attrbutes and ability to recognize current network

*	memory locking (swapping protection)
	is anyone running this on unecnrypted pc?

Further projects
-------------------
*	integration with browser form-fillers

Fundamental data
================
::

    Basicly we need to store (resource_id,password)
      where
          resource_id = 1*n ( Node )

    Node = (type, name)
      where
          name = ALPHA | DIGIT
          type = Attribute.id

    Attribute = (name,type)
       where
            name = ALPHA | DIGIT
            short_name = ALPHA | DIGIT
            type = "chained" | "additional" ;

                ; chained may follow each other
                ; additional must occur only once on a path
                ; this may be completely replaced with parent type restrictions

        can be eg.
          chained = [arbitrary_resource,domain]
          additional = [user,scheme,attribute]

    Then we can have graphs
      arbitrary_resource -> arbitratry_resource -> password
      arbitrary_resource -> domain -> domain -> domain -> scheme -> user -> password

.. ffs, why does there has to be empty line to get rid off README.rst:42: (ERROR/3) Unexpected indentation.
   and why

Command Types
=============
::

    Commands can be separated to those which
        create filters just from command line node path
            These translates node path as expected

            these are:
                mv
                rm
                list
                set

        attach attribute_type filter
            these are little tricky in that if node path does not end with attr= a filter is added to get commonly wanted result
            so if you wanna go for the password, but identify the last node just by attribute type, you need to specify password_type= explicitly

            these are:
                new <nodes>
                    default password_attr= is attached when searching for the goal node

                get <nodes>
                    an empty filter is added, which means getting the next child of the node path specified (currently assumes password has no siblings)

        not applicable to:
            info

Sources
=======
.. [1] http://wiki.python.org/moin/PythonGraphApi
