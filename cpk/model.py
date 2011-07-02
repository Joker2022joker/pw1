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
            root.value = "root"
            session.add(root)
            session.commit()
            return root

    def lower(self, **kwargs):
        return self._get('lower', **kwargs)

    def higher(self, **kwargs):
        return self._get('higher', **kwargs)

    def _get(self,dir,attr=None,node=None):
        edges = "%s_%s" % (dir,'edges')
        edge_attr = "%s_%s" % (dir, "node")
        nodes = [getattr(x,edge_attr) for x in getattr(self,edges)]

        if attr is None and node is None:
            return nodes

        if not node:
            filter = lambda x: x.attr.name == attr
        elif not attr:
            filter = lambda x: x.value == node
        else:
            filter = lambda x: x.value == node and x.attr.name == attr

        return [ x for x in nodes if filter(x) ]

    def add_child(self,node):
        e =Edge(self,node)
        session.add(e)

    def add_parent(self,node):
        Edge(node,self)

    @property
    def attr(node):
        """
            Always returns an Attribute

            If node has no attribute, default Attribute is returned
        """
        if node.attribute:
            return node.attribute
        
        return Attribute.default()

    @classmethod
    def get(self,filters,create=False):
        last_node = self.root()

        while filters:
            filter = filters.pop(0)

            matching_nodes = last_node.lower(**filter)

            if matching_nodes:
                if len(matching_nodes) > 1:
                    from exc import MatchedMultiple
                    raise MatchedMultiple(matching_nodes,last_node)

                last_node = matching_nodes[0]
            elif create:
                new_node = Node()
                new_node.value = filter['node']
                if filter['attr']:
                    new_node.attribute = Attribute.get(filter['attr'])

                last_node.add_child(new_node)
                last_node = new_node
                session.add(last_node)
            else:
                raise NoNode()

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
                                backref='higher_edges')
    higher_node = relationship(Node,
                                primaryjoin=higher_id==Node.id, 
                                backref='lower_edges')

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
    def default():
        return Attribute.get('default')
        # ^ FIXME: hardcoded

    @staticmethod
    def get(name):
        if type(name) is str:
           return session.query(Attribute).filter_by(name=name).one()

        return name

    @classmethod
    def password(self):
        """ returns special attribute password """
        return self.get('password')
        # ^ FIXME: hardcoded


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
