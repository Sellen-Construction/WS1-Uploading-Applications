# This file contains the core functionality for submitting (and validating) API calls

import API.Config as Config
from API.Token import Token
import requests, json
from types import SimpleNamespace

class Core:
    def __Call(endpoint, data):
        try:
            response = ""
            Token.Validate()
            response = requests.post(Config.base_url + endpoint, headers = Config.header, data = data)
        except Exception as ex:
            print(ex)
            if "text" in response:
                print(response.text)
            response = json.loads('{"status_code": 400, "text": "validation_error"}', object_hook = lambda d: SimpleNamespace(**d))
        
        return response
    
    def Call(endpoint, data, validate = False):
        response = Core.__Call(endpoint, data)

        # If validate is passed True, keep retrying the API call until we are successful
        attempt_count = 1
        while validate and response.status_code != 200 and attempt_count <= Config.validation_limit:
            print(f"API call validation failed with status_code: {response.status_code}: {response.text}")
            print(f"Reattempting API call to {endpoint}...")
            response = Core.__Call(endpoint, data)
            attempt_count += 1

        return response