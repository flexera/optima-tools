'''
Bill Connect Tool
---------------------------
Creates a bill connect and returns the response
Usage: python create_bill_connect.py <refresh_token> <shard> <org_id> <cbi_integration_id> <cbi_bill_identifier> <cbi_name> <cbi_params>

Parameters:
<refresh token>:        obtained from Cloud Management:
                        - go to Settings, then API Credentials in the Account Settings;
                        - enable the token and pass its value to this script.
<shard>:                3 or 4 depending on where cm account is. Check url bar in above setting.
<org_id>:               the relevant organization id, e.g. "12345"
<cbi_integration_id>:   the integration id (linked to that integration mentioned just above), e.g. "cbi-oi-optima";
                        - Possible integration ids: “cbi-oi-optima” (Optima CSV default format),
                        - but also "cbi-oi-oracle", “cbi-oi-alibaba” and “cbi-oi-azure-china”
                        - (talk to your Flexera account manager for those last three);
<cbi_bill_identifier>:  a bill identifier of your choice, alphanumeric (or - or _)
                        - sequence uniquely identifying this bill connect of this integration type for your organization, e.g. "test-1";
<cbi_name>:             a name/description, a human-readable string to give more information, e.g. "My test Optima CSV integration, number One";
<cbi_params>:           a parameter object in json to override the default integration settings. Pass an empty one if you are not passing any such parameters,
                        e.g. '{}'.
'''
import os
import json
import logging
import requests
import sys
import time

# Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)

if len(sys.argv) < 8:
    logging.error('Missing command-line options!!!')
    print(__doc__)
    sys.exit(1)

refresh_token, shard, org_id, cbi_integration_id, cbi_bill_identifier, cbi_name, cbi_params = sys.argv[1:]
logging.info("Using org_id {}, cbi_integration_id {}, cbi_bill_identifier {}, cbi_name {}, cbi_params {}".format(
             org_id, cbi_integration_id, cbi_bill_identifier, cbi_name, cbi_params))

if not shard == '3':
  if not shard == '4':
    logging.error('Invalid Shard Number ' + shard)
    sys.exit(1)

json_cbi_params = json.loads(cbi_params)
if type(json_cbi_params) is not type({}):
  logging.error("cbi_params is not of type dict")
  sys.exit(1)

logging.info("Using org_id {}".format(org_id))



token_url = "https://us-"+ shard +".rightscale.com/api/oauth2"
logging.info("OAuth2: Getting Access Token via Refresh Token...")
r = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"X-API-Version": "1.5"})
r.raise_for_status()
access_token = r.json()["access_token"]

# ===== Use Access Token as Bearer token from them on ===== #
auth_headers = {"Api-Version": "1.0", "Authorization": "Bearer " + access_token}
kwargs = {"headers": auth_headers, "allow_redirects": False}

bill_connect_url = "https://onboarding.rightscale.com/api/onboarding/orgs/{}/bill_connects/cbi".format(org_id)
bill_connect = {
  "cbi_bill_identifier": cbi_bill_identifier,
  "cbi_integration_id": cbi_integration_id,
  "cbi_name": cbi_name,
  "cbi_params": json_cbi_params
}
r = requests.post(bill_connect_url, json.dumps(bill_connect), **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()
