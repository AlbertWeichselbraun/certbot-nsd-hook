#!/usr/bin/env python3

#
# nsd-udpate-dns.py certbot hook
#

import os.path
import subprocess

from os import getenv
from shutil import copyfile

import dns.zone
from dns.rdatatype import SOA, TXT

NSD_CONFIG = "/etc/nsd/nsd.conf"

certbot_domain = getenv('CERTBOT_DOMAIN')
certbot_validation = getenv('CERTBOT_VALIDATION')


def get_zonefile(domain):
    ''' Returns:
            the path of the zonefile for the given domain.
    '''
    toplevel = None
    zones = {}
    zone_name = None
    zone_file = None

    with open(NSD_CONFIG) as f:
        for line in f:
            if not line[0].isspace():
                toplevel = line.strip()
                if zone_name and zone_file:
                    zones[zone_name] = zone_file
                    zone_name = None
                    zone_file = None

            if toplevel != 'zone:':
                continue

            if 'name:' in line:
                zone_name = line.split('name:')[1].strip().replace('"','')
            elif 'zonefile:' in line:
                zone_file = line.split('zonefile:')[1].strip().replace('"','')

        if zone_name and zone_file:
            zones[zone_name] = zone_file

    if domain in zones:
        return os.path.join(os.path.dirname(NSD_CONFIG), zones[domain])
    raise ValueError("Cannot find zone '{}' in '{}'.".format(domain,
                                                             NSD_CONFIG))

def update_domain(domain, zonefile, secret):
    '''
    Updates the given domain with the new ACME secret.
    '''
    zone = dns.zone.from_file(zonefile, domain)

    # updata soa serial
    for soa in zone.iterate_rdatasets(rdtype='SOA'):
        soa_name, soa_rdataset = soa
    for rdata in soa_rdataset.processing_order():
        soa_rdataset.add(rdata.replace(serial=rdata.serial + 1))

    # update the acme challenge
    acme_rdataset = zone.find_rdataset('_acme-challenge', rdtype=TXT)
    for rdata in acme_rdataset.processing_order():
        new_acme_rdata = rdata.replace(strings=[secret.encode("utf8")])
    zone.delete_rdataset('_acme-challenge', rdtype=TXT)
    new_acme_rdataset = zone.find_rdataset('_acme-challenge', rdtype=TXT, create=True)
    new_acme_rdataset.add(new_acme_rdata, ttl=acme_rdataset.ttl)

    zone.to_file(zonefile)

#
# Main
#

zonefile = get_zonefile(certbot_domain)
copyfile(zonefile, zonefile + ".bak")
update_domain(certbot_domain, zonefile, certbot_validation)

subprocess.run(['systemctl', 'reload', 'nsd'])
