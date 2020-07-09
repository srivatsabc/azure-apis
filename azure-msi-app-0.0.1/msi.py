import requests
import struct
import os

msi_endpoint = os.environ["MSI_ENDPOINT"]
msi_secret = os.environ["MSI_SECRET"]

def gettoken(resource):
    print("msi_endpoint: " + msi_endpoint)
    print("msi_secret: " + msi_secret)
    token_auth_uri = msi_endpoint + "?resource=" + resource + "&api-version=2017-09-01"
    print("token_auth_uri: " + token_auth_uri)
    head_msi = {'Secret':msi_secret}
    resp = requests.get(token_auth_uri, headers=head_msi)
    access_token = resp.json()['access_token']
    print("access_token: " + access_token)
    accessToken = bytes(access_token, 'utf-8');
    exptoken = b"";
    for i in accessToken:
        exptoken += bytes({i});
        exptoken += bytes(1);
    tokenstruct = struct.pack("=i", len(exptoken)) + exptoken;
    return tokenstruct