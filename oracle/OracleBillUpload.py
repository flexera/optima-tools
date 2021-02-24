import os
import json
import logging
import requests
import sys
import time

# Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)

refresh_token = os.environ.get('REFRESH_TOKEN')
org_id = os.environ.get('ORG_ID')
bill_connect_id = os.environ.get("BILL_CONNECT_ID")
period = os.environ.get("PERIOD")
shard = os.environ.get("SHARD")
if not shard == 3 and not shard == 4:
  logging.error('Invalid Shard Number' + shard)
  sys.exit(1)

logging.info("Using org_id {}, bill_connect_id {}, period {}".format(
             org_id, bill_connect_id, period))

token_url = "https://us-"+ shard +".rightscale.com/api/oauth2"
bill_upload_url = "https://optima-bill-upload-front.indigo.rightscale.com/optima/orgs/{}/billUploads".format(org_id)

logging.info("OAuth2: Getting Access Token via Refresh Token...")
r = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"X-API-Version": "1.5"})
r.raise_for_status()
access_token = r.json()["access_token"]

# ===== Use Access Token as Bearer token from them on ===== #
auth_headers = {"Authorization": "Bearer " + access_token}
kwargs = {"headers": auth_headers, "allow_redirects": False}

logging.info("1. Creating Bill Upload...")
bill_upload = {"billConnectId": bill_connect_id, "billingPeriod": period}
r = requests.post(bill_upload_url, json.dumps(bill_upload), **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()
bill_upload_id = r.json()["id"]

# uploading files to endpoint
dir_path =  os.path.dirname(os.path.realpath(__file__))
json_file = os.path.join(dir_path, 'files.json')

with open(json_file) as f:
  data = json.load(f)

for filename in data:
  base_name = os.path.basename(filename)
  logging.info("2. Upload file {} to Bill Upload {}...".format(base_name, bill_upload_id))
  upload_file_url = "{}/{}/files/{}".format(bill_upload_url, bill_upload_id, base_name)
  r = requests.post(upload_file_url, data=open(filename, 'rb').read(), **kwargs)
  logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))

logging.info("3. Committing the Bill Upload {}...".format(bill_upload_id))
operations_url = "{}/{}/operations".format(bill_upload_url, bill_upload_id)
r = requests.post(operations_url, '{"operation":"commit"}', **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()

# ===== That's all, folks! =====
sys.exit(0)
