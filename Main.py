import requests, json, sys, base64, time, math
import Config
from types import SimpleNamespace

if len(sys.argv) <= 1:
    print("Please include a file name")
    quit()

# Open connection up to Logjam attack due to limitations of the WS1 API.
# TODO: REMOVE THE LINE BELOW WHEN THE API IS UPDATED TO REMOVE THIS VULNERABILITY!!!!
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

def __Call(endpoint, data):
    try:
        response = ""
        ValidateToken()
        response = requests.post(Config.base_url + endpoint, headers = Config.header, data = data)
    except Exception as ex:
        print(ex)
        if "text" in response:
            print(response.text)
        response = json.loads('{"status_code": 400, "text": "token_error"}', object_hook = lambda d: SimpleNamespace(**d))
    return response

def CallAPI(endpoint, data, validate = False):
    response = __Call(endpoint, data)

    # If validate is passed True, keep retrying the API call until we are successful
    while validate and response.status_code != 200:
        print(f"Validation failed with validate: True and status_code: {response.status_code}. Reattempting validation...")
        response = __Call(endpoint, data)

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

                result = CallAPI("/mam/apps/internal/uploadchunk", data, True)
                if result.status_code == 200:
                    current_byte += Config.chunk_size
                    sequence_num += 1
                    transaction_id = json.loads(result.text)['TranscationId']
                else:
                    print(result.text)

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

                result = CallAPI("/mam/apps/internal/uploadchunk", data, True)
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

            result = CallAPI("/mam/apps/internal/uploadchunk", data, True)
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
        "ApplicationName": sys.argv[1],
        "AutoUpdateVersion": True,
        "BlobId" if blob else "TransactionId": f"{app_id}",
        "DeviceType": "WinRT",
        "SupportedModels": {
            "Model": [
                {
                    "ModelId": 83,
                    "ModelName": "Desktop"
                }
            ]
        },
        "PushMode": "OnDemand",
        "Description": "Text value",
        "EnableProvisioning": True,
        "UploadViaLink": False,
        "LocationGroupId": 14522,
        "AppVersion": "6.0.708",
        "BuildVersion": "Text value",
        "FileName": sys.argv[1],
        "SupportedProcessorArchitecture": "x64",
        "MsiDeploymentParamModel": {
            "CommandLineArguments": "Text value",
            "InstallTimeoutInMinutes": 2,
            "RetryCount": 3,
            "RetryIntervalInMinutes": 4,
            "InstallContext": "Unknown"
        },
        "IsDependencyFile": False,
        "DeploymentOptions": {
            "WhenToInstall": {
                "DataContingencies": [],
                "DiskSpaceRequiredInKb": 1,
                "DevicePowerRequired": 2,
                "RamRequiredInMb": 3
            },
            "HowToInstall": {
                "InstallContext": "Device",
                "InstallCommand": "Text value",
                "AdminPrivileges": True,
                "DeviceRestart": "DoNotRestart",
                "RetryCount": 5,
                "RetryIntervalInMinutes": 6,
                "InstallTimeoutInMinutes": 7,
                "InstallerRebootExitCode": "1999",
                "InstallerSuccessExitCode": "0",
                "RestartDeadlineInDays": 10
            },
            "WhenToCallInstallComplete": {
                "UseAdditionalCriteria": True,
                "IdentifyApplicationBy": "DefiningCriteria",
                "CriteriaList": [
                    {
                        "CriteriaType": "FileExists",
                        "FileCriteria": {
                            "Path": "C:\\Program Files\\test\\test",
                            "VersionCondition": "Any",
                            "MajorVersion": 0,
                            "MinorVersion": 0,
                            "RevisionNumber": 0,
                            "BuildNumber": 0,
                            "ModifiedOn": "12-12-1999 12:00"
                        },
                        "LogicalCondition": "End"
                    }
                ],
                "CustomScript": {
                    "ScriptType": "Unknown",
                    "CommandToRunTheScript": "Text value",
                    "CustomScriptFileBlodId": 3,
                    "SuccessExitCode": 1
                }
            }
        },
        "FilesOptions": {
            "AppDependenciesList": [],
            "AppTransformsList": [],
            "AppPatchesList": [],
            "ApplicationUnInstallProcess": {
                "UseCustomScript": True,
                "CustomScript": {
                    "CustomScriptType": "Input",
                    "UninstallCommand": "Text value",
                    "UninstallScriptBlobId": 3
                }
            }
        },
        "CarryOverAssignments": True,
        "ApplicationSource": 0,
        "Criticality": 0,
        "CategoryList": {
            "Category": [
                {
                    "CategoryId": 1,
                    "Name": "Education"
                }
            ]
        },
        "EARAppUpdateMode": 0
    }

    data = json.dumps(data)
    print(data)

    return CallAPI("/mam/apps/internal/begininstall", data, False)


# Set run to "blob" to upload file as Blob data or "chunk" to upload in Chunks
run = "chunk"

run_blob = run == "blob"
result = CreateApp(UploadAppBlob() if run_blob else UploadAppChunks(), run_blob)
print(result.text)