import sys
import os
import StringIO

BAR_BOTTOM = 0.1

class ActivityPlot(object):
	
  def __init__(self):
    self.__data = []
    self.__max_end = 0
    self.__xtics = []
		
  def addData(self, name, start, end, height, colour):
    self.__data.append((name, start, end, height, colour))
    self.__max_end = max(end, self.__max_end)

  def addXtic(self, str, x):
    self.__xtics.append(str)
    self.__xtics.append(x)

  def OutputGNUPlotScript(self, title, output_file, stream):
    '''Outputs the Gnuplot script that will create a plot of the given periods.
    The title an eps file name are specified. Output is written to the given
    stream.'''
    stream.write('''set title "%s"
    set ylabel "Mbps"
    set xtics rotate ('%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d, '%s' %d)
    set term postscript eps 10
    set output "%s"
    ''' % (title, self.__xtics[0], self.__xtics[1], self.__xtics[2], self.__xtics[3], self.__xtics[4], self.__xtics[5], self.__xtics[6], self.__xtics[7], self.__xtics[8], self.__xtics[9], self.__xtics[10], self.__xtics[11], self.__xtics[12], self.__xtics[13], self.__xtics[14], self.__xtics[15], self.__xtics[16], self.__xtics[17], self.__xtics[18], self.__xtics[19], self.__xtics[20], self.__xtics[21], self.__xtics[22], self.__xtics[23], output_file))

    count = 1
    for bar in self.__data:
      stream.write(
    'set object %s rect from %f, %f to %f, %f, 2 fc rgb "%s" fs solid\n' %
    (count, bar[1], BAR_BOTTOM,
    bar[2], BAR_BOTTOM + bar[3], bar[4]))
      count += 1

    stream.write('plot [0:%d] [0:%d] 0\n' %
    (self.__max_end, BAR_BOTTOM + bar[3]))
  
    
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
