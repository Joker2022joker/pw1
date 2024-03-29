#! /usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import SafeConfigParser as ConfigParser
from os.path import expanduser, dirname
from logging import getLogger
from xdg.BaseDirectory import load_first_config

class ConfParser(ConfigParser):
    # FIXME i couldnt get the constructor to accept defaults in any way
    defaults = {
        'debug': {
            'encrypt':'on'},
        'main': {
            'db':'wallet.asc',
            'input_kill_0x0a': "on",
            'output_kill_0x0a': "on"}}

    def __init__(self,path):
        # one config ought to be enough for everyone
        ConfigParser.__init__(self)

        if path is not None:
            self.read([path])

        for s,kv in self.defaults.items():
            # set default values into config
            if not self.has_section(s):
                self.add_section(s)

            for k, v in kv.items():
                if not self.has_option(s,k): self.set(s,k,v)


from argparse import ArgumentParser as AP
def arg_parser(**kwargs):
    kwargs["description"]="""A tool for accessing your gpg-secured passwords database"""
    p = AP(**kwargs)

    add_gp = lambda x: x.add_argument("nodes",type=str,metavar='node',nargs='+',help='in sequence forms a tree path identifying a resource with password')

    subp = p.add_subparsers(dest="command")
    ps = {}
    ps['get'] = subp.add_parser("get")

    ps['set'] = subp.add_parser("set")

    ps['new'] = subp.add_parser("new")

    ps['new'].add_argument('-f','--force',help="force overwriting existing password with a new one and check the node path exists",action='store_true',required=False)
    ps['new'].add_argument('-a','--attribute',required=False,action='store_true',help='if used, node argument is used as name of new attribute')
    ps['new'].add_argument('--stdin',required=False,action='store_true',help='do not generate new value but read it from stdin, applicable only to node types that have a generator')

    ps['list'] = subp.add_parser('list')
    ps['list'].add_argument('-a','--attribute',required=False,action='store_true',help='List node types')
    ps['list'].add_argument("nodes",type=str,metavar='node',nargs='*',help='in sequence forms a tree path identifying a resource')

    ps['rm'] = subp.add_parser('rm')

    ps['info'] = subp.add_parser('info')

    ps['search'] = subp.add_parser('search')
    ps['search'].add_argument("node_value", type=str)

    [add_gp(ps[i]) for i in ["get","set","new","rm"]]

    ps['dump'] = subp.add_parser('dump', help=(
        'Dump data into filesystem structure understood by passwordstore.org'
    ))
    ps['dump'].add_argument('output_dir', type=str)

    return p

class App(object):
    conf_parser=ConfParser
    xdg_resource = 'cpk'

    def __init__(self,argv):
        self._argv = argv
        self.__init_logging()
        self._init_db()

    _args = None
    @property
    def args(self):
        if self._args is None:
            p = arg_parser(prog=self._argv[0])
            self._args = p.parse_args(self._argv[1:])

        return self._args

    def __init_logging(self):
        log_cnf = load_first_config(self.xdg_resource,"logging.ini")

        if log_cnf is not None:
            from logging.config import fileConfig
            fileConfig(log_cnf)

        getLogger("%s_%s" % (__name__, self.__class__.__name__,)).debug("logging init")

    _cnf = None
    @property
    def conf(self):
        if self._cnf is None:
            cnf = load_first_config(self.xdg_resource,"config.ini")
            if cnf is None:
                import cpk, sys
                msg = "missing config.ini in $XDG_CONFIG_HOME\nyou " \
                    "can find example files in %s/data/configs" % dirname(cpk.__file__)
                print(msg, file=sys.stderr)
                exit(1)

            self._cnf = self.conf_parser(cnf)
        return self._cnf

    _command_prefix = "cpk.commands."
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
        from cpk.model import init_db
        init_db(self._get_db(),self)

    def __call__(self):
        c = self.command()
        c()

def main():
    from sys import argv
    App(argv)()
