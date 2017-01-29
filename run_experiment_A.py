#!/usr/local/bin/python

from a1gnuplot import ActivityPlot

import os
import re
import subprocess
import sys

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

# Run the program and create the plot.
output = cmd(['./a1sampler', '20'])

plot = ActivityPlot() 
plot.setXtics(1)
prev_end = 0;

# Open file to store raw data
file = open('Activity Periods Data.txt', 'w')

for line in output.splitlines():
  #printf("Active %d: start at %d, duration %d cycles (%f)", count/2,  num_cycles, num_cycles/clock_speed);
  match = re.match('(Active|Inactive)( \d*: start at )(\d*)(, duration )(\d*)( cycles \()(\d*.\d*)( ms\))', line)

  duration = float(match.groups()[6])
  colour = "blue"
  if (str(match.groups()[0]) == "Inactive"):
    colour = "black"

  #print("Adding start: ", prev_end, "stop: ", prev_end+duration, " Colour: ", colour)
  plot.addData(prev_end, prev_end+duration, colour)
  file.write("start: %f stop: %f state: %s\n" % (prev_end, prev_end+duration, str(match.groups()[0])))
  prev_end = prev_end+duration
  
file.close()
plot.CreatePlot('Activity Periods', 'periods.eps')
