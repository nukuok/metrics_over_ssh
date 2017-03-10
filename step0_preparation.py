#!/usr/bin/python

if __name__ == '__main__':
    import sys

    from defs import step0

    ws = step0.PrepareStep1Script()
    ret = ws.generate_workspace('./')
    assert ret == 0

    monitor_name = sys.argv[1]
    host_list = sys.argv[2].split(",")
    ret = ws.generate_subworkspace(monitor_name, host_list)
    assert ret == 0

    ret = ws.generate_step1_script()
    assert ret == 0
