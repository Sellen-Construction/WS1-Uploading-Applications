import sys
import API

if len(sys.argv) <= 1:
    print("Please include a file name")
    quit()

api = API.Public()
result = api.UploadApp(sys.argv[1], "chunk")
print(result.text)