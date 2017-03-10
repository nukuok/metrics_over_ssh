class CommandTemplate(object):
    def __init__(self, init_dict):
        self._dict = {}
        self._dict.command = init_dict["command"]
        self._dict.output_name = init_dict["output_name"]

    def gen_command(self, template):
        return template.safe_substitute(self._dict)
