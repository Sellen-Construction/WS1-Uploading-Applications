# This file contains everything needed to get a valid API token and refresh the token when it expires

import API.Config as Config
import requests, json, time

# Open connection up to Logjam attack due to limitations of the WS1 API.
# TODO: REMOVE THE LINE BELOW WHEN THE API IS UPDATED TO REMOVE THIS VULNERABILITY!!!!
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT:!DH'

class Token:
    def Get():
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
    def Validate():
        if int(time.time()) >= int(Config.token_expiry) - 600:
            Token.Get()