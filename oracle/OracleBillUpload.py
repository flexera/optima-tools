
import oci
import os
import json
import logging
import requests
import sys
import time
				
# This script downloads all of the cost, usage, (or both) reports for a tenancy (specified in the config file).
#
# Pre-requisites: Create an IAM policy to endorse users in your tenancy to read cost reports from the OCI tenancy.
#
# Example policy:
# define tenancy reporting as ocid1.tenancy.oc1..aaaaaaaaned4fkpkisbwjlr56u7cj63lf3wffbilvqknstgtvzub7vhqkggq
# endorse group group_name to read objects in tenancy reporting
#
# Note - The only value you need to change is the group name. Do not change the OCID in the first statement.
				
reporting_namespace = 'bling'
				
# Download all usage and cost files. You can comment out based on the specific need:
# prefix_file = ""                     #  For cost and usage files
prefix_file = "reports/cost-csv"   #  For cost
# prefix_file = "reports/usage-csv"  #  For usage
				
# Update these values
destintation_path = 'downloaded_reports'
				
# Make a directory to receive reports
if not os.path.exists(destintation_path):
    os.mkdir(destintation_path)
				
# Get the list of reports
config = oci.config.from_file(oci.config.DEFAULT_LOCATION, oci.config.DEFAULT_PROFILE)
reporting_bucket = config['tenancy']
object_storage = oci.object_storage.ObjectStorageClient(config)
report_bucket_objects = object_storage.list_objects(reporting_namespace, reporting_bucket, prefix=prefix_file)
				
for o in report_bucket_objects.data.objects:
    print('Found file ' + o.name)
    object_details = object_storage.get_object(reporting_namespace, reporting_bucket, o.name)
    filename = o.name.rsplit('/', 1)[-1]
				
    with open(destintation_path + '/' + filename, 'wb') as f:
        for chunk in object_details.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
				
    print('----> File ' + o.name + ' Downloaded')

'''
Basic Bill Upload example 2
---------------------------
Creates a bill upload, uploads a file, then commits that bill_upload.
Note: it's OK to create a new upload for a given org_id, bill connect and period,
provided any previous one (for that same org_id/bill connect/period) has been committed (or aborted).
 
Usage: ./bill_upload_example2.py <refresh_token> <org_id> <bill_connect_id> <period> <filename>
 
Parameters:
<refresh token>:   obtained from Cloud Management:
                   - go to Settings, then API Credentials in the Account Settings;
                   - enable the token and pass its value to this script.
<org_id>:          the relevant organization id, e.g. "25667"
<bill_connect_id>: for WotC, for now, please use "cbi-wotc-1"
<period>:          the billing month in YYYY-MM format, e.g. "2020-06"
<filename>:        the file path, e.g. "./testfiles/my_file01.csv"

 
# Tweak the destination (e.g. sys.stdout instead) and level (e.g. logging.DEBUG instead) to taste!
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stderr, level=logging.INFO)
 
if len(sys.argv) < 6:
    logging.error('Missing command-line options!!!')
    print(__doc__)
    sys.exit(1)
 
refresh_token, org_id, bill_connect_id, period, filename = sys.argv[1:]
logging.info("Using org_id {}, bill_connect_id {}, period {}, filename {}".format(
             org_id, bill_connect_id, period, filename))
 
if org_id == "25667" and bill_connect_id != "cbi-wotc-1":
    logging.error('For org 25667, please use bill_connect_id cbi-wotc-1, not {}'.format(bill_connect_id))
    sys.exit(1)
 
token_url = "https://us-3.rightscale.com/api/oauth2"
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
 
logging.info("2. Upload file {} to Bill Upload {}...".format(filename, bill_upload_id))
upload_file_url = "{}/{}/files/{}".format(bill_upload_url, bill_upload_id, filename)
r = requests.post(upload_file_url, data=open(filename, 'rb').read(), **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
 
logging.info("3. Committing the Bill Upload {}...".format(bill_upload_id))
operations_url = "{}/{}/operations".format(bill_upload_url, bill_upload_id)
r = requests.post(operations_url, '{"operation":"commit"}', **kwargs)
logging.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
r.raise_for_status()
 
# ===== That's all, folks! =====
sys.exit(0)

'''