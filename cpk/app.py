#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser as ConfigParser
from os.path import expanduser
from logging import getLogger
from xdg.BaseDirectory import load_first_config

class ConfParser(ConfigParser):
    # FIXME i couldnt get the constructor to accept defaults in any way
    defaults = {
        'debug': {
            'encrypt':'on'},
        'main': {
            'password_generator': 'apg',
            'db':'wallet.asc',
            'input_kill_0x0a': "on",
            'output_kill_0x0a': "on"}}

    def __init__(self,path):
        # one config ought to be enough for everyone
        ConfigParser.__init__(self)

        if path is not None:
            self.read([path])

        for (s,kv) in self.defaults.iteritems():
            # set default values into config
            if not self.has_section(s):
                self.add_section(s)

            for k, v in kv.iteritems():
                if not self.has_option(s,k): self.set(s,k,v)


from argparse import ArgumentParser as AP
def arg_parser(**kwargs):
    kwargs["description"]="""A tool for accessing your gpg-secured passwords database"""
    p = AP(**kwargs)

    add_gp = lambda x: x.add_argument("nodes",type=str,metavar='node',nargs='+',help='in sequence forms a tree path identifying a resource with password')

    subp = p.add_subparsers(dest="command")
    ps = {}
    ps['get'] = subp.add_parser("get")
    ps['get'].add_argument('-a','--attribute',type=str,required=False,help='gets an attribute of nodes')

    ps['set'] = subp.add_parser("set")
    ps['set'].add_argument('-a','--attribute',type=str,required=False)

    ps['new'] = subp.add_parser("new")

    ps['new'].add_argument('-f','--force',help="force overwriting existing password with a new one and check the node path exists",action='store_true',required=False)
    ps['new'].add_argument('-a','--attribute',required=False,action='store_true',help='if used, node argument is used as name of new attribute')
    ps['new'].add_argument('--stdin',required=False,action='store_true',help='do not generate new pwd but read it from stdin')

    ps['list'] = subp.add_parser('list')
    ps['list'].add_argument('-a','--attribute',required=False,action='store_true')
    ps['list'].add_argument("nodes",type=str,metavar='node',nargs='*',help='in sequence forms a tree path identifying a resource')



    ps['info'] = subp.add_parser('info')

    [add_gp(ps[i]) for i in ["get","set","new"]]

    return p

class App(object):
    conf_parser=ConfParser
    xdg_resource = 'cpk'

    def __init__(self,argv):
        self._argv = argv
        self.__init_logging()
    
    _args = None
    @property
    def args(self):
        if self._args is None:
            p = arg_parser(prog=self._argv[0])
            self._args = p.parse_args(self._argv[1:])

            self._init_db()

            import re
            from model import Attribute, session
            attrs = [i.short_name for i in session.query(Attribute).all()]
            
            sre_parse_nodes = '^((?P<node_type>%s)=)?(?P<node_name>[a-zA-Z0-9]+)$' % "|".join(attrs)
            getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(sre_parse_nodes)
            sre_parse_nodes = re.compile(sre_parse_nodes)

            if self._args.nodes is not None:
                new_nodes = [sre_parse_nodes.match(i).groupdict().values()
                    for i in self._args.nodes]
                # ^ FIXME raises AttributeError on syntax error
                getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug(new_nodes)
                self._args.nodes = new_nodes

        return self._args

    def __init_logging(self):
        log_cnf = load_first_config(self.xdg_resource,"logging.ini")
        if log_cnf is None:
            raise Exception("no logging.ini")
            # FIXME handle this

        from logging.config import fileConfig
        fileConfig(log_cnf)
        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug("logging init")

    _cnf = None
    @property
    def conf(self):
        if self._cnf is None:
            cnf = load_first_config("cpk","config.ini")
            if cnf is None:
                raise Exception("no config.ini")

            self._cnf = self.conf_parser(cnf)
        return self._cnf

    _command_prefix = "commands."
    def command(self):
        command = __import__(self._command_prefix+self.args.command,globals(),locals(),[self.args.command])
        command = getattr(command,"Command")
        c = command()
        c.app = self
        return c

    def _get_db(self):
        db = self.conf.get('main','db')
        if not db == ':memory:':
            from xdg.BaseDirectory import save_data_path
            from os.path import join
            res_data_path = save_data_path(self.xdg_resource)
            db = join(res_data_path,db)

        return db

    def _init_db(self):
        from model import init_db
        init_db(self._get_db())

    def __call__(self):
        c = self.command()
        c()
