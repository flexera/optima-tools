import logging
import json
import os
import requests
import sys
import time
import oss2

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential


def handler(event, context):

    def authenticate( token_url, refresh_token, api_version, logger):
        logger.info("authenticate using token_url {}, api_version {}".format(
                     token_url, api_version))

        logger.info("OAuth2: Getting Access Token via Refresh Token...")
        r = requests.post(token_url, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"X-API-Version": api_version})
        r.raise_for_status()
        access_token = r.json()["access_token"]
        return access_token

    def create_bill_upload( base_upload_url, access_token, org_id, bill_connect_id, period, logger):

        logger.info("create_bill_upload using base_upload_url {}, org_id {}, bill_connect_id {}, period {}".format(
                     base_upload_url, org_id, bill_connect_id, period))

        bill_upload_url = "{}/{}/billUploads".format(base_upload_url, org_id)

        # ===== Use Access Token as Bearer token from them on ===== #
        auth_headers = {"Authorization": "Bearer " + access_token}
        kwargs = {"headers": auth_headers, "allow_redirects": False}

        logger.info("1. Creating Bill Upload...")
        bill_upload = {"billConnectId": bill_connect_id, "billingPeriod": period}
        r = requests.post(bill_upload_url, json.dumps(bill_upload), **kwargs)
        logger.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
        r.raise_for_status()
        bill_upload_id = r.json()["id"]
        return bill_upload_id

    def upload_file( base_upload_url, access_token, org_id, bill_connect_id, period, bill_upload_id,  s3_object, filename, logger):

        logger.info("upload_file using base_upload_url {}, org_id {}, bill_connect_id {}, period {}, bill upload ID {} filename {}".format(
                     base_upload_url, org_id, bill_connect_id, period, bill_upload_id, filename))

        bill_upload_url = "{}/{}/billUploads".format(base_upload_url, org_id)

        # ===== Use Access Token as Bearer token from them on ===== #
        auth_headers = {"Authorization": "Bearer " + access_token}
        kwargs = {"headers": auth_headers, "allow_redirects": False}

        logger.info("2. Upload file {} to Bill Upload {}...".format(filename, bill_upload_id))
        upload_file_url = "{}/{}/files/{}".format(bill_upload_url, bill_upload_id, filename)
        r = requests.post(upload_file_url, data=s3_object.read(), **kwargs)
        logger.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
        r.raise_for_status()

    def commit_bill_upload( base_upload_url, access_token, org_id, bill_connect_id, period, bill_upload_id, logger):

        logger.info("Using base_upload_url {}, org_id {}, bill_connect_id {}, period {}, bill upload ID {}".format(
                     base_upload_url, org_id, bill_connect_id, period, bill_upload_id))

        bill_upload_url = "{}/{}/billUploads".format(base_upload_url, org_id)

        # ===== Use Access Token as Bearer token from them on ===== #
        auth_headers = {"Authorization": "Bearer " + access_token}
        kwargs = {"headers": auth_headers, "allow_redirects": False}

        logger.info("3. Committing the Bill Upload {}...".format(bill_upload_id))
        operations_url = "{}/{}/operations".format(bill_upload_url, bill_upload_id)
        r = requests.post(operations_url, '{"operation":"commit"}', **kwargs)
        logger.info("Response: {}\n{}".format(r.status_code, json.dumps(r.json(), indent=4)))
        r.raise_for_status()

    def download_oss_objects_for_month(account_id, bucket, year, month, max_day, logger):
        logger.info("download_oss_objects_for_month using account_id {}, year {}, month {}, max_day {}".format(
                        account_id,  year, month, max_day))
        res = []

        for i in range(1, max_day) :
            key = account_id + "_ACE1_BillingItemDetail_" + str(year) + str(month).zfill(2) + str(i).zfill(2)
            logger.info("downloading OSS object {}".format(
                                    key))
            try:
                s3_object = bucket.get_object(key)
                item = {}
                item['key'] = key
                item['s3_object'] = s3_object
                res.append(item)
            except:
                logger.warning("Unable to download {} = {}".format(key, sys.exc_info()[0]))

        return res

    def subscribe_billing(clt, bucket_name, bucket_owner_id):

        print("subscribe_billing")
        req = CommonRequest()
        req.set_accept_format('json')
        req.set_domain('business.ap-southeast-1.aliyuncs.com')
        req.set_method('POST')
        req.set_version('2017-12-14')
        req.set_action_name('SubscribeBillToOSS')
        req.add_query_param('MultAccountRelSubscribe', 'ACE1')
        req.add_query_param('BucketOwnerId', bucket_owner_id)
        req.add_query_param('SubscribeBucket', bucket)
        req.add_query_param('SubscribeType', "BillingItemDetailForBillingPeriod")

        print(req)

        res = json.loads(clt.do_action(req))

        print(res)

        return res

    print(event)
    event_json = json.loads(event)

    logger = logging.getLogger()
    logger.info(event_json)

    creds = context.credentials

    if "action" in event_json and event_json["action"]=="subscribe":
        sts_token_credential = StsTokenCredential(creds.access_key_id, creds.access_key_secret, creds.security_token)
        acs_client = AcsClient(region_id=region, credential=sts_token_credential)

        # ===== Getting settings from env ===== #

        bucket_name = os.getenv("BUCKET_NAME", None)
        bucket_owner_id = os.getenv("BUCKET_OWNER_ID", None)

        return subscribe_billing(acs_client, bucket_name, bucket_owner_id)
    else:
        # TODO => get from KMS

        refresh_token = os.getenv("REFRESH_TOKEN", None)

        # ===== Getting settings from env ===== #

        account_id = os.getenv("ACCOUNT_ID", None)
        region = os.getenv("REGION", None)
        org_id = os.getenv("RIGHTSCALE_ORG_ID", None)
        bill_connect_id = os.getenv("RIGHTSCALE_BILL_CONNECT_ID", None)
        api_version = os.getenv("RIGHTSCALE_API_VERSION", None)
        token_url = os.getenv("RIGHTSCALE_TOKEN_URL", None)
        base_upload_url = os.getenv("RIGHTSCALE_BASE_UPLOAD_URL", None)

        auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)

        access_token = authenticate(token_url, refresh_token, api_version, logger)

        for oss_event in event_json["events"]:
            logger.info("New OSS event", oss_event)
            oss_source = oss_event["oss"]
            oss_source_bucket = oss_source["bucket"]
            oss_source_object = oss_source["object"]
            key = oss_source_object["key"]

            if key.find("ACE1") < 0:
                logger.info("Skipping Non ACE1 object %s", key)
                return "ignored"

            dt = ""
            i = key.rfind("_")
            if i < 0 or (len(key) -i) < 9 :
                logger.error("Invalid ACE1 filename %s", key)
                return "invalid_object_key"

            year = int(key[i+1:i+5])
            month = int(key[i+5:i+7])
            day = int(key[i+7:i+9])

            period = str(year) + "-" + str(month).zfill(2)
            logger.info("Billing period detected = %", period)

            bill_upload_id = create_bill_upload(base_upload_url, access_token, org_id, bill_connect_id, period, logger )

            logger.info("Bill upload ID = " + bill_upload_id)

            bucket = oss2.Bucket(auth, 'http://oss-cn-hangzhou.aliyuncs.com', oss_source_bucket["name"])

            objects = download_oss_objects_for_month(account_id, bucket, year, month, day, logger)

            for obj in objects:
                filename = obj['key'] + '.csv'
                upload_file( base_upload_url, access_token, org_id, bill_connect_id, period, bill_upload_id, obj['s3_object'], filename, logger)

            commit_bill_upload( base_upload_url, access_token, org_id, bill_connect_id, period, bill_upload_id, logger)

