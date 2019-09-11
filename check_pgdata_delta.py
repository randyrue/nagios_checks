#!/usr/bin/python
###########################################################################
# Application:  check_pgdata_delta.py
# Function:     nagios check checks space usage on local dirs and
#		notifies on rate of change in GB/hour
# Author(s):    Randy Rue, scharp.org
###########################################################################
#load the required modules
import os, sys, string, time
from datetime import datetime


def main():
    """ main entry point; only called if __main__ """
    
    # defaults
    data_dir = "/pgdata_local"
    warning = 25 # GB per hour
    critical = 50 # GB per hour
    min_data = 15 # minimum time to collect before reporting, avoids false criticals on startup
    
    # crude args parsing
    for i in range(1,len(sys.argv)):
	if sys.argv[i].lower() == '-d':
	    data_dir = sys.argv[i+1]
	if sys.argv[i].lower() == '-w':
	    warning = int(sys.argv[i+1])
	if sys.argv[i].lower() == '-c':
	    critical = int(sys.argv[i+1])
    
    data_file = "/tmp/check_pgdata/%s.txt" % string.replace(data_dir,"/","_")

    # check for the data file dir and data dir and create if needed
    if not os.path.isdir("/tmp/check_pgdata"):
	
	os.mkdir('/tmp/check_pgdata/')
    if not os.path.isfile(data_file):
	open(data_file,'a').close()
    
    
    # what time is it right now
    right_now = int(time.time())
    
    # how's our directory looking right now
    # THE NRPE USER MUST HAVE PERMISSIONS IN THE DATA_DIR
    # OR NRPE MUST HAVE SUDO RIGHTS TO THE DU COMMAND
    try:
	dir_size = int(os.popen("sudo du -s %s" % data_dir).read().split()[0])
    except:
	sys.stdout.write("FAIL: Unable to parse %s (check permissions?)" % data_dir)
	sys.exit(3)
    
    # load the existing data
    # only retain the last 60 minutes
    infile = open(data_file)
    inlines = infile.readlines()
    infile.close()
    history = []
    outlines = []
    for line in inlines:
	if line.startswith("#"): outlines.append(line)
	f = line.strip().split(",")
	if right_now - int(f[0]) < 3600:
	    outlines.append([f[0],f[1]])
	    history.append([f[0],f[1]])
    outlines.append([str(right_now),str(dir_size)])
    # replace the data file
    outfile = open(data_file, 'w')
    for ol in outlines:
	outfile.write("%d,%d\n" % (int(ol[0]), int(ol[1])))
    outfile.close()
    
    # find the change
    # elapsed time in seconds
    elapsed_time = int(outlines[len(outlines)-1][0]) - int(outlines[0][0])
    if float(elapsed_time) / 60 < min_data:
	sys.stdout.write("WAITING: Not enough data yet (only %0.0f out of %d minutes)" % (float(elapsed_time)/60, min_data) )
	sys.exit(1)
    # space change in KB
    delta_disk = int(outlines[len(outlines)-1][1]) - int(outlines[0][1])
    
    delta = float(delta_disk)/float(elapsed_time) # in KB/second
    delta = delta * 3600 / 1048576 # in GB/hour
    
    if delta < warning:
	sys.stdout.write("OK: %s, change rate=%0.2f GB/hr" % (data_dir,delta))
	sys.exit(0)
    elif delta < critical:
	sys.stdout.write("WARNING: %s, change rate=%0.2f GB/hr" % (data_dir,delta))
	sys.exit(1)
    else:
	sys.stdout.write("CRITICAL:%s, change rate=%0.2f GB/hr" % (data_dir,delta))
	sys.exit(2)
    
    
    
    

if __name__ == '__main__': main()
