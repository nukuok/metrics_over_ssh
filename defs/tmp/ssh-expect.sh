#!/usr/bin/expect -f

set host [lindex $argv 0]
# set password [exec cat pwd]
# set password $env(password)
set password [lindex $argv 1]

spawn ssh $host vmstat -t 1 10

expect {
"(yes/no)?"     {
        send -- "yes\r"
        exp_continue
        }
"*assword:*" {
        send -- "$password\r"
        }
}

expect eof
exit
