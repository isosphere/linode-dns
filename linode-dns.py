#!/usr/bin/python
"""
linode-dns.py
Author: Michael Shepanski
Date: Jan 17, 2010

Updated by: Matthew Scheffel
Date: May 20, 2017

A script to update a DNS record on Linode to your external IP.

References:
  http://atxconsulting.com/content/linode-api-bindings
  https://github.com/tjfontaine/linode-python/
"""
import re
from linode import Api
import requests

APIKEY = 'sekret'
DOMAIN = 'example.com'
RECORD = 'www'
CHECKIP = "http://checkip.dyndns.org:8245/"

def get_external_ip():
    """ Return the current external IP. """
    print "Fetching external IP from: %s" % CHECKIP
    request = requests.get(CHECKIP)
    external_ip = re.findall('[0-9.]+', request.text)[0]
    return external_ip

def set_dns_target(utarget, udomain=DOMAIN, urecord=RECORD):
    """ Update the domain's DNS record with the specified target. """
    api = Api(APIKEY)
    for domain in api.domain.list():
        if domain['DOMAIN'] == udomain:
            # Check the DNS Entry already exists
            for record in api.domain.resource.list(domainid=domain['DOMAINID']):
                if record['NAME'] == RECORD:
                    if record['TARGET'] == utarget:
                        # DNS Entry Already at the correct value
                        print "Entry '%s:%s' already set to '%s'." % (udomain, urecord, utarget)
                        return record['RESOURCEID']
                    else:
                        # DNS Entry found; Update it
                        print "Updating entry '%s:%s' target to '%s'." % (udomain, urecord, utarget)
                        return api.domain.resource.update(domainid=domain['DOMAINID'],
                            resourceid=record['RESOURCEID'], target=utarget)
            # DNS Entry not found; Create it
            print "Creating entry '%s:%s' target as '%s'." % (udomain, urecord, utarget)
            return api.domain.resource.create(domainid=domain['DOMAINID'],
                name=urecord, type='A', target=utarget, ttl_sec=3600)
            print "Error: Domain %s not found." % udomain

if __name__ == '__main__':
    set_dns_target(get_external_ip(), DOMAIN, RECORD)
    print "Done."
