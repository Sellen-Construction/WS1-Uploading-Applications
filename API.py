import requests, json, base64, time, math, sys
import Config, JSON
from types import SimpleNamespace

# Open connection up to Logjam attack due to limitations of the WS1 API.
# TODO: REMOVE THE LINE BELOW WHEN THE API IS UPDATED TO REMOVE THIS VULNERABILITY!!!!
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT:!DH'

class Token:
    def Get(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": Config.id,
            "client_secret": Config.secret
        }

        result = requests.post(Config.token_url, data = data)
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
    def Validate(self):
        if int(time.time()) >= int(Config.token_expiry) - 600:
            self.Get()

class Core:
    def __init__(self):
        self.token = Token()
    
    def __Call(self, endpoint, data):
        try:
            response = ""
            self.token.Validate()
            response = requests.post(Config.base_url + endpoint, headers = Config.header, data = data)
        except Exception as ex:
            print(ex)
            if "text" in response:
                print(response.text)
            response = json.loads('{"status_code": 400, "text": "token_error"}', object_hook = lambda d: SimpleNamespace(**d))
        
        return response
    
    def Call(self, endpoint, data, validate = False):
        response = self.__Call(endpoint, data)

        # If validate is passed True, keep retrying the API call until we are successful
        while validate and response.status_code != 200:
            print(f"Validation failed with validate: True and status_code: {response.status_code}. Reattempting validation...")
            response = self.__Call(endpoint, data)

        return response

    def UploadAppChunk(self, filename):
            with open(filename, "rb") as file:
                bytes = file.read()

                if len(bytes) > Config.chunk_size:
                    chunk_count, tail_size = divmod(len(bytes), Config.chunk_size)
                    print(f"Found file larger than {Config.chunk_size} bytes. Splitting into {chunk_count + 1} chunks...")

                    current_byte = 0
                    sequence_num = 1
                    transaction_id = ""

                    for _ in range(0, chunk_count):
                        print(" " * 80, end = "\r")
                        print(f"Processing and uploading chunk {sequence_num}/{chunk_count + 1} ({math.floor((sequence_num / (chunk_count + 1)) * 100 * 100) / 100}%)", end = "\r")
                        data = {
                            "TransactionId": transaction_id,
                            "ChunkData": base64.b64encode(bytes[current_byte : current_byte + Config.chunk_size]).decode(),
                            "ChunkSequenceNumber": sequence_num,
                            "TotalApplicationSize": len(bytes),
                            "ChunkSize": Config.chunk_size
                        }
                        data = json.dumps(data)

                        result = self.Call("/mam/apps/internal/uploadchunk", data, True)
                        if result.status_code == 200:
                            current_byte += Config.chunk_size
                            sequence_num += 1
                            transaction_id = json.loads(result.text)['TranscationId']
                        else:
                            print(result.text, file = sys.stderr)

                    if tail_size > 0:
                        print(" " * 80, end = "\r")
                        print(f"Processing and uploading chunk {sequence_num}/{chunk_count + 1} ({math.floor((sequence_num / (chunk_count + 1)) * 100 * 100) / 100}%)")
                        data = {
                            "TransactionId": transaction_id,
                            "ChunkData": base64.b64encode(bytes[current_byte :]).decode(),
                            "ChunkSequenceNumber": sequence_num,
                            "TotalApplicationSize": len(bytes),
                            "ChunkSize": tail_size
                        }
                        data = json.dumps(data)

                        result = self.Call("/mam/apps/internal/uploadchunk", data, True)
                else:
                    file.seek(0)
                    data = {
                        "TransactionId": "",
                        "ChunkData": base64.b64encode(bytes).decode(),
                        "ChunkSequenceNumber": 1,
                        "TotalApplicationSize": len(bytes),
                        "ChunkSize": len(bytes)
                    }
                    data = json.dumps(data)

                    result = self.Call("/mam/apps/internal/uploadchunk", data, True)
                    transaction_id = json.loads(result.text)['TranscationId']
            return transaction_id

    def UploadAppBlob(self, filename):
        blob_id = ""
        with open(filename, "rb") as file:
            print(f"Uploading {filename} as a Blob...")
            result = self.Call(f"/mam/blobs/uploadblob?filename={filename}&organizationGroupId=14522&moduleType=Application", file.read())
            print(result.text)
            blob_id = json.loads(result.text)['Value']

        return blob_id

    def CreateApp(self, filename, app_id, is_blob):
        data = JSON.GetBlob(filename, app_id) if is_blob else JSON.GetChunk(filename, app_id)
        print(data)

        return self.Call("/mam/apps/internal/begininstall", data, False)

class Public:
    def __init__(self):
        self.cloud = Core()

    def UploadApp(self, filename, type):
        is_blob = type == "blob"
        return self.cloud.CreateApp(filename, self.cloud.UploadAppBlob(filename) if is_blob else self.cloud.UploadAppChunk(filename), is_blob)