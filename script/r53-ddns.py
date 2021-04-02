#!/usr/bin/env python

"""Update Route 53 resource record with current public IP address

The purpose of this application is to utilize an existing Route 53
hosted zone and record for dynamic DNS.

The logic in this script assumes that the supplied DNS name will
resolve to some value, if it doesn't exist, an exception will be
raised.  Be sure the A record exists before execution.
"""

import argparse
import boto3
import logging
import requests
import socket
from botocore.exceptions import ClientError
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# DNS ttl, hosted zone id, and resource record to upsert
# Hardcode if desired, arguments will override if supplied
ttl = 60
hosted_zone_id = ''
dns_name = ''

# ipify simple public address API endpoint
api_endpoint = 'https://api.ipify.org'

parser = argparse.ArgumentParser(description=('Update Route 53 record'
                                              ' with public IP address'))
parser.add_argument('-i', '--hosted-zone-id',
                    type=str,
                    help='hosted zone id')
parser.add_argument('-n', '--name',
                    type=str,
                    help='host/dns name to update')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='informational output')
parser.add_argument('-vv', '--debug',
                    action='store_true',
                    help='debug output')
args = parser.parse_args()

# Configure verbosity based on args
if args.verbose:
    logger.setLevel(logging.INFO)
if args.debug:
    logger.setLevel(logging.DEBUG)

# Set the hosted zone id based on run-time args, else prompt
if args.hosted_zone_id:
    hosted_zone_id = args.hosted_zone_id
while not hosted_zone_id:
    hosted_zone_id = input("Provide the hosted zone id for your record: ")
logging.info(f'Hosted Zone ID: {hosted_zone_id}')

# Set the record to update based on run-time args, else prompt
if args.name:
    dns_name = args.name
while not dns_name:
    dns_name = input("Provide the record (DNS) name to update: ")
logging.info(f'DNS name: {dns_name}')

# Get current public ipv4 address via API
logging.info(f'API endpoint: {api_endpoint}')
try:
    get_response = requests.get(api_endpoint)
except requests.exceptions.RequestException as e:
    logging.error(f'API get method failed\n{e}')
    raise
current_ip = get_response.text
logging.info(f'Current IP: {current_ip}')
logging.debug(f'Request Status: {get_response.status_code}')
logging.debug(f'Request Elapsed: {get_response.elapsed}')
logging.debug(f'Request Headers: {get_response.headers}')

# Resolve expected host name
try:
    resolved_ip = socket.gethostbyname(dns_name)
except socket.error as e:
    logging.error(f'Name resolution failed\n{e}')
    raise
logging.info(f'Resolved IP: {resolved_ip}')

# If current and resolved IPs don't match, update the R53 record
if current_ip != resolved_ip:
    logging.info(f'Current and resolved IP mismatch,'
                 f' updating {dns_name} record')
    now = datetime.now()
    try:
        r53 = boto3.client('route53')
        response = r53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': f'Updated {dns_name} programatically'
                           f' - {now.strftime("%Y-%m-%d %H:%M:%S")}',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': dns_name,
                            'Type': 'A',
                            'TTL': ttl,
                            'ResourceRecords': [
                                {
                                    'Value': current_ip
                                },
                            ]
                        }
                    },
                ]
            }
        )
    except ClientError as e:
        logging.error(f'Unable to update resource record set\n{e}')
        raise
    logging.warning(f'IP address changed from {resolved_ip} to {current_ip};'
                    f' {dns_name} record has been updated')
else:
    logging.info(f'No change, {dns_name} resolves to'
                 f' {resolved_ip} which matches current IP')
