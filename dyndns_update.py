#!/usr/bin/env python3

import requests
import yaml
import logging


logging.basicConfig(filename='dyndns.log', format="%(asctime)s %(message)s", datefmt="%B %d %H:%M:%S",
                    level=logging.INFO)


def main():
    with open('dyndns_update.yaml', 'r') as file:
        config_kv = yaml.safe_load(file)
    url = config_kv.get('url')
    parameters = config_kv.get('parameters')

    ipv4_address = get_ipv4_address()
    logging.info("Public IPv4: " + ipv4_address)

    parameters['ipv4'] = ipv4_address
    patch_records(url, parameters)


def get_ipv4_address():
    return requests.request("GET", "https://api4.ipify.org").text


def patch_records(url, parameters):
    response = requests.request("GET", url, params=parameters)
    logging.info("Response code: " + f'{response.status_code}')


main()