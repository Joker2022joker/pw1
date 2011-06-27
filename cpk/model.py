#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import create_engine, select, case, func

from sqlalchemy.orm import scoped_session, sessionmaker, relationship, MapperExtension, aliased, backref
from sqlalchemy.ext.declarative import declarative_base as d_b, declared_attr 
from sqlalchemy import Integer,Boolean,String,Text, Column, ForeignKey, BLOB

Base = d_b()

session = None

class NestedSetExtension(MapperExtension):
    def before_insert(self, mapper, connection, instance):
        if not instance.parent:
            instance.parent_id = None
        else:
            instance.parent_id = instance.parent.id


class Node(Base):
    __tablename__ = 'nodes'
    __mapper_args__ = {
        "extension":NestedSetExtension(),
        'batch':False
    }

    parent_id = Column(Integer,ForeignKey('nodes.id'))
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    password_id = Column(Integer,ForeignKey('passwords.id'))

    children = relationship("Node",backref=backref('parent',remote_side=id))
    password = relationship("Password",backref=backref("nodes",uselist=False))

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

class Password(Base):
    __tablename__ = 'passwords'
    id = Column(Integer,primary_key=True)
    password = Column(BLOB)

    @staticmethod
    def get(node,create=False):
        g = Node.get(node,create)

        if g.password_id:
           return session.query(Password).filter_by(id=g.password_id).one()

        if create:
            p = Password()
            g.password = p
            session.add(g)
            return p

        raise NoPass()


class Attribute(Base):
    __tablename__ = 'attributes'

    id = Column(Integer,primary_key=True)
    name = Column(String(256),unique=True)

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

class AttributeValue(Base):
    __tablename__ = 'attr_values'
    node_id = Column(Integer,ForeignKey('nodes.id'),primary_key=True)
    attr_id = Column(Integer,ForeignKey('attributes.id'),primary_key=True)
    value = Column(String(256))

    @staticmethod
    def get(attribute,node,create=False):
        attribute = Attribute.get(attribute)
        node = Node.get(node)

        try:
           return session.query(AttributeValue).filter_by(node_id=node.id,attr_id=attribute.id).one()
        except sa.orm.exc.NoResultFound:
            if not create:
                raise NoAttrValue()

            av = AttributeValue()
            av.node_id = node.id
            av.attr_id = attribute.id
            return av

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
