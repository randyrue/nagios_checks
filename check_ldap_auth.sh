#!/bin/bash
# check for working ldap authentication
# pass the username of an account to test

# clear any cached authentication for the username
# also test if the cache command is installed
# and if the user exists (will squawk if you 
# try to clear a non-existent user

sss_cache -u $1 &>/dev/null
exit_status=$?
if [ $exit_status -eq 127 ]; then
    echo "Command not found: sss_cache"
    exit 3 #Nagios "UNKNOWN" status return
fi

if [ $exit_status -ne 0 ]; then
    echo "CRITICAL: sssd can't find LDAP user $1"
    exit 2 #Nagios "CRITICAL" status return
fi

echo "OK: sssd found LDAP user $1"
exit 0
