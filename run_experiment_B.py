#!/usr/local/bin/python

from a1bGnuplot import ActivityPlot

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

def get_data(input, lines_to_skip, max_lines):
  ''' Given a numactl stream input, strip the uncessary strings and return an array containing the data'''
  i = 0
  data = []
  for line in input.splitlines():
    file.write(line + '\n')
    if (i < lines_to_skip or i >= max_lines):
      i += 1
      continue
    i += 1
    
    
    #Best rate, Avg Time, Min time, Max time
    match = re.match('(\s*\w*\d*:\s*)(\d*.?\d*)(\s*)(\d*.?\d*)(\s*)(\d*.?\d*)(\s*)(\d*.?\d*)(\s*)', line)

    data.append([float(match.groups()[1]), float(match.groups()[3]), float(match.groups()[5]), float(match.groups()[7])])
  file.write('----------------------')
  return data
  
def make_rate_graph(toplevel, hw, node_nums):
  bar_width = 10 
  operations = ['Copy', 'Scale', 'Add', 'Triad']
  types = ['Same core', 'Same Node', 'Different Node', 'Expected']
  colours = ['blue', 'cyan', '#00008B', 'red']
  i = 0
  start = 0
  base = 0
  rate_plot = ActivityPlot()
  while (i < 4): 
    j = 0
    while (j < 3): #Set to 4 later if we're adding the hw defaults
      #name, start, end, height, colour
      ratio = hw[0][0]/hw[0][node_nums[j]]
      expected = toplevel[j][i][0]*ratio
      rate_plot.addData('%s - %s' % (types[j], operations[i]), start, start+bar_width, toplevel[j][i][0], colours[j])
      rate_plot.addXtic(types[j] + ' - ' + operations[i], start+bar_width/2)
      j += 1
      start += bar_width
    start += bar_width #Add white space
    i += 1
  
  rate_plot.CreatePlot('Rate Graph', 'rate.eps')
 
# File to store raw data
file = open('Numactl Data.txt', 'w')


 
# Build the program.
output1 = cmd(['/u/csc469h/fall/pub/assgn1/bin/numactl', '/u/csc469h/fall/pub/assgn1/bin/mccalpin-stream', '--membind 15', '--physcpubind 15'])
data1 = get_data(output1, 23, 27)

#TODO: Decide if I want to take the min of some data samples
#If so for each data point, just add another match and take the min of the floats
#We want min because the average may be skewed by heavy load 

output2 = cmd(['/u/csc469h/fall/pub/assgn1/bin/numactl', '/u/csc469h/fall/pub/assgn1/bin/mccalpin-stream', '--membind 17', '--physcpubind 19'])
data2 = get_data(output2, 23, 27)

output3 = cmd(['/u/csc469h/fall/pub/assgn1/bin/numactl', '/u/csc469h/fall/pub/assgn1/bin/mccalpin-stream', '--membind 18', '--physcpubind 41'])
data3 = get_data(output3, 23, 27)

hw_output = cmd(['/u/csc469h/fall/pub/assgn1/bin/numactl', '-H'])
hw_data = get_data(hw_output, 15, 30)


file.close()

toplevel = [data1, data2, data3]
node_nums = [0, 0, 2]

make_rate_graph(toplevel, hw_data, node_nums)

print("Done, see rate.eps")



