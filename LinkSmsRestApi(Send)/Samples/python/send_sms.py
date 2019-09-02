#!env python3

import json
import os
from argparse import ArgumentParser
from collections import namedtuple
from pathlib import Path

from requests import post
from requests.auth import HTTPBasicAuth

basedir = Path(os.path.dirname(os.path.realpath(__file__)))


class SmsSender(object):

    def __init__(self, dry_run, config, msisdns):
        self.dry_run = dry_run
        self.server_url = config['server_url']
        self.platformId = config['platformId']
        self.platformPartnerId = config['platformPartnerId']
        self.auth = HTTPBasicAuth(config['username'], config['password'])
        self.msisdns = msisdns

    def do_request(self, path, data):
        if not self.dry_run:
            response = post(self.server_url + path, json=data, auth=self.auth)
            print(response.json())
        else:
            print('### Dry run (override to do real request using -n)')
            print(f'Request would be: POST {self.server_url + path}\nBody: {data}')

    def send_single_sms(self):
        self.do_request('/send', {
            "source": "LINK",
            "destination": self.msisdns[0],
            "userData": "Hello, this is a single test message.",
            "platformId": self.platformId,
            "platformPartnerId": self.platformPartnerId,
            "useDeliveryReport": False})

    def send_bulk_sms(self):
        pass

    def send_payment_sms(self):
        pass

    def execute(self, command):
        commands = {
        'send': self.send_single_sms,
        'send_bulk': self.send_bulk_sms,
        'send_payment': self.send_payment_sms
        }
        commands[command]()


def main():
    parser = ArgumentParser()

    parser.add_argument('command',
                        choices=['send', 'send_bulk', 'send_payment'],
                        metavar='COMMAND',
                        help='Available commands: %(choices)s')
    parser.add_argument('msisdns',
                        nargs='+',
                        metavar='MSISDNS',
                        help='One or more MSISDNs to test sending with')
    parser.add_argument('-n', '--no-dry-run', action='store_false', dest='dry_run')

    args = parser.parse_args()


    try:
        with open(basedir / 'server_settings.json') as server_settings:
            config = json.load(server_settings)
    except FileNotFoundError:
        print('File server_settings.txt not found!')

    sms_sender = SmsSender(args.dry_run, config, args.msisdns)
    sms_sender.execute(args.command)


if __name__ == '__main__':
    main()
