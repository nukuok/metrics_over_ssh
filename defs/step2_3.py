import os
import re

from commands import getstatusoutput
from urlparse import parse_qs

from step2_2 import MetricsData
from step2_2 import gen_sar_anaylzer
from utils import RepeatedTimer


class Backend(object):
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

    def _add_to_dict(self, target_dict, keys, value):
        if len(keys) == 1:
            target_dict[keys[0]] = target_dict.get(keys[0], []) + [value]
        else:
            target_dict[keys[0]] = target_dict.get(keys[0], {})
            self._add_to_dict(target_dict[keys[0]], keys[1:], value)

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

    def sar_data_update_all(self, sar_list, sar_data_until_line, sar_analyzers):
        self.sar_data_update(sar_list, sar_data_until_line, sar_analyzers, range(len(sar_list)))

    def sar_data_update(self, sar_list, sar_data_until_line, sar_analyzers, target_ids):
        for ii in target_ids:
            total_line = int(getstatusoutput("wc -l %s" % sar_list[ii])[1].lstrip(" ").split(" ")[0])
            updated_lines = getstatusoutput("tail -n %d %s" %
                                            (total_line - sar_data_until_line[ii], sar_list[ii]))[1].split("\n")
            for line in updated_lines:
                sar_analyzers[ii].update(line.strip("\r"))

            sar_data_until_line[ii] = total_line


class WebServer(Backend):
    def _response_index(self, env, start_response):
        script_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(script_path, 'html/index.html'), 'r') as fid:
            index_contents = fid.read()
        length = str(len(index_contents))

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('HTTP-Version', 'HTTP/1.1'),
                                  ('Content-Type', 'text/html'),
                                  ('Content-Length', length)])
        return [index_contents]

    def _response_source_list(self, env, start_response):
        res_body = str(self.ws_structure).replace("'", '"').encode()

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Type', 'application/json'),
                                  ('Content-Length', str(len(res_body)))])
        return [res_body]

    def _response_source(self, env, start_response):
        path_info = env['PATH_INFO'].split("/")
        data_id = int(path_info[2])
        assert path_info[3] == "status"

        query_string = parse_qs(env['QUERY_STRING'])
        items = query_string["items"][0].split(",")
        from_index = int(query_string["from_index"][0])
        res_body = str(self.sar_data[data_id].extract_data_after_index(from_index, items)).replace("'", '"').encode()

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Length', str(len(res_body)))])
        return [res_body]

    def _response_favicon(self, env, start_response):
            start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                      ('Content-Length', '1')])
            return [b' ']


    def _response_js(self, env, start_response):
        script_path = os.path.dirname(os.path.realpath(__file__))
        js_path = os.path.join(script_path, "html", env['PATH_INFO'].lstrip('/'))
        with open(js_path, 'r') as fid:
            js_contents = fid.read()

        length = str(len(js_contents.encode()))

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Type', 'text/javascript'),
                                  ('Content-Length', length)])
        return [js_contents]

    def _response_css(self, env, start_response):
        script_path = os.path.dirname(os.path.realpath(__file__))
        css_path = os.path.join(script_path, "html", env['PATH_INFO'].lstrip('/'))
        with open(css_path, 'r') as fid:
            css_contents = fid.read()

        length = str(len(css_contents.encode()))

        start_response("200 OK", [('Access-Control-Allow-Origin', 'null'),
                                  ('Content-Type', 'text/css'),
                                  ('Content-Length', length)])
        return [css_contents]

    def __call__(self, env, start_response):
        if env['PATH_INFO'] == "/":
            return self._response_index(env, start_response)
        elif env['PATH_INFO'].startswith("/source/lists"):
            return self._response_source_list(env, start_response)
        elif env['PATH_INFO'].startswith("/source/"):
            return self._response_source(env, start_response)
        elif env['PATH_INFO'] == "/favicon.ico":
            return self._response_favicon(env, start_response)
        elif env['PATH_INFO'].endswith("js"):
            return self._response_js(env, start_response)
        elif env['PATH_INFO'].endswith("css"):
            return self._response_css(env, start_response)
        else:
            assert False


def main():
    application = WebServer()
    application.startup()

    application.sar_data_update_all(application.sar_list,
                                    application.sar_data_until_line,
                                    application.sar_analyzers)

    mame = RepeatedTimer(10,
                         application.sar_data_update_all,
                         application.sar_list,
                         application.sar_data_until_line,
                         application.sar_analyzers)
    try:
        mame.start()

        from wsgiref.simple_server import make_server

        port = 8888
        server = make_server('', port, application)
        print("Serving on port %d" % port)
        server.serve_forever()

    finally:
        mame.stop()

if __name__ == '__main__':
    main()
    # sar_data_update(sar_list, sar_data_until_line, sar_analyzers)
