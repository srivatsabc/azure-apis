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
import dbs
from azure.keyvault import KeyVaultClient
from msrestazure.azure_active_directory import MSIAuthentication

app = Flask(__name__)

config = json.load(open('app.properties'))

#Overloaded returnError method for error handling
def returnError(httpErrorCode, id, api, error=None):
    print('httpErrorCode: ' + str(httpErrorCode))
    #endpoint_url = config.get(envType, envType + '.' + api + '.endpoint.url') + iata
    outputroot = config[str(httpErrorCode) + ".error.message"]
    outputroot['error']['endpoint'] = api
    if not error is None:
        outputroot['error']['message'] = error
    outputroot_json = json.dumps(outputroot)
    return outputroot_json

@app.route('/v1.0/links', methods=['POST'])
def returnAirportInfo():
    outputroot = {}
    #Validate IATA
    try:
        id = str(request.headers.get('oid'))
        tenant_id = str(request.headers.get('tenant-id'))
        if len(id) < 3:
            raise IATAException
    except IATAException:
        error = returnError(400, id)
        return Response(error, status=400, mimetype='application/json')
    else:
        #If IATA Valid - Call the first system API on SAP Hana Cloud
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

        # Construct connection string
        try:
            credentials = MSIAuthentication(resource="https://vault.azure.net")
            kvclient = KeyVaultClient(credentials)
            azure_sql_db_connectionstring = kvclient.get_secret("https://myb2capikeyvault.vault.azure.net/", "dbconnectionstring", "").value
            print(azure_sql_db_connectionstring)
            dbAccessStr = dbs.loads(azure_sql_db_connectionstring)
            print("dbAccessStr: " + dbAccessStr)
            conn = pyodbc.connect(dbAccessStr)
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
            output_json = {}
            output_json['message'] = "Hello " + name 
            output_json['upn'] = graph_response_json.get('userPrincipalName')
            return Response(json.dumps(output_json), mimetype='application/json')
        else:
            output_json = {}
            output_json['error'] = "Cannot send DB output" 
            output_json['upn'] = graph_response_json.get('userPrincipalName')
            return Response(json.dumps(output_json), status=400, mimetype='application/json')

        #Convert to JSON
        #outputroot_json = json.dumps(graph_response_json)
        #return Response(outputroot_json, mimetype='application/json')

class Error(Exception):
   """Base class for other exceptions"""
   pass

class IATAException(Error):
   """Raised when the input IATA length is greater than 3"""
   pass

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080, debug=True)