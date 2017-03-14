import os
import re

from commands import getstatusoutput

from step2_2 import MetricsData
from step2_2 import gen_sar_anaylzer
from step2_4_graph import graph_list


class ReportGenerator(object):
    def __init__(self):
        pass

    def _add_to_dict(self, target_dict, keys, value):
        if len(keys) == 1:
            target_dict[keys[0]] = target_dict.get(keys[0], []) + [value]
        else:
            target_dict[keys[0]] = target_dict.get(keys[0], {})
            self._add_to_dict(target_dict[keys[0]], keys[1:], value)

    def startup(self):
        self.ws_path = os.path.join(os.getcwd(), "workspace")

        self.ws_structure, self.sar_list = self.get_dir_structure(self.ws_path)
        self.sar_data = []
        self.sar_data_until_line = []
        self.sar_analyzers = []
        for ii in range(len(self.sar_list)):
            self.sar_data += [MetricsData()]
            self.sar_data_until_line += [0]
            self.sar_analyzers += [gen_sar_anaylzer(self.sar_data[ii])]

    def get_dir_structure(self, ws_path):
        path_format = re.compile("(monitor_[0-9a-zA-Z_-]*)/(run_[0-9a-zA-Z_-]*)/([0-9a-z\.-]*)")

        mame_dict = {}
        mame_list = []
        count = 0
        walker = os.walk(ws_path)
        for path, dirs, files in walker:
            matched = path_format.match(path[len(ws_path):].lstrip("/"))
            if matched and "sar.txt" in files:
                self._add_to_dict(mame_dict, [matched.group(1), matched.group(2), matched.group(3)], count)
                mame_list += [os.path.join(path, "sar.txt")]
                count += 1

        return mame_dict, mame_list

    def newest_report_existed(self, id):
        target_sar = self.sar_list[id]
        target_report = os.path.join(os.path.dirname(target_sar), "report.html")
        if not(os.path.exists(target_report)):
            return False
        else:
            ts_time = float(os.getmtime(target_sar))
            tr_time = float(os.getmtime(target_report))
            return tr_time > ts_time

    def gen_report(self, id):
        target_sar = self.sar_list[id]
        target_content = getstatusoutput("cat %s" % target_sar)[1].split("\n")
        for line in target_content:
            self.sar_analyzers[id].update(line.strip("\r"))

    def gen_all_report(self):
        for ii in range(len(self.sar_list)):
            if not(self.newest_report_existed(ii)):
                self.gen_report(ii)

    def show_list(self):
        for monitor in self.ws_structure:
            print("%s:" % monitor)
            for run in self.ws_structure[monitor]:
                print("==>  %s:" % run)
                for node in self.ws_structure[monitor][run]:
                    print("------>  %s: %s" % (node,
                                               self.ws_structure[monitor][run][node]))

if __name__ == '__main__':
    rg = ReportGenerator()
    rg.startup()
    rg.gen_all_report()
    # rg.show_list()
    result_template = "var data=[%s];"
    print(result_template % ",".join([graph.get_output(rg.sar_data[0].data) for graph in graph_list]))
