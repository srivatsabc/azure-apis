CREATE TABLE Customers (
CustomerID int IDENTITY(1,1) PRIMARY KEY,
CustomerName varchar(255),
Age int,
PhoneNumber BIGINT);

drop table Customers

INSERT INTO Customers (CustomerName,Age, PhoneNumber)
VALUES ('From DB','25','9876543210');

select * from Customers

groupid=$(az ad group create --display-name myAzureSQLDBAccessGroup --mail-nickname myAzureSQLDBAccessGroup --query objectId --output tsv)
msiobjectid=$(az webapp identity show --resource-group sqldb-RG --name mydemoapi --query principalId --output tsv)
az ad group member add --group $groupid --member-id $msiobjectid
az ad group member list -g $groupid

sqlcmd -S sqldbhost01.database.windows.net -d sqldb -G -U srivatsa@ncmithungmail.onmicrosoft.com -P "Il0v35l0n35tr33t@%100" -l 30

CREATE USER [mydemoapi] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [mydemoapi];
ALTER ROLE db_datawriter ADD MEMBER [mydemoapi];
ALTER ROLE db_ddladmin ADD MEMBER [mydemoapi];
GO