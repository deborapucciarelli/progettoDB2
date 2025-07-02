@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM === PERCORSI E NOMI ===
SET MONGO_BIN="C:\Program Files\MongoDB\Server\8.0\bin"
SET BASE_DIR=%USERPROFILE%\mongo-replica
SET REPLSET_NAME=rs0

REM === CREA LE CARTELLE PER I DATI DI CIASCUN NODO ===
mkdir "%BASE_DIR%\%REPLSET_NAME%-node1"
mkdir "%BASE_DIR%\%REPLSET_NAME%-node2"
mkdir "%BASE_DIR%\%REPLSET_NAME%-node3"

REM === AVVIO DEI 3 NODI IN 3 PORTE DIVERSE ===
start "MongoDB Node1" %MONGO_BIN%\mongod.exe --replSet %REPLSET_NAME% --port 27017 --dbpath "%BASE_DIR%\%REPLSET_NAME%-node1" --bind_ip localhost --oplogSize 50
start "MongoDB Node2" %MONGO_BIN%\mongod.exe --replSet %REPLSET_NAME% --port 27018 --dbpath "%BASE_DIR%\%REPLSET_NAME%-node2" --bind_ip localhost --oplogSize 50
start "MongoDB Node3" %MONGO_BIN%\mongod.exe --replSet %REPLSET_NAME% --port 27019 --dbpath "%BASE_DIR%\%REPLSET_NAME%-node3" --bind_ip localhost --oplogSize 50

REM === MESSAGGIO DI ISTRUZIONE ===
echo.
echo ====================================================
echo Replica Set %REPLSET_NAME% avviato su:
echo  - localhost:27017
echo  - localhost:27018
echo  - localhost:27019
echo ====================================================
echo.
echo Ora apri un terminale con:
echo mongosh --port 27017
echo.
echo E poi esegui il seguente comando per inizializzare il Replica Set:
echo.
echo rs.initiate({
echo   _id: "%REPLSET_NAME%",
echo   members: [
echo     { _id: 0, host: "localhost:27017"},
echo     { _id: 1, host: "localhost:27018"},
echo     { _id: 2, host: "localhost:27019"}
echo   ]
echo })
echo.


pause
