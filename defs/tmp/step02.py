def register_in_globals(function):
    def mame(class_instance, *args, **kwargs):
        class_instance.__getattribute__(function.__name__)(*args, **kwargs)
    globals()[function.__name__] = mame
    return function


class InputType(object):
    def __init__(self, type_id, match_function, manipulate_function):
        self.type_id = type_id
        self.match_function = match_function
        self.manipulate_function = manipulate_function

    def match(self, string):
        # accepts string only
        return self.match_function(string)

    def get_arguments(self, string):
        return self.manipulate_function(string)


class State(object):
    def __init__(self, state_id, data_object):
        self.state_id = state_id
        self.data_object = data_object
        self.next_rule = {}

    # def add_next_rule(self, state_id, input_type_id, next_state_id, data_object_function, *args, **kwargs):
    def add_next_rule(self, state_id, input_type_id, next_state_id, data_object_function):  # , *args, **kwargs):
        mame = {}
        # mame['side_effect'] = lambda: data_object_function(self.data_object, *args, **kwargs)
        mame['side_effect'] = data_object_function  # lambda: data_object_function(self.data_object, *args, **kwargs)
        mame['next_state_id'] = next_state_id

        self.next_rule[(state_id, input_type_id)] = mame

    def next(self, input_type_id, *args, **kwargs):
        self.next_rule[self.state_id, input_type_id]['side_effect'](*args, **kwargs)
        self.state_id = self.next_rule[self.state_id, input_type_id]['next_state_id']


class StateMachine(object):
    def __init__(self):
        self.input_type_list = []
        self.state = 0

    def _match_input(self, string):
        for input_type in self.input_type_list:
            if input_type.match(string):
                return input_type

        # add new input_type when reached here
        assert False

    def update(self, string):
        matched_input_type = self._match_input(string)
        arguments_for_update = matched_input_type.get_arguments(string)
        self.state.next(matched_input_type, arguments_for_update)


class MetricsData(object):
    def __init__(self):
        self.data = {}
        self.available_index = 0

    def _add_timestamp(self, new_timestamp):
        if self.data.get('timestamp'):
            if new_timestamp > self.data['timestamp'][-1]:
                self.data['timestamp'] += [new_timestamp]
            else:
                pass
        else:
            self.data['timestamp'] = new_timestamp

    def _update_available(self):
        lens = [len(self.data[key]) for key in self.data]
        self.available_index = max(self.available_index, min(lens) - 1)

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
    def identity(self, *args, **kwargs):
        pass

    def extract_data_after_timestamp(self, timestamp):
        index_is_after = [ts > timestamp for ts in self.data['timestamp']]
        first_index_after_timestamp = index_is_after.index(True)
        result = {}
        for key in self.data:
            result[key] = self.data[key][first_index_after_timestamp, self.available_index]

