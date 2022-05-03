import io
import json
import oci
import requests
import datetime
from fdk import response

API_KEY = "2r4ZmC5j*********IYi"

def handler(ctx, data: io.BytesIO = None):
    signer = oci.auth.signers.get_resource_principals_signer()
    print(signer)
    data = requests.get(f"https://api.nytimes.com/svc/mostpopular/v2/viewed/1.json?api-key={API_KEY}").json()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
        namespace = object_storage_client.get_namespace().data
        object_storage_client.put_object(namespace,
            bucket_name=“DE-Bucket",
            object_name=f"NYT-{timestamp}",
            put_object_body=json.dumps(data).encode(),
            content_type="application/json")

        resp_data = {"status":"200"}
        return response.Response( ctx, response_data=resp_data, headers={"Content-Type": "application/json"})
    except oci.exceptions.ServiceError as inst:
        return response.Response( ctx, response_data=inst, headers={"Content-Type": "application/json"})
