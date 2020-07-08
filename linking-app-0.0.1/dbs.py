import os

def fetch(conn_string, name):
    return conn_string[conn_string.find(name) + len(name) + 1:conn_string.find(';', conn_string.find(name))]

def loads(dbConnectionString):
    dbDriver = '{ODBC Driver 17 for SQL Server}'
    dbServer = fetch(dbConnectionString, "Server").split(',')[0]
    dbPort = fetch(dbConnectionString, "Server").split(',')[1]
    database = fetch(dbConnectionString, "Initial Catalog")
    dbUsername = fetch(dbConnectionString, "User ID")
    dbPassword = fetch(dbConnectionString, "Password")
    dbAccessStr = 'DRIVER=' + dbDriver + ';SERVER=' + dbServer + ';PORT=' + dbPort + ';DATABASE=' + database + ';UID=' + dbUsername + ';PWD=' + dbPassword
    return dbAccessStr
