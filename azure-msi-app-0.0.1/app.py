from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from objdict import ObjDict
import requests
import logging
import json
import msal
import pyodbc
import msi

app = Flask(__name__)
config = json.load(open('app.properties'))

#Overloaded returnError method for error handling
def returnError(httpErrorCode, id, api, error=None):
    print('httpErrorCode: ' + str(httpErrorCode))
    outputroot = config[str(httpErrorCode) + ".error.message"]
    outputroot['error']['endpoint'] = api
    if not error is None:
        outputroot['error']['message'] = error
    outputroot_json = json.dumps(outputroot)
    return outputroot_json

@app.route('/v1.0/account-links', methods=['GET'])
def returnAirportError():
    try:
        raise LinkException
    except LinkException:
        error = returnError(400, "<NULL>", "/api/v1/links")
        return Response(error, status=400, mimetype='application/json')

@app.route('/v1.0/account-links/<string:id>', methods=['GET'])
def returnVendorAssociationsInfo(id):
    outputroot = {}
    #Validate id
    try:
        if len(id) < 3:
            raise LinkException
    except LinkException:
        error = returnError(400, id)
        return Response(error, status=400, mimetype='application/json')
    else:
        #If Valid WID - Call the Graph Api
        print ("headers : " + str(request.headers))
        try:
            oauth = msal.ConfidentialClientApplication(
                    config["client_id"], 
                    authority=config["authority"],
                    client_credential=config["secret"],
                )
            result = None
            result = oauth.acquire_token_silent(config["scope"], account=None)
            if not result:
                logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
                result = oauth.acquire_token_for_client(scopes=config["scope"])

            if "access_token" in result:
                # Calling graph using the access token
                api_url = config["graph.api.url"]
                api = api_url.replace ("{id}", id)
                print('graph_api_url : ' + api)
                graph_response = requests.get(api, headers={'Authorization': 'Bearer ' + result['access_token']},)
                graph_response_json = json.loads(graph_response.text)
                print("Graph API call result: " + str(graph_response_json))
        #Handle exceptions
        except requests.exceptions.HTTPError as error:
            error = returnError(504, id, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.ConnectionError as error:
            error = returnError(504, id, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.Timeout as error:
            error = returnError(504, id, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except requests.exceptions.RequestException as error:
            error = returnError(504, id, api, str(error))
            return Response(error, status=504, mimetype='application/json')
        except:
            #Generic Error Handler
            error = returnError(graph_response.status_code, id, api)
            return Response(error, status=graph_response.status_code, mimetype='application/json')

        # Get Associations from DB 
        try:
            # Connect to Azure SQL DB using MSI
            token = msi.gettoken(config["resource"])
            print("token: " + str(token))
            #conn = pyodbc.connect(dbAccessStr)
            conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=sqldbhost01.database.windows.net,1433;Database=sqldb", attrs_before = { 1256:bytearray(token) });
            print("Connection established")
        except pyodbc.ProgrammingError as err:
            print(err)
            error = returnError(503, id, api, str(err))
            return Response(error, status=503, mimetype='application/json')
        except pyodbc.Error as err:
            print(err)
            error = returnError(503, id, api, str(err))
            return Response(error, status=503, mimetype='application/json')
        else:
            # Upon successful connection
            cursor = conn.cursor()
            cursor.execute("select * from Customers")
            row = cursor.fetchone()
            name = None
            while row:
                print (str(row[0]) + " " + str(row[1]))
                name = str(row[1])
                row = cursor.fetchone()

            print("Finally!")
            conn.commit()
            cursor.close()
            conn.close()
            print("Done.")

        # Send response
        if name:
            return Response(f"Hello {name}!", mimetype='application/json')
        else:
            return Response(f"Cannot send DB output", status=400, mimetype='application/json')

        #Convert to JSON
        #outputroot_json = json.dumps(graph_response_json)
        #return Response(outputroot_json, mimetype='application/json')

class Error(Exception):
   """Base class for other exceptions"""
   pass

class LinkException(Error):
   """Raised when the input id length is greater than 3"""
   pass

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080, debug=True)
