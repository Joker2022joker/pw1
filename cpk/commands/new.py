#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace, ResourceExists
from model import Node, session, Attribute

class Command(IFace):
    def new_pwd(self):
        from subprocess import Popen, PIPE
        pgen = self.conf.get('main','password_generator')
        p = Popen(pgen.split(" "),stdout=PIPE)
        p.wait()
        return p.stdout.read()[:-1]

    def _run(self,args):
        if args.force and args.stdin:
            from .. import ContradictingArgs
            raise ContradictingArgs("-f --stdin")

        if args.attribute:
            a = Attribute()
            a.name = args.nodes.pop()

            if not args.nodes == []:
                a.descrption = args.nodes.pop()

            session.add(a)
            from sqlalchemy.exc import IntegrityError
            try:
                session.commit()
            except IntegrityError:
                self.die("IntegrityError, attribute name not unique?")

        else:
            Node.get(self.tokenize_nodes(),create=True)


            passwd = Node()
            passwd.attribute = Attribute.get('password')
            # ^ FIXME: hardcoded

#            p = Password.get(args.nodes,create=True)
#
#            if p.password is not None and p.password is not '':
#                # if there is password and it is non-empty string
#                if not args.force:
#                    # do nothing, unless user enforces overriding
#                    raise ResourceExists()
#
            if args.stdin:
                pwd = self.input()
            else:
                pwd = self.new_pwd()

            passwd.value = self.encrypt(pwd)
            session.commit()

            if not args.stdin:
                self.output(pwd)
