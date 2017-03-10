import os
import re

from commands import getstatusoutput
from urlparse import parse_qs

from step2_2 import MetricsData
from step2_2 import gen_sar_anaylzer
from utils import RepeatedTimer


def _add_to_dict(target_dict, keys, value):
    if len(keys) == 1:
        target_dict[keys[0]] = target_dict.get(keys[0], []) + [value]
    else:
        target_dict[keys[0]] = target_dict.get(keys[0], {})
        _add_to_dict(target_dict[keys[0]], keys[1:], value)


def get_dir_structure(ws_path):
    path_format = re.compile("(monitor_[0-9a-zA-Z_-]*)/(run_[0-9a-zA-Z_-]*)/([0-9a-z\.-]*)")

    mame_dict = {}
    mame_list = []
    count = 0
    walker = os.walk(ws_path)
    for path, dirs, files in walker:
        matched = path_format.match(path[len(ws_path):].lstrip("/"))
        if matched and "sar.txt" in files:
            _add_to_dict(mame_dict, [matched.group(1), matched.group(2), matched.group(3)], count)
            mame_list += [os.path.join(path, "sar.txt")]
            count += 1

    return mame_dict, mame_list


def sar_data_update(sar_list, sar_data_until_line, sar_analyzers):
    for ii in range(len(sar_list)):
        total_line = int(getstatusoutput("wc -l %s" % sar_list[ii])[1].lstrip(" ").split(" ")[0])
        updated_lines = getstatusoutput("tail -n %d %s" %
                                        (total_line - sar_data_until_line[ii], sar_list[ii]))[1].split("\r\n")
        for line in updated_lines:
            sar_analyzers[ii].update(line)
            sar_data_until_line[ii] = total_line


def application(env, start_response):
    if env['PATH_INFO'] == "/":
        # index_contents = Path('html/index.html').read_text().encode()
        script_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_path, 'html/index.html'), 'r') as fid:
            index_contents = fid.read()
        length = str(len(index_contents))

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('HTTP-Version', 'HTTP/1.1'),
                                  ('Content-Type', 'text/html'),
                                  ('Content-Length', length)])
        return [index_contents]
    elif env['PATH_INFO'].startswith("/source/lists"):
        res_body = str(ws_structure).replace("'", '"').encode()

        print(res_body)
        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Type', 'application/json'),
                                  ('Content-Length', str(len(res_body)))])
        return [res_body]
    elif env['PATH_INFO'].startswith("/source/"):
        path_info = env['PATH_INFO'].split("/")
        data_id = int(path_info[2])
        assert path_info[3] == "status"

        query_string = parse_qs(env['QUERY_STRING'])
        items = query_string["items"][0].split(",")
        from_index = int(query_string["from_index"][0])
        res_body = str(sar_data[data_id].extract_data_after_index(from_index, items)).replace("'", '"').encode()

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Length', str(len(res_body)))])
        return [res_body]
    elif env['PATH_INFO'] == "/favicon.ico":
        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Length', '1')])
        return [b' ']
    else:
        if env['PATH_INFO'].endswith("js"):
            script_path = os.path.dirname(os.path.realpath(__file__))
            js_path = os.path.join(script_path, "html", env['PATH_INFO'].lstrip('/'))
            with open(js_path, 'r') as fid:
                js_contents = fid.read()

            length = str(len(js_contents.encode()))

            start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                      ('Content-Type', 'text/javascript'),
                                      ('Content-Length', length)])
            return [js_contents]
        elif env['PATH_INFO'].endswith("css"):
            script_path = os.path.dirname(os.path.realpath(__file__))
            css_path = os.path.join(script_path, "html", env['PATH_INFO'].lstrip('/'))
            with open(css_path, 'r') as fid:
                css_contents = fid.read()

            length = str(len(css_contents.encode()))

            start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                      ('Content-Type', 'text/css'),
                                      ('Content-Length', length)])
            return [css_contents]
        else:
            assert False


if __name__ == '__main__':
    ws_path = os.path.join(os.getcwd(), "workspace")

    ws_structure, sar_list = get_dir_structure(ws_path)
    sar_data = []
    sar_data_until_line = []
    sar_analyzers = []
    for ii in range(len(sar_list)):
        sar_data += [MetricsData()]
        sar_data_until_line += [0]
        sar_analyzers += [gen_sar_anaylzer(sar_data[ii])]

    sar_data_update(sar_list, sar_data_until_line, sar_analyzers)

    mame = RepeatedTimer(10, sar_data_update, sar_list, sar_data_until_line, sar_analyzers)
    try:
        mame.start()

        from wsgiref.simple_server import make_server

        port = 8888
        server = make_server('', port, application)
        print("Serving on port %d" % port)
        server.serve_forever()

    finally:
        mame.stop()

    # for ss in sar_data:
    #     print(len(ss.data[ss.data.keys()[0]]))
