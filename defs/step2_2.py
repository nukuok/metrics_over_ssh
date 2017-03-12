import re

from step2_1 import InputType
from step2_1 import State
from step2_1 import StateMachine


def register_in_globals(function):
    def mame(class_instance, *args, **kwargs):
        class_instance.__getattribute__(function.__name__)(*args, **kwargs)
    globals()[function.__name__] = mame
    return function


class MetricsData(object):
    def __init__(self):
        self.data = {}
        self.available_index = 0
        self.metrics_names = []
        self.metrics_suffix = ''

    def _add_timestamp(self, new_timestamp):
        if self.data.get('timestamp'):
            if new_timestamp != self.data['timestamp'][-1]:
                self.data['timestamp'] += [new_timestamp]
            else:
                pass
        else:
            self.data['timestamp'] = [new_timestamp]

    def _update_available(self):
        lens = [len(self.data[key]) for key in self.data]
        # self.available_index = max(self.available_index, min(lens) - 1)
        self.available_index = min(lens)  # - 1

    @register_in_globals
    def add_data(self, *args, **kwargs):
        for key in kwargs:
            if key == 'timestamp':
                self._add_timestamp(kwargs['timestamp'])
            else:
                if self.data.get(key):
                    self.data[key] += [kwargs[key]]
                else:
                    self.data[key] = [kwargs[key]]

        self._update_available()

    @register_in_globals
    def update_current_metrics_names(self, *args, **kwargs):
        if kwargs.get("uppercase"):
            # "XX:XX:XX AM DEVICE xxx/s xxx/s" <===== for here
            self.metrics_suffix = kwargs["uppercase"]
            self.metrics_names = args
        else:
            # "XX:XX:XX AM DEVICE xxx/s xxx/s" <===== for here
            self.metrics_suffix = ""
            self.metrics_names = args

    @register_in_globals
    def add_data_blindly(self, *args, **kwargs):
        if self.metrics_suffix:
            # "XX:XX:XX AM DEVICE xxx/s xxx/s"
            # "XX:XX:XX AM all 0.0 0.0"   <===== for here
            metrics_names = ("%s-%s-%s" % (metrics_name, self.metrics_suffix, args[0])
                             for metrics_name in self.metrics_names)
            data_dict = dict(zip(metrics_names, args[1:]))
            data_dict["timestamp"] = kwargs["timestamp"]
            self.add_data(**data_dict)
        else:
            # "XX:XX:XX AM xxx/s xxx/s xxx/s"
            # "XX:XX:XX AM 0.0 0.0 0.0"   <===== for here
            data_dict = dict(zip(self.metrics_names, args))
            data_dict["timestamp"] = kwargs["timestamp"]
            self.add_data(**data_dict)

        self._update_available()

    @register_in_globals
    def remove_current_metrics_names(self, *args, **kwargs):
        self.metrics_suffix = ""
        self.metrics_names = []

    @register_in_globals
    def identity(self, *args, **kwargs):
        pass

    def extract_data_after_timestamp(self, timestamp):
        index_is_after = [ts > timestamp for ts in self.data['timestamp']]
        first_index_after_timestamp = index_is_after.index(True)
        result = {}
        for key in self.data:
            result[key] = self.data[key][first_index_after_timestamp:self.available_index]

        return result

    def extract_data_after_index(self, index, keys):
        result = {}
        for key in keys:
            if key == "timestamp":
                result[key] = self.data[key][index:self.available_index]
            else:
                result[key] = [float(value) for value in self.data[key][index:self.available_index]]

        return result


def gen_sar_anaylzer(sar_data):
    format01 = re.compile("^[0-9]{2}:[0-9]{2}:[0-9]{2} [\ ]*([A-Z]+) (.*)$")
    format02 = re.compile("^([0-9]{2}:[0-9]{2}:[0-9]{2}) [\ ]*([0-9a-z/]*.*)$")

    def function01(string):
        matched = format01.match(string)
        result_list = matched.group(2).split(" ")
        result_list = [result for result in result_list if result != '']
        result_dict = {"uppercase": matched.group(1)}
        return (result_list, result_dict)

    def function02(string):
        matched = format02.match(string)
        result_list = matched.group(2).split(" ")
        result_list = [result for result in result_list if result != '']
        result_dict = {"timestamp": matched.group(1)}
        return (result_list, result_dict)

    input00_default = InputType(0, lambda string: True, lambda string: ([], {}))
    input01_log_timestamp_uppercase = InputType(1, lambda string: format01.match(string), function01)
    input02_log_timestamp_lowercase = InputType(2, lambda string: format02.match(string), function02)
    input03_empty_line = InputType(3, lambda string: string == '', lambda string: ([], {}))

    state = State(0, sar_data)
    # state1 = State(-1, sar_data)

    state.add_next_rule(0, 0, 0, identity)
    state.add_next_rule(0, 1, -1, update_current_metrics_names)
    state.add_next_rule(0, 2, -1, update_current_metrics_names)
    state.add_next_rule(0, 3, 0, identity)

    state.add_next_rule(-1, 0, 0, identity)
    state.add_next_rule(-1, 1, 0, identity)
    state.add_next_rule(-1, 2, -1, add_data_blindly)
    state.add_next_rule(-1, 3, 0, identity)

    sar_analyzer = StateMachine([input01_log_timestamp_uppercase,
                                 input02_log_timestamp_lowercase,
                                 input03_empty_line,
                                 input00_default],
                                state)
    return sar_analyzer


if __name__ == '__main__':
    sar_data = MetricsData()
    sar_analyzer = gen_sar_anaylzer(sar_data)
