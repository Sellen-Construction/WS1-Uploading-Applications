import sys
import API

if len(sys.argv) <= 1:
    print("Please include a file name")
    quit()

api = API.Public()
result = api.UploadApp(sys.argv[1], "chunk")
if result.status_code == 200:
    print("Uploaded and created successfully!")
else:
    print(result.text)