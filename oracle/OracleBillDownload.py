import oci
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

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
prefix_file = ""                     #  For cost and usage files
# prefix_file = "reports/cost-csv"   #  For cost
# prefix_file = "reports/usage-csv"  #  For usage

# Update these values
destintation_path = 'CBI'

# Download all file or just past three months.
env_download_all = os.environ.get("DOWNLOAD_ALL")
download_all_files = bool(env_download_all)

# Make a directory to receive reports
if not os.path.exists(destintation_path):
    os.mkdir(destintation_path)

# Get the list of reports
config = oci.config.from_file(oci.config.DEFAULT_LOCATION, oci.config.DEFAULT_PROFILE)
reporting_bucket = config['tenancy']
object_storage = oci.object_storage.ObjectStorageClient(config)
report_bucket_objects = object_storage.list_objects(reporting_namespace, reporting_bucket, prefix=prefix_file, fields='name,etag,timeCreated,md5,timeModified,storageTier,archivalState')

# Do date stuff
utc=pytz.UTC
now = datetime.now()
last_three_months = utc.localize(now) + relativedelta(months=-3)

for o in report_bucket_objects.data.objects:
  if download_all_files:
    download = True
  elif o.time_modified >= last_three_months:
    print("Downloading files from " + last_three_months.strftime("%Y-%m") + " to " + now.strftime("%Y-%m"))
    download = True
  else:
    download = False

  if download:
    print('Found file ' + o.name)
    folder_time = o.time_modified.strftime("%Y-%m")
    download_folder = os.path.join(destintation_path,folder_time)
    # Make a directory to receive reports
    if not os.path.exists(download_folder):
      os.mkdir(download_folder)

    object_details = object_storage.get_object(reporting_namespace, reporting_bucket, o.name)
    filename = o.name.rsplit('/', 1)[-1]

    with open(download_folder + '/' + filename, 'wb') as f:
        for chunk in object_details.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)

    print('----> File ' + o.name + ' Downloaded')

