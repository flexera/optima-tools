import json
import logging
import requests
import sys
import time
import csv
import datetime

CLOUD_VENDOR_ACCOUNT_ID = 'cluster1'
DATE = datetime.datetime.now()
IYM = '2020-08'

r = requests.get("http://34.69.242.82/model/aggregatedCostModel?window=1d&aggregation=pod&allocateIdle=true&rate=hourly")
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
    'InvoiceYearMonth'
  ]
]
for x in j["data"]:
  arr_cbi.append([
    CLOUD_VENDOR_ACCOUNT_ID, 
    'kubernetes', 
    'Compute', 
    j["data"][x]["aggregation"], 
    'Usage', 
    x.split('/')[0], 
    'pod', 
    x, 
    'Kubernetes',
    {},
    1,
    'TotalCost',
    j["data"][x]['totalCost'],
    'USD',
    DATE,
    IYM
    ])
for item in arr_cbi:
  print(','.join(map(str,item)))