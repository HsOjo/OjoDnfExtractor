class Terminal:
    def __init__(self, prompt='OjoTerminal> '):
        self._exit = False
        self._prompt = prompt

        self._cmds = {}

    def start(self):
        self.bind_function('help', self.print_help, {
            'cmd': {'type': str, 'null': True, 'help': 'command id in command list.'}
        }, 'show help message.')
        self.bind_function('exit', self.exit, {}, 'exit terminal.')

        cmds = self._cmds
        while not self._exit:
            input_str = input(self._prompt).strip()
            if input_str != '':
                input_args = input_str.split(' ')
                for i, v in enumerate(input_args):
                    input_args[i] = v.strip()

                cmd = cmds.get(input_args[0])
                if cmd is None:
                    print('input help to show command list.')
                else:
                    func = cmd.get('func')

                    if func is not None:
                        try:
                            func_args = input_args[1:]
                            param = cmd.get('param')
                            if param is not None:
                                for i, [k, v] in enumerate(param.items()):
                                    if i < len(func_args):
                                        func_args[i] = v['type'](func_args[i])
                                    elif not v.get('null', False):
                                        raise Exception('param: %s cannot be null.' % k)
                            func(*func_args)
                        except Exception as e:
                            print(e)

    def bind_function(self, cmd, func, param: dict, help):
        bind = {
            'func': func,
            'param': param,  # { 'type': str, 'null': True , 'help': 'help text'}
            'help': help,
        }
        self._cmds[cmd] = bind

    def set_prompt(self, prompt):
        self._prompt = prompt

    def usage(self, cmd_key):
        cmds = self._cmds
        cmd = cmds[cmd_key]
        usage = cmd_key

        type_str = lambda x: str(x)[8:-2]
        param = cmd.get('param')
        if param is not None:
            for k, v in param.items():
                null = v.get('null', False)
                usage += ' '
                p = '(%s)%s' % (type_str(v['type']), k)
                if null:
                    p = '[%s]' % p
                usage += p

        return usage

    def print_help(self, cmd_key=None):
        cmds = self._cmds
        if cmd_key is None:
            for k in cmds:
                print(self.usage(k))
        elif cmd_key in cmds:
            cmd = cmds[cmd_key]
            param = cmd['param']
            print('usage: ' + self.usage(cmd_key))
            for k, v in param.items():
                p_help = v.get('help')
                if p_help is not None:
                    print('\t\t%s: %s' % (k, p_help))
            print(cmd.get('help'))
        else:
            print('unknown command: %s' % cmd_key)

    def exit(self):
        self._exit = True
