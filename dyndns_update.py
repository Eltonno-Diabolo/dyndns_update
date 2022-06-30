#!/usr/bin/env python3

import requests
import yaml
import logging
import argparse
import sys

config_file_name = 'dyndns_update.yaml'
log_file_name = 'dyndns.log'

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="URL to call for the DNS update.")
parser.add_argument("-p", "--parameters", metavar="KEY=VALUE", nargs='+',
                    help="Set a number of key-value pairs to call the URL with. "
                         "No spaces before or after the = sign.")


logging.basicConfig(
    handlers=[logging.FileHandler(log_file_name), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s %(levelname)s %(message)s", datefmt="%B %d %H:%M:%S",
    level=logging.INFO)


def main():
    url, parameters, config_file = open_config_file()
    if not config_file:
        logging.info("Missing config file or missing required configuration. Looking for arguments.")
        args = parser.parse_args()
        url = args.url
        parameters = args.parameters
        if args.url is None or args.parameters is None:
            logging.error("Neither config file nor arguments present. Quitting.")
            print_config(url, parameters)
            quit()
        logging.info("Using command line arguments.")
        parameters = parse_vars(args.parameters)
    else:
        logging.info("Using config file.")
    ipv4_address = get_ipv4_address()
    logging.info("Public IPv4: " + ipv4_address)
    parameters['ipv4'] = ipv4_address
    patch_records(url, parameters)


def print_config(url, parameters):
    logging.info(f'URL: {url}' + '\t'
                 f'Parameters: {parameters}')


def open_config_file():
    config_file = True
    url = None
    parameters = None
    try:
        with open(config_file_name, 'r') as file:
            config_kv = yaml.safe_load(file)
    except FileNotFoundError:
        config_file = False
    if config_file:
        url = config_kv.get('url')
        if not url:
            logging.error("Missing URL in configuration file.")
            config_file = False
        parameters = config_kv.get('parameters')
        if not parameters:
            logging.error("Missing parameters in configuration file.")
            config_file = False

    return url, parameters, config_file


def get_ipv4_address():
    return requests.request("GET", "https://api4.ipify.org").text


def patch_records(url, parameters):
    response = requests.request("GET", url, params=parameters)
    logging.info("Response code: " + f'{response.status_code}')


def parse_vars(items):
    d = {}
    if items:
        for item in items:
            key, value = parse_var(item)
            d[key] = value
    return d


def parse_var(item):
    item = item.split('=')
    key = item[0].strip()
    value = item[1]
    #   value = '='.join(item[1:]) for emtpy spaces in values
    return key, value


main()
