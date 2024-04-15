#!/bin/python

import json
import argparse
import re
from collections import deque
import subprocess
import shlex


#This program requires one argument: the file to be processed
parser = argparse.ArgumentParser(description='Generates tasks from projects')
parser.add_argument('file', metavar='file', type=str, nargs=1, help='File to be processed')
args = parser.parse_args()
file = args.file[0]

#Dictionary with the properties of the tasks
indicators = {
        'Name:': ['', 'proj:'],
        'Priority:': ['', 'priority:'],
        'Due': ['', 'due:'],
        }

#Begining of the command
base_command = 'task add '

#Stack for remembering task dependencies, it's elements are of the form:
# ( task description, dependency level, task id )
stack = deque()

f = open(file, 'r')
for line in f.readlines():
    line = line.strip('\n')
    ind = False

    #Verification for special properties, defined in the dictionary indicators
    for k in indicators:
        if k == line[:len(k)]:
            ind = True
            indicators[k][0] = line[len(k):]
            if indicators[k][0][0] == ' ':
                indicators[k][0] = indicators[k][0][1:]
            print(indicators[k][0])
   
    if not ind:
        line = re.sub(r"\s", ' ', line)
        if line == '':
            continue
        command = base_command
        n = 0
        #Counting the dependency level as a function of identation
        for c in line:
            if c == ' ':
                n += 1
            else:
                break
        #Adds additional properties to the command
        for k in indicators:
            if indicators[k][0] != '':
                command += ' ' + indicators[k][1] + indicators[k][0]
        #Checks if the current task depends on another task
        while stack:
            s = stack.pop()
            if s[1] < n:
                command += ' depends:' + str(s[2])
                stack.append(s)
                break
        #Runs the command and reads the output to get the task id
        command += ' '+line
        r = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
        r = r.decode()
        r = r.removeprefix("Created task ")[:-2]
        stack.append((line, n, int(r)))
