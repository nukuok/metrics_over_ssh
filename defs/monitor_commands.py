commands = {
    "iostat": {
        "command": "LANG=en_US.UTF-8 iostat -xdkt ${interval} ${times}",
        "output": "iostat.txt"
    },
    "mpstat": {
        "command": "LANG=en_US.UTF-8 mpstat -P ALL ${interval} ${times}",
        "output": "mpstat.txt"
    },
    "sar": {
        "command": "LC_TIME=C LANG=en_US.UTF-8 sar -A ${interval} ${times}",
        "output": "sar.txt"
    },
    "top": {
        "command": "LANG=en_US.UTF-8 top -b -c -d ${interval} -n ${times}",
        "output": "top.txt"
    },
    "vmstat": {
        "command": "LANG=en_US.UTF-8 vmstat -t ${interval} ${times}",
        "output": "vmstat.txt"
    }
}
