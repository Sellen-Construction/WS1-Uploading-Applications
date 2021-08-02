import requests, json, base64, time, math, sys, os
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
            response = json.loads('{"status_code": 400, "text": "validation_error"}', object_hook = lambda d: SimpleNamespace(**d))
        
        return response
    
    def Call(self, endpoint, data, validate = False):
        response = self.__Call(endpoint, data)

        # If validate is passed True, keep retrying the API call until we are successful
        attempt_count = 1
        while validate and response.status_code != 200 and attempt_count <= 25:
            print(f"Validation failed with validate: True and status_code: {response.status_code}. Reattempting validation...")
            response = self.__Call(endpoint, data)
            attempt_count += 1

        return response

    def __GetChunks(self, file):
        chunk = file.read(Config.chunk_size)
        while chunk:
            yield chunk
            chunk = file.read(Config.chunk_size)

    def UploadAppChunk(self, filename):
            sequence_num = 1
            transaction_id = ""
            file_size = os.path.getsize(filename)
            
            with open(filename, "rb") as file:
                chunk_count, tail_size = divmod(file_size, Config.chunk_size)
                if chunk_count > 1:
                    print(f"Found file larger than {Config.chunk_size} bytes. Splitting into {chunk_count + 1} chunks...")

                for chunk in self.__GetChunks(file):
                    print(" " * 80, end = "\r")
                    print(f"Processing and uploading chunk {sequence_num}/{chunk_count + 1} ({math.floor((sequence_num / (chunk_count + 1)) * 100 * 100) / 100}%)", end = "\r")

                    data = {
                        "TransactionId": transaction_id,
                        "ChunkData": base64.b64encode(chunk).decode(),
                        "ChunkSequenceNumber": sequence_num,
                        "TotalApplicationSize": file_size,
                        "ChunkSize": Config.chunk_size
                    }
                    data = json.dumps(data)

                    result = self.Call("/mam/apps/internal/uploadchunk", data, True)
                    if result.status_code == 200:
                        sequence_num += 1
                        transaction_id = json.loads(result.text)['TranscationId']
                    else:
                        print() # Print an extra line so we can see the previous output
                        print(result.text, file = sys.stderr)
                print() # Print en extra line once we have finished uploading
            
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
        print(f"Creating app {filename} using uploaded data with {'Blob' if is_blob else 'Chunk'} ID: {app_id}")

        return self.Call("/mam/apps/internal/begininstall", data, True)

class Public:
    def __init__(self):
        self.core = Core()

    def UploadApp(self, filename, type):
        is_blob = type == "blob"
        return self.core.CreateApp(filename, self.core.UploadAppBlob(filename) if is_blob else self.core.UploadAppChunk(filename), is_blob)