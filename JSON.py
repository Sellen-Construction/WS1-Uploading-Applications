import json

def GetBlob(filename, blob_id):
    data = {
        "ApplicationName": filename,
        "AutoUpdateVersion": True,
        "BlobId": blob_id,
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
        "EnableProvisioning": False,
        "UploadViaLink": False,
        "FileName": filename,
        "IsDependencyFile": False,
        "LocationGroupId": 14522,
        "DeploymentOptions": {
            "WhenToInstall": {
                "DataContingencies": [],
                "DiskSpaceRequiredInKb": 10,
                "DevicePowerRequired": 20,
                "RamRequiredInMb": 30
            },
            "HowToInstall": {
                "InstallContext": "Device",
                "InstallCommand": "echo test",
                "AdminPrivileges": True,
                "DeviceRestart": "DoNotRestart",
                "RetryCount": 0,
                "RetryIntervalInMinutes": 0,
                "InstallTimeoutInMinutes": 15,
                "InstallerRebootExitCode": "1641",
                "InstallerSuccessExitCode": "0"
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
            }
        },
        "FilesOptions": {
            "AppTransformsList": [],
            "AppPatchesList": [],
            "ApplicationUnInstallProcess": {
                "UseCustomScript": False,
                "CustomScript": {
                    "CustomScriptType": "Input",
                    "UninstallCommand": "msiexec /x \"test\" /passive",
                    "UninstallScriptBlobId": 0,
                    "UseCustomScript": "true"
                }
            }
        },
        "SupportedProcessorArchitecture": "x64"
    }
    return json.dumps(data)

def GetChunk(filename, transaction_id):
    data = {
        "ApplicationName": filename,
        "AutoUpdateVersion": True,
        "TransactionId": f"{transaction_id}",
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
        "FileName": filename,
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
    return json.dumps(data)