from commands import getstatusoutput


def check_hosts(host_list):
    ping_command = "ping -c 1 -t 2 %s"
    results = [getstatusoutput(ping_command % host) for host in host_list]
    status = [output[0] for output in results]
    return status


def 
