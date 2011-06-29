#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import create_engine, select, case, func

from sqlalchemy.orm import scoped_session, sessionmaker, relationship, MapperExtension, aliased, backref
from sqlalchemy.ext.declarative import declarative_base as d_b, declared_attr 
from sqlalchemy import Integer,Boolean,String,Text, Column, ForeignKey, BLOB
from sqlalchemy.schema import Table

Base = d_b()

session = None

nodes_to_nodes = Table('nodes_m2m', Base.metadata,
    Column('parent_id', Integer, ForeignKey('nodes.id')),
    Column('child_id', Integer, ForeignKey('nodes.id'))
)

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer,ForeignKey('attributes.id'))
    name = Column(String(256))

    children = relationship("Node",
                    secondary=nodes_to_nodes,
                    backref="parents")

    @staticmethod
    def get(nodes,create=False):
        global session
        if type(nodes) is not list:
            return nodes

        g = parent_id = parent =None

        create_new = False
        while len(nodes) > 0:
            # ^ FIXME: this and the whole while is probably counter-intuitive and just "wrong"
            i = nodes.pop(0)
            try:
                if create_new:
                    raise sa.orm.exc.NoResultFound()
                sql = session.query(Node).filter_by(name=i,parent_id=parent_id)
                g = sql.one()
                parent_id = g.id
            except sa.orm.exc.NoResultFound:
                if not create:
                    raise NoNode()

                if g is not None:
                    parent = g
                g = Node()
                g.name = i
                if parent is not None:
                    parent.children.append(g)
                else:
                    g.parent_id = None
                session.add(g)

        return g


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer,primary_key=True)
    name = Column(String(256),unique=True)
    short_name = Column(String(16),unique=True)

    @staticmethod
    def get(name):
        if type(name) is str:
           return session.query(Attribute).filter_by(name=name).one()

        return name

    @staticmethod
    def check_not_existing(name):
        try:
            Attribute.get(name)
            raise UniquenessFail()
        except sa.orm.exc.NoResultFound:
            return


class NoNode(Exception):
    pass

class NoPass(Exception):
    pass
    
class NoAttrValue(Exception):
    pass

class UniquenessFail(Exception):
    pass

def init_db(db_path):
    global session
    from os.path import expanduser
    db_path = expanduser(db_path)
    e =create_engine("sqlite+pysqlite:///"+db_path)
    session = scoped_session(sessionmaker(bind=e, autoflush=True))
    Base.metadata.bind = e
    Base.metadata.create_all()
