# Multicraft Forge Installer

## Attenzione
Questo script serve solo se hai installato Multicraft su linux.
Va eseguito come utente root.

## Descrizione
Questo script Python è progettato per automatizzare il processo di installazione di Minecraft Forge su Multicraft per diverse versioni. Supporta sia versioni recenti che più datate di Minecraft.
Questo script quindi aggiunge la versione che vuoi di Forge al daemon jar directory.

## Caratteristiche
- Installazione automatica di server Forge per diverse versioni di Minecraft.
- Supporto per versioni di Minecraft Forge con universal.zip ( < 1.5.2 ) e installer.jar ( > 1.5.1 ).
- Supporto per versioni di Minecraft Forge con avvio senza file .jar ( > 1.17.1 ).
- Verifica dell'integrità dei file scaricati tramite hash MD5 e SHA1.
- Gestione automatica dei file di configurazione.
- Pulizia e rimozione di file temporanei e log di Forge dopo l'installazione.

## Requisiti
- Python 3.6 o superiore.
- Moduli Python: `requests`, `beautifulsoup4`, `logging`, `os`, `pwd`, `grp`, `tempfile`, `subprocess`, `shutil`, `glob`, `hashlib`, `packaging`.

## Installazione
1. Scarica lo script:
   - wget 'https://github.com/TheVezz/multicraft_forge_installer.git'
2. Installa Python3:
   - sudo apt install python3
3. Installa le dipendenze:
   - pip install requests beautifulsoup4 packaging

## Utilizzo
1. Esegui lo script Python:
   - python3 multicraft_forge_installer.py
2. Segui le istruzioni a schermo per selezionare la versione di Minecraft e Forge desiderata e la directory di installazione.
   - Conferma la daemon jar directory di Multicraft
   - Seleziona la versione di Minecraft
   - Seleziona la versione di Forge
