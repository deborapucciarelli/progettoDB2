# progettoDB2
Anno 2024/2025

**Book Review Manager – Progetto DB2**
Book Review Manager è un'applicazione web per la gestione, visualizzazione e analisi di libri, utenti e recensioni.
Il sistema si basa su un database MongoDB con Replica Set per garantire affidabilità e disponibilità, un backend in Flask per fornire API REST, e un frontend sviluppato in React.
--------------------------------------------------------------------------------------------------------------------------------------------------------------
**Tecnologie Utilizzate**
MongoDB con Replica Set (3 nodi)
Python 3.7+ con Flask
React.js (Node.js + npm)
Pymongo, pandas per la gestione e l'inserimento dei dati

--------------------------------------------------------------------------------------------------------------------------------------------------------------
**Istruzioni per l'avvio del progetto su un altro computer**
Per eseguire il progetto Book Review Manager, seguire questi semplici passaggi:

1.Clonare il repository : git clone https://github.com/deborapucciarelli/progettoDB2.git
2.Installare le dipendenze del backend : cd progettoDB2 ed eseguire pip install -r requirements.txt
3.Avviare il Replica Set : Eseguire il file start-replica.bat per avviare i tre nodi MongoDB.
4.Avviare il server Flask : python main.py
5.Avviare il frontend: Aprire un nuovo terminale: cd db2 npm install # solo al primo avvio npm start L'interfaccia sarà accessibile all'indirizzo: http://localhost:3000

----------------------------------------------------------------------------------------------------------------------------------------------------------------
**Funzionalità principali**
1. Operazioni CRUD complete per Libri, Utenti e Valutazioni
2. Operazioni Join tra le collezioni
3. Sezione Aggregazioni
4. Failover automatico in caso di guasto del nodo primario (Replica Set)

--------------------------------------------------------------------------------------------------------------------------------------------------------------

**Dataset utilizzato**
I dati provengono dal dataset pubblico disponibile su Kaggle: https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset

--------------------------------------------------------------------------------------------------------------------------------------------------------------

**Test del Replica Set**
È stato effettuato un test di resilienza simulando il fallimento del nodo primario (localhost:27017). Il sistema ha reagito correttamente: è stato eletto automaticamente un nuovo nodo primario e l'applicazione ha continuato a funzionare senza interruzioni
