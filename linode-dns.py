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
import json
import re
import requests

APIKEY = 'sekret'
DOMAIN = 'example.com'
RECORD = 'www'
CHECKIP = "http://checkip.dyndns.org:8245/"

def get_external_ip():
    """ Return the current external IP. """
    request = requests.get(CHECKIP)
    external_ip = re.findall('[0-9.]+', request.text)[0]
    #print("Fetching external IP from: %s. Result = %s" % (CHECKIP, external_ip))
    return external_ip


if __name__ == '__main__':
    external_ip = get_external_ip()
    headers = {'Authorization': f'Bearer {APIKEY}'}

    response = requests.get(
        url=f'https://api.linode.com/v4/domains',
        headers=headers
    )

    domainId = None
    for domain in response.json()['data']:
        if domain['domain'] == DOMAIN:
            domainId = domain['id']
            break

    assert domainId is not None

    response = requests.get(
        url=f'https://api.linode.com/v4/domains/{domainId}/records',
        headers = headers
    )

    recordId = None
    must_change = False

    for record in response.json()['data']:
        if record['name'] == RECORD:
            if record['target'] != external_ip:
                must_change = True

            recordId = record['id']
            break

    assert recordId is not None

    if must_change:
        response = requests.put(
            url=f'https://api.linode.com/v4/domains/{domainId}/records/{recordId}',
            headers=dict({'Content-Type': 'application/json'}, **headers),
            data=json.dumps({
                'target': external_ip,
                'ttl_sec': 300,
            })
        )

        assert response.status_code == 200
