#!/usr/bin/python
###########################################################################
# Application:  check_dell_warranty.py
# Function:     nagios check checks finds Service Tag and checks warranty
#		status via Dell API
# Author(s):    Randy Rue, scharp.org
###########################################################################
#load the required modules
import os, sys, string, requests, time
from datetime import datetime


def main():
    """ main entry point; only called if __main__ """
    
    # Dell API key
    APIKEY = '77cd9909-3be7-459b-b086-224c1e25588c'
    
    # is this Dell hardware
    svctag = ''
    try:
	infile = os.popen('sudo dmidecode')
        lines = infile.read()
	if not "Chassis Information" in lines:
	    sys.exit(3)
	infile.close()
	# get Dell Service Tag
	for line in lines.split('\n'):
	    if "Serial Number" in line:
	        svctag = line.split()[-1].strip()
	        break
    except:
	sys.stdout.write("CRITICAL: Dell Warranty check failed, is Open Manage installed?")
	sys.exit(3)
    
    # testing hack
    # svctag = 'CL5BHQ2' # this is xensrv5-a
    # svctag = '5ZQ7WV1' # this is atlasxen1-a
    
    URL = "https://api.dell.com/support/assetinfo/v4/getassetwarranty/%s?apikey=%s" % (svctag, APIKEY)
    res = requests.get(URL)
 
    if res.status_code != 200:
        sys.stderr.write('[%s] Caught %i as the response code.\n' % (svctag, res.status_code))
        sys.stderr.write('[%s] Unable to get details for given service tag.\n'
                % svctag)
 
    latest_enddate = datetime.strptime(u'1970-01-01', '%Y-%m-%d')
    now = datetime.now()
    warrs = res.json()['AssetWarrantyResponse'][0]['AssetEntitlementData']
    for warr in warrs:
	enddate = datetime.strptime(warr['EndDate'].split('T')[0], '%Y-%m-%d')
	if enddate > latest_enddate: latest_enddate = enddate
    
    remaining = latest_enddate - now
    remaining = remaining.days
    
    if remaining > 90:
	sys.stdout.write("OK - Dell Warranty expires %s" % latest_enddate.strftime('%Y-%m-%d'))
	sys.exit(0)
    elif remaining > 30:
	sys.stdout.write("WARNING - Dell Warranty expires %s" % latest_enddate.strftime('%Y-%m-%d'))
	sys.exit(1)
    elif remaining > 0:
	sys.stdout.write("CRITICAL - Dell Warranty expires %s" % latest_enddate.strftime('%Y-%m-%d'))
	sys.exit(2)
    elif remaining <= 0:
	sys.stdout.write("CRITICAL - Dell Warranty expired %s" % latest_enddate.strftime('%Y-%m-%d'))
	sys.exit(2)
    else:
	sys.stdout.write("Dell Warranty check failed")
	sys.exit(3)

if __name__ == '__main__': main()
