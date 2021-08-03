# This is the Main file. Execution starts here by passing the filename of the file to upload
# For example:
# python Main.py application.zip

import sys
from Public import Public

if len(sys.argv) <= 1:
    print("Please include a file name")
    quit()

result = Public.UploadApp(sys.argv[1], "chunk")
if result.status_code == 200:
    print("Uploaded and created successfully!")
else:
    print(result.text)