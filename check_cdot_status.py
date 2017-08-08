#!/usr/bin/python
###########################################################################
# Application:  check_cdot_status.py
# Function:     nagios check checks NetApp cluster status via SSH
# Author(s):    Randy Rue, scharp.org
###########################################################################
#load the required modules
import os, sys, string


def main():
    """ main entry point; only called if __main__ """
    
    if len(sys.argv) < 3:
	sys.stdout.write("CRITICAL: Incorrect Arguments")
	sys.exit(2)

    # get CLI arguments crudely
    for i in range(len(sys.argv)):
	arg = sys.argv[i].lower()
	if arg == "-h": host = sys.argv[i+1]

    # system command to be run remotely
    cmd = 'system health status show'
    
    # Windows paths, files and executables
    global ssh, ssh_key
    ssh = 'plink.exe'
    ssh_key = 'h:\\.ssh\\nagios\\nagios.ppk'
    cmdfmt = 'echo yes | %s -i %s -l nagios %s %s'
    
    if os.name == "posix":
        # we're running *nux, change paths and variables for outside calls
        ssh = '/usr/bin/ssh'
        ssh_key = '/usr/local/apps/nagios/.ssh/id_rsa'
	cmdfmt = '%s -i %s -q -o StrictHostKeyChecking=no nagios@%s %s'
    
    
    cmd = cmdfmt % (ssh, ssh_key, host, cmd)
    
    results = os.popen(cmd).readlines()
    
    if string.join(results).strip() == "":
	sys.stdout.write("CRITICAL: No data returned from %s" % host)
	sys.exit(2)

    if results[2].strip() == "ok":
	sys.stdout.write("Global Status OK")
	sys.exit(0)
    else:
	sys.stdout.write("CRITICAL: Check Global Status")
	sys.exit(2)

if __name__ == '__main__': main()
