#!/usr/bin/expect -f

set timeout -1

set host [lindex $argv 0]
set password [lindex $argv 1]
set command [lindex $argv 2]

spawn ssh $host $command

expect {
    "*(yes/no)?" {
	send -- "yes\r"
	exp_continue
    }
    "*assword:*" {
        send -- "$password\r"
    }
}

expect eof
exit

