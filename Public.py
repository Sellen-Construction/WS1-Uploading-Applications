# This file contains all of the important API endpoint functions meant for "Public" consumption.
# So far that is only one endpoint but that will change with time.

from API.Application import Application

class Public:
    def UploadApp(filename, type):
        is_blob = type == "blob"
        return Application.CreateApp(filename, Application.UploadBlob(filename) if is_blob else Application.UploadChunk(filename), is_blob)