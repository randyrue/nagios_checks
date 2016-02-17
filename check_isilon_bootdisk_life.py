#!/usr/bin/python
###########################################################################
# Application:  check_isilon_bootdisk_life.py
# Function:     nagios check gets remaining lifecycle percentage
# 		for Isilon SSD boot disks
# Notes:	SanDisk SSD does not provide % remaining life metric,
#		instead we track hours powered on and assume a 3 year
#		life span
# Author(s):    Randy Rue, fredhutch.org
# Mod Date:     2016-02-16
###########################################################################
#load the required modules
import os, sys, string


def main():
    """ main entry point; only called if __main__ """
    
    if len(sys.argv) < 7:
	sys.stdout.write("CRITICAL: Incorrect Arguments")
	sys.exit(2)

    # get CLI arguments crudely
    for i in range(len(sys.argv)):
	arg = sys.argv[i].lower()
	if arg == "-h": host = sys.argv[i+1]
	if arg == "-w": wrn = int(sys.argv[i+1])
	if arg == "-c": crit = int(sys.argv[i+1])

    # Windows paths, files and executables
    global ssh, ssh_key
    ssh = 'plink.exe'
    ssh_key = "c:\\ssh\\id_rsa.ppk"
    if os.name == "posix":
        # we're running *nux, change paths and variables for outside calls
        ssh = '/usr/bin/ssh'
        ssh_key = '/home/nagios/.ssh/id_rsa'
    
    cmd = "isi_radish -a \"'Internal J3' 'Internal J4' 'Carrier board J3' 'Carrier board J4'\""
    cmdfmt = '%s -i %s root@%s %s'
    cmd = cmdfmt % (ssh, ssh_key, host, cmd)
    
    results = os.popen(cmd).readlines()
    
    if not string.join(results).strip():
	sys.stdout.write("CRITICAL: No data returned from %s %d %d" % (host, wrn, crit))
	sys.exit(2)
    
    disks = {}
    for line in results:
	if line.startswith("Internal"):
	    # disk header line
	    # get the disk info
	    f = line.split()
	    device = f[1]
	    if "SMART iSATA" in line:
		model = "SMART iSATA"
		life_flag = "Percent Life Remaining:"
		hours_flag = "Power-On Hours:"
	    if "SanDisk SSD" in line:
		model = "SanDisk SSD"
		life_flag = "Power-On Hours"
		hours_flag = "Power-On Hours:"
	    if "NETLIST SSD" in line:
		model = "NETLIST SSD"
		life_flag = "Percent Lifetime Left"
		hours_flag = "Power-On Hours:"
	if hours_flag in line:
	    hours = float(int(line.split()[6][:-1], 16))
	if life_flag in line:
	    if model == "SMART iSATA":
		pct_life_remaining = float(int(line.split()[7][:-1], 16))
	    elif model == "SanDisk SSD":
		# SanDisk SSD has no pct_rem metric, estimating based on hours run and three year life span
		pct_life_remaining = 100 - 100*hours/26280
	    elif model == "NETLIST SSD":
		pct_life_remaining = float(int(line.split()[7][:-1], 16))
#		if pct_life_remaining < 0: pct_life_remaining = 0
	if line.startswith("SMART status is"):
	    remaining_days = int(((pct_life_remaining/100) * hours)/(1-(pct_life_remaining/100)))/24
	    disks[device] = remaining_days
    
    keys = disks.keys()
    keys.sort()
    status = "OK"
    ostring = ""
    for key in keys:
	if ostring == "": ostring = "%s:%d days remaining" % (key, disks[key])
	else: ostring = ostring + ", %s:%d days remaining" % (key, disks[key])
	if disks[key] < crit:
	    status = "critical"
	if disks[key] < wrn:
	    if status != "critical": status = "warning"
    
    if status == "OK":
	ostring = "OK: %s" % ostring
	sys.stdout.write(ostring)
	sys.exit(0)
    elif status == "warning":
	ostring = "WARNING: %s" % ostring
	sys.stdout.write(ostring)
	sys.exit(1)
    else:
	ostring = "CRITICAL: %s" % ostring
	sys.stdout.write(ostring)
	sys.exit(2)

	    
	
	


if __name__ == '__main__': main()
