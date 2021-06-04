from EMAN2 import EMArgumentParser


class E3ArgumentParser(EMArgumentParser):

    def __init__(self, prog=None,usage=None,description=None,epilog=None,parents=[],formatter_class=EMArgumentParser.HelpFormatter,prefix_chars='-',fromfile_prefix_chars=None,argument_default=None,conflict_handler='error',add_help=True,allow_abbrev=True):
        super(EMArgumentParser, self).__init__(prog=prog,usage=usage,description=description,epilog=epilog,parents=parents,formatter_class=formatter_class,prefix_chars=prefix_chars,fromfile_prefix_chars=fromfile_prefix_chars,argument_default=argument_default,conflict_handler=conflict_handler,add_help=add_help,allow_abbrev=allow_abbrev)
