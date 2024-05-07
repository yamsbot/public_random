#!/bin/bash

for i in $(seq 0 10000); do ./two $i 2>/dev/null | grep "Congrats\! Youve found the flag" && echo $i ; done
