#!/usr/bin/env python

import socket
import urllib2
import os
import re
import sys
import ConfigParser
import argparse
import pyrax
import pyrax.exceptions as exc

# Variables used for obtaining IP Information
remoteHost = '8.8.8.8'
remotePort = 53
publicRslv = 'http://icanhazip.com/'
publicRslvPort = 80

# Parse ~/.raxdyndns config file
confFile = os.path.expanduser('~') + '/.raxdyndns'
raxConfig = ConfigParser.RawConfigParser()
raxConfig.read(confFile)
try:
    dynHostname = raxConfig.get("raxdyndns", "dyn_hostname")
    zone = raxConfig.get("raxdyndns", "zone")
    raxUser = raxConfig.get("rackspace_cloud", "username")
    raxApiKey = raxConfig.get("rackspace_cloud", "api_key")
except ConfigParser.NoOptionError as e:
    print "Required Option Missing: %s" % e
    sys.exit(1)

# Authenticate with the RAX API
try:
    pyrax.set_credentials(raxUser, raxApiKey)
except exc.AuthenticationFailed as e:
    print "RAX API Auth Error: %s" % e
    sys.exit(2)
except:
    print "Unknown RAX API Auth Error: %s" % exc
    sys.exit(2)


# Argument Parsing
epilog = """
Config File is required at ~/.raxdyndns with the following:

[raxdyndns]
dyn_hostname: {hostname, i.e. 'macbook'}
zone: {domain name, i.e. 'techguy.com'}

[rackspace_cloud]
username: {RAX Cloud username}
api_key: {RAX API Key}

"""
dynParse = argparse.ArgumentParser(description="Obtain your workstation IP Address, and update it's DNS entry in the \nRackspace Cloud DNS",
                                   formatter_class=argparse.RawTextHelpFormatter,
                                   epilog=epilog, add_help=True)
dynParse.add_argument('-q', dest='quiet', action='store_true',
                      help="Silence output")
dynParse.add_argument('-V', '--version', action='version',
                      version='%(prog)s 0.1 by Javier Ayala')
dynArgs = dynParse.parse_args()


# Function to verify FQDN
def isFQDN(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1:] == ".":
        hostname = hostname[:-1]  # strip 1 dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


# Function to obtain the default local IP
def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((remoteHost, remotePort))
    localIP = s.getsockname()[0]
    s.close()
    return localIP


# Function to get the public IP via icanhazip.com
def getPublicIP():
    publicIP = urllib2.urlopen(publicRslv).read().rstrip()
    return publicIP


def updateDynDns(dynHostname, myPublicIP):
    currIP = socket.gethostbyname(dynHostname)
    if (currIP == myPublicIP):
        print "%s is already set to %s in the DNS"
        wasChanged = 'no'
    else:
        print "Need to update the DNS"
        wasChanged = 'yes'
    return wasChanged, currIP


class raxDNS(object):
    """Connect to RAX Cloud DNS and stuff"""
    def __init__(self, pyrax):
        super(raxDNS, self).__init__()
        self.dns = pyrax.cloud_dns
        self.aRec = {'type': 'A', 'name': dynFQDN, 'data': myPublicIP,
                     'ttl': 300}

    def list(self):
        """
        List the domains
        """
        return self.dns.list()

    def findDom(self, domain):
        """
        Find the domain via the zone
        """
        self.domain = self.dns.find(name=domain)

    def findRec(self, dynFQDN):
        """
        Look for the current A record for the FQDN specified.  If not found,
        create it.
        """
        try:
            search = self.domain.find_record('A', name=dynFQDN)
            rec = self.domain.get_record(search.id)
        except exc.DomainRecordNotFound:
            add = self.domain.add_record(self.aRec)
            rec = self.domain.get_record(add[0])
        return rec

    def updateRec(self, dynFQDN):
        """
        Update the record for the existing FQDN with the new ip address.
        """
        search = self.domain.find_record('A', name=dynFQDN)
        return self.domain.update_record(search, data=myPublicIP)


# Gather all of the necessary info
myLocalIP = getLocalIP()
myPublicIP = getPublicIP()
dynFQDN = dynHostname + '.' + zone
if (isFQDN(dynFQDN) is not True):
    print "Error: %s is not a FQDN!" % dynFQDN
    sys.exit(3)

# Try and connect to the RAX Cloud DNS API
dnsConn = raxDNS(pyrax)
# Find the domain
try:
    dnsConn.findDom(zone)
except Exception as e:
    print "Error: %s" % e
    sys.exit(4)
# Find the current A record (or create it if non-existent)
currA = dnsConn.findRec(dynFQDN)
# Check the current A record against the current public, and update if needed.
if (currA["data"] == myPublicIP):
    if (dynArgs.quiet is not True):
        print "Already matches: %s" % currA["data"]
else:
    outcome = dnsConn.updateRec(dynFQDN)
    if (dynArgs.quiet is not True):
        print outcome["status"]
