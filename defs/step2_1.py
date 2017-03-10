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
        self.next_rule[(self.state_id, input_type_id)]['side_effect'](self.data_object, *args, **kwargs)
        self.state_id = self.next_rule[self.state_id, input_type_id]['next_state_id']


class StateMachine(object):
    def __init__(self, input_type_list, state):
        self.input_type_list = input_type_list
        self.state = state

    def _match_input(self, string):
        for input_type in self.input_type_list:
            if input_type.match(string):
                # print(input_type.type_id)
                return input_type

        # add new input_type when reached here
        assert False

    def update(self, string):
        matched_input_type = self._match_input(string)
        arguments_for_update = matched_input_type.get_arguments(string)
        # self.state.next(matched_input_type, arguments_for_update)
        # print(arguments_for_update)
        self.state.next(matched_input_type.type_id, *arguments_for_update[0], **arguments_for_update[1])
