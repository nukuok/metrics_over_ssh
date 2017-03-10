import os
import os.path
import time

from commands import getstatusoutput
from logging import getLogger
from logging import FileHandler
from logging import StreamHandler
from logging import INFO
from logging import ERROR


class Workspace(object):
    def _gen_workspace_path(self):
        # self.timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        # self.ws_name = "ws_%s" % self.timestamp
        self.ws_name = "workspace"
        self.ws_path = os.path.join(self.under_dir, self.ws_name)

        assert (not os.path.isdir(self.ws_path))
        os.mkdir(self.ws_path)

        return 0

    def _gen_log_path(self):
        self.log_name = "run.log"
        self.log_path = os.path.join(self.ws_path, self.log_name)

        self.logger = getLogger(self.ws_path)

        handler = FileHandler(self.log_path)
        handler.setLevel(INFO)
        self.logger.addHandler(handler)

        handler_shell = StreamHandler()
        handler_shell.setLevel(ERROR)
        self.logger.addHandler(handler_shell)

        return 0

    def generate_workspace(self, under_dir):
        if not os.path.isdir(under_dir):
            print("Failed: %s doesn't exist or isn't a directory." % under_dir)

            return 1
        else:
            self.under_dir = under_dir
            self._gen_workspace_path()
            self._gen_log_path()

            return 0


class SubWorkspace(Workspace):
    def check_hosts(host_list):
        ping_command = "ping -c 1 -t 2 %s"
        results = [getstatusoutput(ping_command % host) for host in host_list]
        status = [output[0] for output in results]
        return status

    def make_sub_
