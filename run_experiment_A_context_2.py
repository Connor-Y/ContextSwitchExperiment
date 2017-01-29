#!/usr/local/bin/python

from a1gnuplot import ActivityPlot

import os
import re
import subprocess
import sys
from multiprocessing import Process, Queue

def cmd(command):
  '''Runs the given shell command and returns its standard output as a string.
     Throws an exception if the command returns anything other than 0.'''
  p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  ret = os.waitpid(p.pid, 0)[1]
  if ret != 0:
    raise Exception('Command [%s] failed with status %d\n:%s' % (command, ret, p.stderr.read()))
  return p.stdout.read()

# Build the program.
cmd('make')


def multirun(output):
  temp = cmd(['./a1sampler', '50', '1'])
  output.put(temp)
  
plot = ActivityPlot()


output = Queue()
p1 = Process(target=multirun, args=(output,))
p2 = Process(target=multirun, args=(output,))
p1.start()
p2.start()
p1.join()
p2.join()

output1 = output.get()
output2 = output.get()

split1 = output1.splitlines()
split2 = output2.splitlines()

# Open file to store raw data
file = open('Context Data 2.txt', 'w')


# Start at 2 to drop the first active and inactive cycle
i1 = 2
i2 = 2
start = 0
duration = 0
prev_end = 0
reducer = 0

while (i1 < len(split1) and i2 < len(split2)):
  match1 = re.match('(Active|Inactive)( \d*: start at )(\d*)(, duration )(\d*)( cycles \()(\d*.\d*)( ms\))', split1[i1])
  match2 = re.match('(Active|Inactive)( \d*: start at )(\d*)(, duration )(\d*)( cycles \()(\d*.\d*)( ms\))', split2[i2])
  colour = "black"
  #If we are null => inactive => skip
  #Otherwise, choose the one that starts first and print it too the graph
  #Then cycle to the next one 
  #Repeat until we have gone through all values
  #The empty ones are inactive time 
  #The gaps between small active times are context switches

  
  
  if (match1.groups()[0] == 'Inactive'):
    i1 += 1
    continue
  if (match2.groups()[0] == 'Inactive'):
    i2 += 1
    continue
  
  #print("S1 %d, S2: %d" % (int(match1.groups()[2]), int(match2.groups()[2])))
  if (int(match1.groups()[2]) <= int(match2.groups()[2])):
    start = prev_end
    duration = float(match1.groups()[6])
    colour = "red"
    i1 += 2
  else:
    start = prev_end
    duration = float(match2.groups()[6])
    colour = "blue"
    i2 += 2
  
  
  if reducer == 0:
    reducer = start
  
  if colour == "red":
    process = "Process 1 Running"
  else:
    process = "Process 2 Running"
    
  file.write("start: %f stop: %f state: %s\n" % (prev_end, prev_end+duration, process))
  plot.addData(start, start+duration, colour) 
  prev_end = start+duration

  
file.close()
plot.CreatePlot('Context Switching', 'context_2.eps')


