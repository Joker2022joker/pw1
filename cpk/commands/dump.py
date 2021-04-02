#! /usr/bin/env python
# -*- coding: utf-8 -*-

from . import Command as IFace
from cpk.model import Attribute, session, Node, Edge
from cpk import exc

from pathlib import Path
import os
import traceback
import io

from pprint import pprint

class Command(IFace):
    def parent(self, node):
        xs = session.query(Edge).filter_by(lower_node=node).all()
        if not xs:
            assert False, f"no parent edge for {node}"

        if len(xs) > 1:
            assert False, f"{node} has multiple parents"

        edge = xs.pop()
        parent = edge.higher_node
        if not parent:
            assert False, f"Parent node of {node} referenced by {edge} doesn't exist"

        return parent

    def fq_node(self, node):
        fq = [node]

        while node.id != 1:
            up = self.parent(node)
            if up in fq:
                raise RuntimeError(f"self referencing node {up}")

            if up.id == 1:
                break
            else:
                fq.insert(0, up)
                node = up

        return fq

    def fmt_fq(self, fq):

        xs = list(fq)
        pwd = xs.pop()
        assert pwd.value.startswith('-----BEGIN PGP'), f"leaf not pwd"

        return "/".join(f'{node.value}' for node in xs)

    def __call__(self):
        basepath = self.app.args.output_dir

        attrs = session.query(Attribute).all()
        attrs = {x.name: x for x in attrs}
        # pprint(attrs)

        nodes = session.query(Node).all()
        leafs = (x for x in nodes if session.query(Edge).filter_by(higher_node=x).count() == 0)

        for i, x in enumerate(leafs):
            fq_node = self.fq_node(x)
            path = basepath + '/' + self.fmt_fq(fq_node)
            if x.attribute.name == 'p':
                path += '.gpg'
            else:
                path += f'.attrs/{x.attribute.name}'

            path = Path(path)

            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('w') as f:
                    f.write(x.value)
            except Exception as e:
                print(fq_node)

        print(f"Leaf count: {i}")
