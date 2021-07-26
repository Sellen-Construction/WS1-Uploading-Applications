import requests, json, sys, base64, time, math
import Config
from types import SimpleNamespace

if len(sys.argv) <= 1:
    print("Please include a file name")
    quit()

#Open connection up to Logjam attack due to limitations of the WS1 API.
#TODO: REMOVE THE LINE BELOW WHEN THE API IS UPDATED TO REMOVE THIS VULNERABILITY!!!!
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT:!DH'

def GetToken():
    data = {
        "grant_type": "client_credentials",
        "client_id": Config.id,
        "client_secret": Config.secret
    }

    result = requests.post(Config.token_url, data=data)
    if result.status_code == 200:
        token_data = json.loads(result.text)
        Config.token_expiry = time.time() + token_data['expires_in']
        Config.header = {
            "Authorization": f"Bearer {token_data['access_token']}",
            "aw-tenant-code": Config.key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    else:
        raise ConnectionError(f"Failed to refresh token: {result.text}")

# Check to make sure our token is still valid, get a fresh token otherwise
# This should be called before every request to the API
def ValidateToken():
    if int(time.time()) >= int(Config.token_expiry) - 600:
        GetToken()

def CallAPI(endpoint, data, validate = False):
    try:
        ValidateToken()
        response = requests.post(Config.base_url + endpoint, headers = Config.header, data = data)
    except:
        response = json.loads('{"status_code": 400, "text": "token_error"}', object_hook = lambda d: SimpleNamespace(**d))

    # If validate is passed True, keep retrying the API call until we are successful
    while validate and response.status_code != 200:
        try:
            ValidateToken()
            response = requests.post(Config.base_url + endpoint, headers = Config.header, data = data)
        except:
            response = json.loads('{"status_code": 400, "text": "token_error"}', object_hook = lambda d: SimpleNamespace(**d))
    
    return response

def UploadAppChunks():
    with open(sys.argv[1], "rb") as file:
        bytes = file.read()

        if len(bytes) > Config.chunk_size:
            chunk_count, tail_size = divmod(len(bytes), Config.chunk_size)
            print(f"Found file larger than {Config.chunk_size} bytes. Splitting into {chunk_count + 1} chunks...")

            current_byte = 0
            sequence_num = 1
            transaction_id = ""

            for _ in range(0, chunk_count):
                print("\x1b[2K", end = "")
                print(f"Processing and uploading chunk {sequence_num}/{chunk_count + 1} ({math.floor((sequence_num / (chunk_count + 1)) * 100 * 100) / 100}%)", end = "\r")
                data = {
                    "TransactionId": transaction_id,
                    "ChunkData": base64.b64encode(bytes[current_byte : current_byte + Config.chunk_size]).decode(),
                    "ChunkSequenceNumber": sequence_num,
                    "TotalApplicationSize": chunk_count + (1 if tail_size > 0 else 0), # Should this be the total size in bytes or the total chunk count? The API doesn't seem to care, using either doesn't appear to make a difference.
                    "ChunkSize": Config.chunk_size
                }
                data = json.dumps(data)

                result = CallAPI("/mam/apps/internal/uploadchunk", data, False)
                if result.status_code == 200:
                    current_byte += Config.chunk_size
                    sequence_num += 1
                    transaction_id = json.loads(result.text)['TranscationId']
                else:
                    print(result.text)

            if tail_size > 0:
                print("\x1b[2K", end = "")
                print(f"Processing and uploading chunk {sequence_num}/{chunk_count + 1} ({math.floor((sequence_num / (chunk_count + 1)) * 100 * 100) / 100}%)")
                data = {
                    "TransactionId": transaction_id,
                    "ChunkData": base64.b64encode(bytes[current_byte :]).decode(),
                    "ChunkSequenceNumber": sequence_num,
                    "TotalApplicationSize": chunk_count + (1 if tail_size > 0 else 0), # Should this be the total size in bytes or the total chunk count? The API doesn't seem to care, using either doesn't appear to make a difference.
                    "ChunkSize": tail_size
                }
                data = json.dumps(data)

                result = CallAPI("/mam/apps/internal/uploadchunk", data, False)
        else:
            file.seek(0)
            data = {
                    "TransactionId": "",
                    "ChunkData": base64.b64encode(bytes).decode(),
                    "ChunkSequenceNumber": 1,
                    "TotalApplicationSize": 1, # Should this be the total size in bytes or the total chunk count? The API doesn't seem to care, using either doesn't appear to make a difference.
                    "ChunkSize": len(bytes)
                }
            data = json.dumps(data)

            result = CallAPI("/mam/apps/internal/uploadchunk", data, False)
            transaction_id = json.loads(result.text)['TranscationId']
    return transaction_id

def UploadAppBlob():
    blob_id = ""
    with open(sys.argv[1], "rb") as file:
        print(f"Uploading {sys.argv[1]} as a Blob...")
        result = CallAPI(f"/mam/blobs/uploadblob?filename={sys.argv[1]}&organizationGroupId=14522&moduleType=Application", file.read())
        print(result.text)
        blob_id = json.loads(result.text)['Value']

    return blob_id

def CreateApp(app_id, blob = False):    
    data = {
        "BlobId" if blob else "TranscationId": f"{app_id}",
        "DeviceType": "12",
        "ApplicationName": "TestApp",
        "SupportedModels": {
            "Model": [
                {
                    "ModelId": 223,
                    "ModelName": "Windows 10"
                }
            ]
        },
        "PushMode": "OnDemand",
        "Description": "Text value",
        "EnableProvisioning": True,
        "UploadViaLink": False,
        "FileName": sys.argv[1],
        "IsDependencyFile": False,
        "LocationGroupId": 14522
    }

    data = json.dumps(data)
    print(data)

    return CallAPI("/mam/apps/internal/begininstall", data)


# Set run to "blob" to upload file as Blob data or "chunk" to upload in Chunks
run = "chunk"

run_blob = run == "blob"
result = CreateApp(UploadAppBlob() if run_blob else UploadAppChunks(), run_blob)
print(result.text)