from flask import Flask, render_template
from flask import request
import jwt
import requests

app = Flask(__name__)

@app.route('/welcome')
def index():
    print ("headers : " + str(request.headers))
    access_token = str(request.headers.get('X-Ms-Token-Aad-Id-Token'))
    id = str(request.headers.get('X-Ms-Client-Principal-Id'))
    print ("access_token: " + access_token)
    claim = jwt.decode(access_token, verify=False)
    groups = claim.get('groups')
    if "1c096920-e90d-470e-8b2a-f412fab96e23" in groups:
        return render_template('index.html')
    else:
        return render_template('error.html')
    
if __name__ == "__main__":
    app.run("0.0.0.0", port=8080, debug=True)