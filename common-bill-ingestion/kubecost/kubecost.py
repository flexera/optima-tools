import json
import logging
import requests
import sys
import time
import csv
import datetime
import click
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import calendar
import csv

# Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)

CLOUD_VENDOR_ACCOUNT_ID = 'cluster1'
DATE = datetime.datetime.now()
IYM = DATE.strftime("%Y-%m")
refresh_token = '1984132d9be38cd7186e8e25f7ef9081047c9911'
org_id = 5723
bill_connect_id = "cbi-oi-optima-kubecost1"
shard = "4"
token_url = "https://us-"+ shard +".rightscale.com/api/oauth2"
period = IYM
bill_upload_url = "https://optima-bill-upload-front.indigo.rightscale.com/optima/orgs/{}/billUploads".format(org_id)


#https://stackoverflow.com/questions/57274902/python-iterate-over-all-days-in-a-month
def date_iter(year, month):
  intMonth = int(month)
  intYear = int(year)
  x = calendar._monthlen(intYear, intMonth) + 1
  for i in range(1, x):
      yield datetime.date(intYear, intMonth, i)

files_to_upload = []

for d in date_iter(DATE.strftime("%Y"), DATE.strftime("%#m")):
  if d > datetime.datetime.now().date():
    continue
  else:
    url = "http://34.69.242.82/model/aggregatedCostModel?window="+d.strftime("%Y-%m-%dT00:00:00Z")+","+d.strftime("%Y-%m-%dT23:59:59Z")+"&aggregation=deployment&allocateIdle=true"
    logging.info("Generating Bill from " + url)
    r = requests.get(url)
    r.raise_for_status()
    j = json.loads(r.text)
    data = j["data"]

    arr_cbi = [
      [
        'CloudVendorAccountID',
        'CloudVendorAccountName',
        'Category',
        'LineItemType',
        'ResourceGroup',
        'ResourceType',
        'ResourceID',
        'Service',
        'Tags',
        'UsageAmount',
        'UsageUnit',
        'Cost',
        'CurrencyCode',
        'UsageStartTime',
        'InvoiceYearMonth',
        'ManufacturerName'
      ]
    ]

    for x in j["data"]:
      arr_cbi.append([
        CLOUD_VENDOR_ACCOUNT_ID,
        'kubernetes',
        'Compute',
        'Usage',
        x.split('/')[0],
        j["data"][x]["aggregation"],
        x,
        'Kubernetes',
        {},
        1,
        'TotalCost',
        j["data"][x]['totalCost'],
        'USD',
        d.strftime("%Y-%m-%dT00:00:00Z"),
        IYM,
        'Google'
        ])

    dir_path =  os.path.dirname(os.path.realpath(__file__))
    csv_file = os.path.join(dir_path, 'kubecost-'+d.strftime("%Y-%m-%d")+'.csv')
    files_to_upload.append(csv_file)
    with open(csv_file,'w',newline='') as outFile:
      csv_writer = csv.writer(outFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      for item in arr_cbi:
        csv_writer.writerow(item)

logging.info("OAuth2: Getting Access Token via Refresh Token...")
r = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"X-API-Version": "1.5"})
r.raise_for_status()
access_token = r.json()["access_token"]

# ===== Use Access Token as Bearer token from them on ===== #
auth_headers = {"Authorization": "Bearer " + access_token}
kwargs = {"headers": auth_headers, "allow_redirects": False}

logging.info("Using org_id {}, bill_connect_id {}, period {}".format(
            org_id, bill_connect_id, period))
logging.info("1. Creating Bill Upload for Period:" + period)
bill_upload = {"billConnectId": bill_connect_id, "billingPeriod": period}
r = requests.post(bill_upload_url, json.dumps(bill_upload), **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()
bill_upload_id = r.json()["id"]

for fileName in files_to_upload:
  base_name = os.path.basename(fileName)
  logging.info("2. Upload file {} to Bill Upload {}...".format(base_name, bill_upload_id))
  upload_file_url = "{}/{}/files/{}".format(bill_upload_url, bill_upload_id, base_name)
  r = requests.post(upload_file_url, data=open(fileName, 'rb').read(), **kwargs)
  logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))

logging.info("3. Committing the Bill Upload {}...".format(bill_upload_id))
operations_url = "{}/{}/operations".format(bill_upload_url, bill_upload_id)
r = requests.post(operations_url, '{"operation":"commit"}', **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()

# ===== That's all, folks! =====
sys.exit(0)
