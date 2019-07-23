#!/usr/bin/env python3

import requests
import json
import time
import os
import sys

asList = sys.argv[1]

get_AS = 'https://stat.ripe.net/data/bgp-state/data.json?resource={}&timestamp={}'.format(asList,time.strftime("%Y-%m-%d"))
response = requests.get(get_AS)
source_id = response.json()['data']['bgp_state'][0]['source_id']
os.system('ipset -N {} nethash'.format(asList))
for x in response.json()['data']['bgp_state']:
    if x['source_id'] == source_id:
        os.system('ipset -A {} '.format(asList) + x['target_prefix'])
