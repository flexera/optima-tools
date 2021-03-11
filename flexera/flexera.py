import os
import json
import logging
import requests
import click
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning

@click.command()
@click.option('--refresh-token', prompt="Refresh Token", help='Refresh Token from CM or FlexeraOne')
@click.option('--shard', type=click.Choice(['3', '4', 'F1'], case_sensitive=False), prompt='Shard for authentication', help='Shard for authentication')
@click.option('--disable-tls-verify', is_flag=True)

def cli(shard, refresh_token, disable_tls_verify):
  access_token = auth(shard, refresh_token, disable_tls_verify)
  return access_token

def auth(shard, refresh_token, disable_tls_verify):
  if shard not in ['F1','3','4']:
    logging.error('Invalid Shard Number ' + shard)
    sys.exit(1)

  if shard == 'F1':
    token_url = "https://login.flexera.com/oidc/token"
  else:
    token_url = "https://us-"+ shard +".rightscale.com/api/oauth2"

  if disable_tls_verify:
    urllib3.disable_warnings(InsecureRequestWarning)
    tls_verify = False
  else:
    tls_verify = True

  logging.info("OAuth2: Getting Access Token via Refresh Token...")
  r = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"X-API-Version": "1.5"}, verify=tls_verify)
  r.raise_for_status()
  access_token = r.json()["access_token"]
  click.echo(access_token)
  return access_token

if __name__ == '__main__':
  # click passes no args
  # pylint: disable=no-value-for-parameter
  cli()
