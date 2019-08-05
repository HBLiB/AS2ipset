#!/usr/bin/env python3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import json
import time
import os
import sys
import syslog
import argparse

def requests_retry_session(
    retries=3,
    backoff_factor=5,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def latest(asNR):
    source_url = 'https://stat.ripe.net/data/bgp-state/data.json?'
    pull_data = source_url + 'resource={}&timestamp={}'.format(asNR,time.strftime("%Y-%m-%d"))
    try:
        return requests_retry_session().get(pull_data)
        pass
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, 'Failed 3 times connecting to stat.ripe.net in AS2ipset for {}'.format(asNR))
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description='Create ipset net:hash per AS')
    parser.add_argument('--AS', type=int,
                        help='AS number to fetch prefixes for')
    parser.add_argument('--deploy',
                        default=False,
                        action='store_true',
                        help='Use this to write changes to ipset')
    parser.add_argument('--print',
                        help='log errors in syslog, turned on by default with cron option used',
                        action='store_true',
                        default=True)
    args = parser.parse_args()

    if not args.AS:
        print ('Need at least AS number to run, try --help')
        sys.exit()
    ASnr = 'AS' + str(args.AS)
    response = latest(ASnr)
    prefixes = []
    if response.json()['status_code'] == 200 :
        source_id = response.json()['data']['bgp_state'][0]['source_id']
        for x in response.json()['data']['bgp_state']:
            if x['source_id'] == source_id:
                prefixes.append(x['target_prefix'])
    else:
        print('Status error ' + str(response.json()['status_code']))
        syslog.syslog(syslog.LOG_ERR, 'Failed to parse json for request {}, return code: '.format(ASnr) + str(response.json()['status_code']) )
        sys.exit()

    if args.deploy:
        os.system('ipset destroy {} 2>/dev/null'.format(ASnr))
        os.system('ipset -N {} nethash'.format(ASnr))
        for i in prefixes:
            os.system('ipset -A {} '.format(ASnr) + i)
    elif args.print:
        print(*prefixes, sep = "\n")

if __name__ == "__main__":
    main()
