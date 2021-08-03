# This file contains everything needed to upload an application

import API.Config as Config, API.JSON_DATA as JSON_DATA
from API.Core import Core
import os, math, base64, json, sys

class Application:
    def __GetChunks(file):
        chunk = file.read(Config.chunk_size)
        while chunk:
            yield chunk
            chunk = file.read(Config.chunk_size)

    def UploadChunk(filename):
            sequence_num = 1
            transaction_id = ""
            file_size = os.path.getsize(filename)
            
            with open(filename, "rb") as file:
                chunk_count, tail_size = divmod(file_size, Config.chunk_size)
                chunk_count += 1 if tail_size > 0 else 0
                if chunk_count > 1:
                    print(f"Found file larger than {Config.chunk_size} bytes. Splitting into {chunk_count} chunks...")

                for chunk in Application.__GetChunks(file):
                    print(" " * 80, end = "\r")
                    print(f"Processing and uploading chunk {sequence_num}/{chunk_count} ({math.floor((sequence_num / (chunk_count)) * 100 * 100) / 100}%)", end = "\r")

                    data = {
                        "TransactionId": transaction_id,
                        "ChunkData": base64.b64encode(chunk).decode(),
                        "ChunkSequenceNumber": sequence_num,
                        "TotalApplicationSize": file_size,
                        "ChunkSize": Config.chunk_size
                    }
                    data = json.dumps(data)

                    result = Core.Call("/mam/apps/internal/uploadchunk", data, True)
                    if result.status_code == 200:
                        sequence_num += 1
                        transaction_id = json.loads(result.text)['TranscationId']
                    else:
                        print() # Print an extra line so we can see the previous output
                        print(result.text, file = sys.stderr)
                print() # Print en extra line once we have finished uploading
            
            return transaction_id

    def UploadBlob(filename):
        blob_id = ""
        with open(filename, "rb") as file:
            print(f"Uploading {filename} as a Blob...")
            result = Core.Call(f"/mam/blobs/uploadblob?filename={filename}&organizationGroupId=14522&moduleType=Application", file.read())
            print(result.text)
            blob_id = json.loads(result.text)['Value']

        return blob_id

    def CreateApp(filename, app_id, is_blob):
        data = JSON_DATA.GetBlob(filename, app_id) if is_blob else JSON_DATA.GetChunk(filename, app_id)
        print(f"Creating app {filename} using uploaded data with {'Blob' if is_blob else 'Chunk'} ID: {app_id}")

        return Core.Call("/mam/apps/internal/begininstall", data, True)