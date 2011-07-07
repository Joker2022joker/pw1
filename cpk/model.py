#! /usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Integer,Boolean,String,Text, Column, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import Table

from logging import getLogger

Base = declarative_base()

session = app = None

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer,ForeignKey('attributes.id'))
    value = Column(String(256),nullable=False)

    def __repr__(self):
        return "<%s_%s_%s_%s>" % (self.__class__.__name__, self.id, self.attribute_id, self.value)

    @classmethod
    def root(self):
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

        if not attr and not node:
            return nodes

        if attr.__class__ == Attribute:
            attr = attr.name

        
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug("%s %s"%(node,attr))

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
        """ Get exactly one node identified by filters which translates to a unique path in the graph """
        last_node = self.root()

        while filters:
            filter = filters.pop(0)

#            if filter['attr'].__class__ is Attribute:
#                filter['attr'] = filter['attr'].name

            matching_nodes = last_node.lower(**filter)

            if matching_nodes:
                if len(matching_nodes) > 1:
                    from exc import MatchedMultiple
                    raise MatchedMultiple(matching_nodes,last_node)

                last_node = matching_nodes[0]
            elif create:
                new_node = Node()
                if filter.has_key('node'):
                    new_node.value = filter['node']


                getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(filter)
                if filter['attr']:
                    if not filter['attr'].__class__ is Attribute:
                        filter['attr'] = Attribute.get(filter['attr'])

                    new_node.attribute = filter['attr']

                last_node.add_child(new_node)
                last_node = new_node
                session.add(last_node)
            else:
                raise NoNode(filter)

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

    @classmethod
    def magic_password_id(self):
        return self.__get_conf('password')

    @classmethod
    def __get_conf(self,name):
        from ConfigParser import NoSectionError, NoOptionError
        try:
            return app.conf.get('attributes',name)
        except (NoSectionError, NoOptionError):
            class FakeDefaultAttr(object):
                id = None
                name = ''
                description = None
            return FakeDefaultAttr()

    @classmethod
    def default(self):
        name = self.__get_conf('default')
        return Attribute.get(name)

    @staticmethod
    def get(name):
        if type(name) is str:
           return session.query(Attribute).filter_by(name=name).one()

        return name

    @property
    def generator(self):
        """ Returns value generator or None """

        if self.name == self.magic_password_id():
            return True

        return None

    @classmethod
    def password(self):
        """ returns special attribute password or None if not configured """
        if not self.magic_password_id():
            return None

        try:
            return self.get(self.magic_password_id())
        except NoResultFound:
            a = Attribute()
            a.name = self.magic_password_id()
            session.add(a)
            return a

    @property
    def one_per_higher_node(self):
        """
            Return True if the type is required to be only one per higher node
        """
        return self.name == self.magic_password_id()


class NoNode(Exception):
    pass

class NoPass(Exception):
    pass
    
class NoAttrValue(Exception):
    pass

def init_db(db_path,_app):
    global session
    global app

    app = _app

    from os.path import expanduser
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    db_path = expanduser(db_path)
    e =create_engine("sqlite+pysqlite:///"+db_path)
    session = scoped_session(sessionmaker(bind=e, autoflush=True))
    Base.metadata.bind = e
    Base.metadata.create_all()
