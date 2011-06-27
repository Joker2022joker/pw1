#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser as ConfigParser
from os.path import expanduser
from logging import getLogger

class ConfParser(ConfigParser):
    # FIXME i couldnt get the constructor to accept defaults in any way
    defaults = {
        'debug': {
            'encrypt':'on'},
        'main': {
            'password_generator': 'apg',
            'db_path':expanduser('~/.config/cpk/wallet.asc'),
            'input_kill_0x0a': "on",
            'output_kill_0x0a': "on"}}

    def __init__(self,path):
        # one config ought to be enough for everyone
        ConfigParser.__init__(self)

        if path is not None:
            self.read([path])

        lgr = getLogger("ConfigParser")


        for (s,kv) in self.defaults.iteritems():
            # set default values into config
            lgr.debug(s)
            if not self.has_section(s):
                self.add_section(s)

            for k, v in kv.iteritems():
                lgr.debug("k: {0} v: {1}".format(k, v))
                if not self.has_option(s,k): self.set(s,k,v)


from argparse import ArgumentParser as AP
def arg_parser(**kwargs):
    kwargs["description"]="""A tool for accessing your gpg-secured passwords database"""
    p = AP(**kwargs)

    p.add_argument('-d','--debug',action='store_true',required=False)
    p.add_argument('-c','--config',type=str,required=False)
    p.add_argument('--no-config',action='store_true',default=False,required=False)
    p.add_argument('--input-kill-0x0a',action='store_false',default=None,required=False)
    p.add_argument('--output-kill-0x0a',action='store_false',default=None,required=False)

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

    [add_gp(ps[i]) for i in ["get","set","new"]]

    return p

class App(object):
    conf_parser=ConfParser

    def __init__(self,argv):
        self._argv = argv
    
    _args = None
    @property
    def args(self):
        if self._args is None:
            p = arg_parser(prog=self._argv[0])
            args = p.parse_args(self._argv[1:])

            if args.no_config:
                args.config = None
            else:
                cnf_path = None
                if args.config:
                    from os.path import isfile
                    if not isfile(args.config):
                        print "config does not exists"
                        exit(1)

                    cnf_path = args.config

                if cnf_path is None :
                    if args.debug:
                        cnf_path = '~/.config/cpk/development.ini'
                    else:
                        cnf_path = '~/.config/cpk/config.ini'

                args.config = expanduser(cnf_path)

            self._args = args

        return self._args

    _cnf = None
    @property
    def conf(self):
        if self._cnf is None:
            from logging.config import fileConfig
            if self.args.config is not None:
                fileConfig(self.args.config)

            from logging import getLogger
            lgr = getLogger('cpk.args')
            lgr.debug(self.args)

            self._cnf = self.conf_parser(self.args.config)
            self.conf_after_load()

        return self._cnf

    def conf_after_load(self):
        # load some configs and set them into args if not set
        # the other way around may be better:
        #   simple rule: if an option can be in config, use it from config
        #   argparser could show reasonable defaults
        #   there would be no "race condition" as in - have config already been loaded or are we getting data from argparser only?
        for _type,opts in {bool: {"main":["input_kill_0x0a","output_kill_0x0a"]}}.iteritems():
            for section,names in opts.iteritems():
                [setattr(self._args,name,self.conf.getboolean(section,name)) for name in names if _type is bool and getattr(self._args,name) is None]
                    

        from logging import getLogger
        lgr = getLogger('cpk.args')
        lgr.debug(self.args)

    _command_prefix = "commands."
    def command(self):
        command = __import__(self._command_prefix+self.args.command,globals(),locals(),[self.args.command])
        command = getattr(command,"Command")
        c = command()
        c.app = self
        return c

    def _init_db(self):
        from model import init_db
        init_db(self.conf.get('main','db_path'))

    def __call__(self):
        self._init_db()
        # ^ this also ensures config has been read before calling the command
        c = self.command()
        c()
