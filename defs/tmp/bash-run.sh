#!/bin/bash

echo "Password!"
read -s password

./expect-ssh.sh 192.168.20.144 ${password}
