import sys
import os
import StringIO

BAR_BOTTOM = 0.1
BAR_HEIGHT = 3
xtics = 0
class ActivityPlot(object):
	
  def __init__(self):
    self.__data = []
    self.__max_end = 0
		
  def addData(self, start, end, colour):
    self.__data.append((start, end, colour))
    self.__max_end = max(end, self.__max_end)

  def setXtics(self, x):
    self.xtics = x
    
  def OutputGNUPlotScript(self, title, output_file, stream):
    '''Outputs the Gnuplot script that will create a plot of the given periods.
    The title an eps file name are specified. Output is written to the given
    stream.'''
    if (xtics == 0):
      stream.write('''set title "%s"
      set xlabel "Time (ms)"
      set noytics
      set term postscript eps 10
      set output "%s"
      ''' % (title, output_file))
    else:
      stream.write('''set title "%s"
        set xlabel "Time (ms)"
        set noytics
        set xtics %d
        set term postscript eps 10
        set output "%s"
        ''' % (title, self.xtics, output_file))

    #
    count = 1
    for period in self.__data:
      stream.write(
    'set object %d rect from %f, %f to %f, %f, 2 fc rgb "%s" fs solid\n' %
    (count, period[0], BAR_BOTTOM,
    period[1], BAR_BOTTOM + BAR_HEIGHT, period[2]))
      count += 1

    stream.write('plot [0:%d] [0:%d] 0\n' %
    (self.__max_end, BAR_BOTTOM + BAR_HEIGHT))
  
  def CreatePlot(self, title, output_file):
    '''Runs Gnuplot to create a period plot. The output is an eps file with the
       given name.'''
    command = StringIO.StringIO()
    command.write('gnuplot << ---EOF---\n')
    self.OutputGNUPlotScript(title, output_file, command)
    command.write('---EOF---\n')
    ret = os.system(command.getvalue())
    if ret != 0:
      raise Exception(
        'Error running the plotting script:\n%s' % (command.getvalue()))
