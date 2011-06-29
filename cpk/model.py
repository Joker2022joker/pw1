#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import create_engine, select, case, func

from sqlalchemy.orm import scoped_session, sessionmaker, relationship, MapperExtension, aliased, backref
from sqlalchemy.ext.declarative import declarative_base as d_b, declared_attr 
from sqlalchemy import Integer,Boolean,String,Text, Column, ForeignKey, BLOB
from sqlalchemy.schema import Table
from logging import getLogger

Base = d_b()

session = None

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer,ForeignKey('attributes.id'))
    value = Column(String(256),nullable=False)

    def higher_neighbors(self):
        parents = [x.higher_node for x in self.lower_edges]
        if parents is None or parents == [None]:
            raise NoNode()
        return parents

    def lower_neighbors(self):
        children = [x.lower_node for x in self.higher_edges]
        if children is None or children == [None]:
            # ^ FIXME: this is weird
            raise NoNode()
        return children

    def __repr__(self):
        return "<%s_%s_%s_%s>" % (self.__class__.__name__, self.id, self.attribute_id, self.value)

    @classmethod
    def root(self):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            return session.query(self).filter_by(id=1).one()
            # ^ FIXME: determine root node in a better way
        except NoResultFound:
            root = self()
            root.id = 1
            root.value = ""
            session.add(root)
            session.commit()
            return root

    def get_lower(self,node):
        for i in self.lower_neighbors():
            if i.attribute is None and i.value == node[1]:
                return i

        raise NoNode(node)

    def add_child(self,node):
        e =Edge(self,node)
        session.add(e)

    def add_parent(self,node):
        Edge(node,self)

    @classmethod
    def get(self,nodes,create=False):
#        if type(nodes) is not list:
#            return nodes

        last_node = self.root()
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(last_node)

        while not nodes == []:
            look_for = nodes.pop(0)
            getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(look_for)

            try:
                last_node = last_node.get_lower(look_for[1])
            except NoNode:
                if not create:
                    raise

                new_node = Node()
                new_node.value = look_for[1]
                last_node.add_child(new_node)
                last_node = new_node
                session.add(last_node)

        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(repr(last_node))
        return last_node

class Edge(Base):
    __tablename__ = 'edges'

    lower_id = Column(Integer, 
                        ForeignKey('nodes.id'), 
                        primary_key=True)

    higher_id = Column(Integer, 
                        ForeignKey('nodes.id'), 
                        primary_key=True)

    lower_node = relationship(Node,
                                primaryjoin=lower_id==Node.id, 
                                backref='lower_edges')
    higher_node = relationship(Node,
                                primaryjoin=higher_id==Node.id, 
                                backref='higher_edges')

    def __init__(self, higher, lower):
        self.lower_node = lower
        self.higher_node = higher


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer,primary_key=True)
    name = Column(String(16),unique=True,nullable=False)
    description = Column(String(256))

    nodes = relationship(Node, backref='attribute')

    @staticmethod
    def get(name):
        if type(name) is str:
           return session.query(Attribute).filter_by(name=name).one()

        return name

class NoNode(Exception):
    pass

class NoPass(Exception):
    pass
    
class NoAttrValue(Exception):
    pass

def init_db(db_path):
    global session
    from os.path import expanduser
    db_path = expanduser(db_path)
    e =create_engine("sqlite+pysqlite:///"+db_path)
    session = scoped_session(sessionmaker(bind=e, autoflush=True))
    Base.metadata.bind = e
    Base.metadata.create_all()
