class GraphData(object):
    def __init__(self, graph_list, title="",
                 metrics_filter=lambda x: True,
                 graph_type="plot",
                 modify_key_filter=lambda x: False,
                 modify_value=lambda x: x):
        self.title = title
        self.metrics_filter = metrics_filter
        self.modify_key_filter = modify_key_filter
        self.modify_value = modify_value
        self.graph_type = graph_type
        graph_list.extend([self])

    def get_output(self, metrics):
        self.data_dict = {key: [float(value) for value in metrics[key]] for key in metrics if self.metrics_filter(key)}
        self.data_dict_renew = {}
        for key in self.data_dict:
            new_key = self.modify_key_filter(key)
            if new_key:
                self.data_dict_renew[new_key] = [self.modify_value(value) for value in self.data_dict[key]]
            else:
                self.data_dict_renew[key] = self.data_dict[key]

        self.data_dict_renew["title"] = self.title
        self.data_dict_renew["graph_type"] = self.graph_type
        return str(self.data_dict_renew).replace("'", '"')

graph_list = []

graph_cpu_usage = GraphData(graph_list, graph_type="fill", title="CPU Usage",
                            metrics_filter=lambda x: ("CPU-all" in x) and ("%" in x))

graph_mem_usage = GraphData(graph_list, graph_type="fill", title="Memory Usage",
                            metrics_filter=lambda x: x in ["kbswpused", "kbswpfree", "kbcached",
                                                           "kbbuffers", "kbmemused", "kbmemfree"],
                            modify_key_filter=lambda x: x.startswith("kb"),
                            modify_value=lambda x: x / 1000)
graph_runq = GraphData(graph_list, title="Number of run queue",
                       metrics_filter=lambda x: x in ["runq-sz"])

graph_process = GraphData(graph_list, title="Number of process created",
                       metrics_filter=lambda x: x in ["proc/s"])

graph_swap = GraphData(graph_list, title="Swap", metrics_filter=lambda x: x in ["pswpin/s", "pswpout/s"])

graph_page = GraphData(graph_list, title="Page", metrics_filter=lambda x: x in ["pgpgin/s", "pgpgout/s"])

graph_context_switch = GraphData(graph_list, title="Context switch", metrics_filter=lambda x: x in ["cswch/s"])

graph_packet_rt = GraphData(graph_list, title="Packet I/O", metrics_filter=lambda x: "xpck" in x and not("lo" in x))

graph_network_rt = GraphData(graph_list, title="Network I/O", metrics_filter=lambda x: "xkB" in x and not("lo" in x))

graph_disk_io = GraphData(graph_list, title="Disk I/O (sector/s)", metrics_filter=lambda x: "dev" in x and "_sec/s" in x)

graph_disk_service_time = GraphData(graph_list, title="Disk Service Time", metrics_filter=lambda x: "dev" in x and "svctm" in x)

graph_disk_util = GraphData(graph_list, title="Disk Util", metrics_filter=lambda x: "dev" in x and "%util" in x)

