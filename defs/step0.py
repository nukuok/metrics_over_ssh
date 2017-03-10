import os
import os.path
import shutil
import stat
import sys
import os

import time

from commands import getstatusoutput
from logging import getLogger
from logging import FileHandler
from logging import Formatter
from logging import StreamHandler
from logging import INFO
from logging import ERROR


def to_continue(info="Error !!!"):
    print("===========")
    print(info)
    c = 0
    while c not in ["y", "n"]:
        c = raw_input("Continue [y/n]? ")
        print("===========")
        if c == "y":
            break
        elif c == "n":
            sys.exit(1)
    return 0


class Workspace(object):
    def _gen_workspace_path(self):
        # self.timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        # self.ws_name = "ws_%s" % self.timestamp
        self.ws_name = "workspace"
        self.ws_path = os.path.join(self.under_dir, self.ws_name)

        if not os.path.exists(self.ws_path):
            os.mkdir(self.ws_path)

        return 0

    def _gen_log_path(self):
        self.log_name = "preparation.log"
        self.log_path = os.path.join(self.ws_path, self.log_name)

        self.logger = getLogger(self.ws_name)
        self.logger.setLevel(INFO)

        log_format = Formatter("%(asctime)s - %(name)s:[%(levelname)s]: %(message)s")

        handler = FileHandler(self.log_path)
        handler.setLevel(INFO)
        handler.setFormatter(log_format)
        self.logger.addHandler(handler)

        handler_shell = StreamHandler()
        handler_shell.setLevel(ERROR)
        handler_shell.setFormatter(log_format)
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
            self.logger.info("Workspace generated or using existing workspace.")
            self.workspace_gen = 0
            return 0


class SubWorkspace(Workspace):
    def check_hosts(self, host_list):
        ping_command = "ping -c 1 -t 2 %s"
        results = [getstatusoutput(ping_command % host) for host in host_list]
        status = [output[0] for output in results]
        return status

    def _make_sub_hosts(self):
        check_result = self.check_hosts(self.host_list)
        self.valid_hosts = []
        for ii, value in enumerate(check_result):
            host = self.host_list[ii]
            if value == 0:
                self.logger.info("host added: %s" % host)
                self.valid_hosts += [host]
            else:
                self.logger.error("host unreachable: %s" % host)
                to_continue()

    def _host_name_replace(self, hostname):
        return hostname.replace(".", "_")

    def generate_subworkspace(self, monitor_name, host_list):
        assert self.workspace_gen == 0

        self.timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        # self.sub_ws_name = "monitor_since_%s" % self.timestamp
        # self.sub_ws_name = "monitor_%s" % monitor_name
        self.sub_ws_name = "monitor_%s" % (monitor_name + "_" + self.timestamp)
        self.sub_ws_path = os.path.join(self.ws_path, self.sub_ws_name)

        if os.path.exists(self.sub_ws_path):
            to_continue("%s already exists. Will overwrite." % self.sub_ws_path)
        else:
            os.mkdir(self.sub_ws_path)

        self.host_list = host_list
        self._make_sub_hosts()
        # for host in self.valid_hosts:
        #     os.mkdir(os.path.join(self.sub_ws_path,
        #                           self._host_name_replace(host)))

        self.logger.info("Sub workspace %s Generated." % self.sub_ws_path)
        self.subworkspace_gen = 0
        return 0


class PrepareStep1Script(SubWorkspace):
    def _load_template(self):
        self.template_sh = "template.sh"
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(self.script_dir, self.template_sh)

        with open(template_path, "r") as fid:
            template_context = fid.readlines()

        return template_context

    def _to_add0_block_title(self, title):
        block_title_line = "#### %s ####\n"
        return [block_title_line % title]

    def _to_add1_mkdir(self):
        mkdir_line_template = "mkdir ${run_path}/%s\n"
        return [mkdir_line_template % host for host in self.valid_hosts]

    def _to_add2_expect_ssh(self):
        from monitor_commands import commands as cmds
        expect_ssh_line_template = '${sub_ws}/expect-ssh.sh %s ${password} "%s" > ${run_path}/%s/%s &\n'
        self.logger.info("Generating expect expect-ssh commands.")
        self.logger.info("Valid hosts: %s" % str(self.valid_hosts))
        # self.logger.info("Fetching commands: %s" % str(cmds))

        return [expect_ssh_line_template % (host,
                                            cmds[cmd]['command'],
                                            host,
                                            cmds[cmd]['output'])
                for cmd in cmds for host in self.valid_hosts]

    def _to_add3_pid_info(self):
        cmd_line = ['ps aux | grep expect-ssh | grep -v grep | tr -s " " | cut -d " " -f 2,14,17 |' +
                    'sort --key=2,3 > ${run_path}/process_pid']
        return cmd_line

    def generate_step1_script(self):
        assert self.subworkspace_gen == 0

        self.step1_script_name = "step1_start_monitor.sh"
        self.step1_script_path = os.path.join(self.sub_ws_path, self.step1_script_name)

        with open(self.step1_script_path, "w") as fid:
            context = (self._load_template() +
                       self._to_add0_block_title("make host dirs") +
                       self._to_add1_mkdir() +
                       self._to_add0_block_title("fetching metrics") +
                       self._to_add2_expect_ssh() +
                       self._to_add0_block_title("PID info") +
                       self._to_add3_pid_info())

            for line in context:
                fid.write(line)

        shutil.copy(os.path.join(self.script_dir, "expect-ssh.sh"), self.sub_ws_path)

        st = os.stat(self.step1_script_path)
        os.chmod(self.step1_script_path, st.st_mode | stat.S_IEXEC)

        self.logger.info("step1 script generated: %s" % self.step1_script_path)
        self.step1_script_gen = 0
        return 0
