#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO Paginator pagesize , Issue: botocore #1063

import argparse
import boto3
import logging
import sys
import datetime

def __getComment(args):
    if args.func.__name__ == 'ttl':
        return "Update %s to %s for domain %s @%s" % (
            args.func.__name__, args.ttl, args.domain, datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        )
    if args.func.__name__ == 'replaceIp':
        return "Update %s from %s to %s for domain %s @%s" % (
            args.func.__name__, args.oldIP, args.newIP, args.domain, datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        )

def ttl(record, args):
    if(record['TTL'] != args.ttl):
        logging.info("Changing ttl from %s to %s for %s %s" % (record['TTL'], args.ttl, record['Name'], record['Type']))
        record['TTL'] = args.ttl
        return True
    return False

def replaceIp(record, args):
    changes = False

    if 'ResourceRecords' in record:
        for value in record['ResourceRecords']:
            if args.oldIP in value['Value']:
                logging.info("Changing ip from %s to %s for %s %s" % (args.oldIP, args.newIP, record['Name'], record['Type']))
                value['Value'] = value['Value'].replace(args.oldIP, args.newIP)
                changes = True
    return changes

def changeRecords(client, domainZone, args):
    paginator = client.get_paginator('list_resource_record_sets') #client.list_resource_record_sets(
    page_iterator = paginator.paginate(
            HostedZoneId=domainZone['Id'],
            MaxItems=MAX_FETCH_ITEMS
    )

    changeRecordSet=list()

    for page in page_iterator:
        logging.debug("Page: %s" % page)
        for record in page['ResourceRecordSets']:
            if (record['Type'] == 'SOA' and not args.SOA): continue
            if record['Type'] == 'NS' and not args.NS: continue

            changed = args.func(record,args)
            if(changed):
                changeRecordSet.append({
                    'Action': 'UPSERT',
                    'ResourceRecordSet': record
                })

    logging.info("Changes: %s", changeRecordSet )
    if changeRecordSet and not args.dryrun:
        response = client.change_resource_record_sets(
            HostedZoneId=domainZone['Id'],
            ChangeBatch={
                'Comment': __getComment(args),
                'Changes': changeRecordSet
            }
        )
        logging.debug("Response: %s" % response)

        if(args.waitForSync and response['ChangeInfo']['Status']!='INSYNC'):
            waiter = client.get_waiter('resource_record_sets_changed')
            waiter.wait(Id=response['ChangeInfo']['Id'])
            logging.info("Changes are INSYNC")

# Main command
parser = argparse.ArgumentParser(description='Change Route53 domain records')
parser.add_argument('--dryrun', help="don't submit record change", action="store_true")
parser.add_argument('--waitForSync', help='wait for changes to propagate', action="store_true")
parser.add_argument('--maximumFetchItems', help='maximum items to fetch (default: 100)', dest="maxFetchItems", type=int, default=100, metavar='N')
parser.add_argument('--SOA', action="store_true", help='change SOA record')
parser.add_argument('--NS', action="store_true", help='change NS record')
parser.add_argument('-v', '--verbose', help='verbose', action="store_const", dest="loglevel", const=logging.INFO)
parser.add_argument('-d', '--debug', help='debug', action="store_const", dest="loglevel", const=logging.DEBUG)
subparser = parser.add_subparsers(description="available commands", help="additional help", dest="command")
subparser.required=True

# TTL command
ttl_parser = subparser.add_parser('ttl', help='change domain records TTL')
ttl_parser.add_argument('--domain', type=str, help='domain to change', required=True)
ttl_parser.add_argument('--ttl', default=14400, type=int, help='ttl to set (default: 14440)')
ttl_parser.set_defaults(func=ttl)

# Replace IP command
replaceIp_parser = subparser.add_parser('replaceIp', help='change server ip for all records')
replaceIp_parser.add_argument('--domain', type=str, help='domain to change', required=True)
replaceIp_parser.add_argument('--oldIP', type=str, help='old ip address', required=True)
replaceIp_parser.add_argument('--newIP', type=str, help='new ip address', required=True)
replaceIp_parser.set_defaults(func=replaceIp)

args = parser.parse_args()

# Constants
MAX_FETCH_ITEMS = str(args.maxFetchItems)

if args.loglevel is not None:
    logging.basicConfig(level=args.loglevel)

client = boto3.client('route53')

response = client.list_hosted_zones_by_name(
    DNSName=args.domain,
    MaxItems="1"
)

domainZone = response['HostedZones'][0]

if domainZone['Name'] != args.domain+".":
    logging.error('Domain %s not found' % args.domain)
    sys.exit(-1)

logging.debug("DomainZone: %s" % domainZone)

changeRecords(client, domainZone, args)
