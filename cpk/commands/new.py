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

    def attribute(self):
        a = Attribute()
        a.name = self.args.nodes.pop()

        if self.args.nodes:
            a.descrption = args.nodes.pop()

        session.add(a)
        from sqlalchemy.exc import IntegrityError

        try:
            session.commit()
        except IntegrityError:
            self.die("IntegrityError, attribute name not unique?")

    def get_pwd(self):
        if self.args.stdin:
            return self.input()

        return self.new_pwd()


    def password(self):
        n = Node.get(self.tokens_2_filters(self.tokenize_nodes()),create=True)

        p = n.lower(attr='password')
        if p:
            passwd = p[0]
            if passwd.value and not self.args.force:
                raise ResourceExists()
        else:
            passwd = Node()
            passwd.attribute = Attribute.get('password')
            # ^ FIXME: hardcoded


        pwd = self.get_pwd()

        passwd.value = self.encrypt(pwd)
        n.add_child(passwd)

        session.add(passwd)
        session.commit()

        if not self.args.stdin:
            self.output(pwd)

    def _run(self,args):
        if args.force and args.stdin:
            from .. import ContradictingArgs
            raise ContradictingArgs("-f --stdin")

        if args.attribute:
            return self.attribute()

        self.password()
