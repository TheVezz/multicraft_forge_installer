# Usato per fare richieste HTTP per scaricare file e recuperare dati dalle pagine web
import requests

# Utilizzato per l'analisi del contenuto HTML
from bs4 import BeautifulSoup

# Permette di registrare messaggi di debug, informazioni, avvertimenti ed errori
import logging

# Fornisce funzioni per interagire con il sistema operativo
import os

# Utilizzati per ottenere informazioni sugli utenti e sui gruppi del sistema operativo, necessari per cambiare il proprietario dei file e delle directory.
import pwd
import grp

# Usato per creare directory temporanee
import tempfile

# Permette di eseguire comandi esterni
import subprocess

# Fornisce funzioni di alto livello per operazioni su file e collezioni di file
import shutil

# Utilizzato per trovare tutti i percorsi che corrispondono a un pattern specifico
import glob

# Per calcolare hash MD5 e SHA1 dei file scaricati, utili per verificare l'integrità dei file
import hashlib

# Utilizzato per confrontare le versioni
from packaging import version

# Permette di lavorare con archivi ZIP
import zipfile

# Inizializza il logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cache locale per memorizzare le pagine HTML già scaricate
html_cache = {}

# Chiede all'utente di inserire la directory di installazione
def ask_install_directory(default_directory="/home/minecraft/jar/"):
    """
    Chiede all'utente di inserire la directory di installazione.
    Se non viene inserito nulla, utilizza una directory di default.
    """
    # Log che indica l'inizio del processo di richiesta della directory
    logger.debug(f"Richiesta della directory di installazione all'utente. Directory di default: '{default_directory}'")

    install_directory = input(f"Inserisci la directory del daemon jar (premere invio per usare '{default_directory}'): ") or default_directory

    # Log che mostra la directory scelta dall'utente o quella di default
    logger.info(f"Directory di installazione scelta: '{install_directory}'")

    return install_directory

# Ottiene l'HTML di una pagina web
def get_html(url):
    # Log dell'inizio del tentativo di recupero dell'HTML
    logger.debug(f"Tentativo di recupero dell'HTML per {url}")

    if url not in html_cache:
        try:
            # Esecuzione della richiesta HTTP GET
            response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            if response.status_code == 200:
                # Salvataggio dell'HTML nella cache se la richiesta ha avuto successo
                html_cache[url] = response.text
                logger.info(f"HTML recuperato con successo per {url}")
            else:
                # Log se la richiesta non è andata a buon fine
                logger.error(f"Risposta non valida per {url}: Status code {response.status_code}")
        except requests.RequestException as e:
            # Log dell'errore in caso di eccezione nella richiesta
            logger.error(f"Errore nel recupero dell'HTML per {url}: {e}")
            return None
    else:
        # Log se l'HTML è già presente nella cache
        logger.debug(f"HTML per {url} trovato nella cache")

    return html_cache.get(url, None)

# Ottiene le versioni di Forge per la versione di Minecraft specificata
def get_version_data(version_url):
    # Richiesta HTML della pagina
    html = get_html(version_url)
    logger.debug(f"Richiesta HTML per {version_url}")

    if html:
        # Analisi HTML della pagina
        soup = BeautifulSoup(html, 'html.parser')
        version_data = []
        try:
            # Estrazione dei dati delle versioni
            version_elements = soup.find_all('td', class_='download-version')
            for version_element in version_elements:
                version_text = version_element.get_text(strip=True)
                version_data.append(version_text)
                logger.debug(f"Versione trovata: {version_text}")

            logger.info(f"Versioni estratte con successo da {version_url}")
            return version_data
        except Exception as e:
            # Log dell'errore in caso di eccezione
            logger.error(f"Errore durante l'estrazione delle versioni da {version_url}: {e}")
            return []
    else:
        # Log in caso di mancato recupero del contenuto HTML
        logger.error(f"Impossibile recuperare il contenuto HTML da {version_url}")
        return []

# Ottiene il link dell'installer per la versione di Forge specificata
def get_installer_link(game_version, forge_version):
    installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-installer.jar"
    try:
        # Richiesta HEAD per verificare il link
        response = requests.head(installer_url)
        logger.debug(f"Richiesta HEAD inviata a {installer_url}")

        # Log della risposta
        logger.debug(f"Risposta per il link Installer: {response.status_code}")

        # Controllo dello status code della risposta
        if response.status_code == 200:
            logger.info(f"Link Installer trovato: {installer_url}")
            return installer_url
        else:
            logger.warning(f"Link Installer non trovato o non raggiungibile: Status Code {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Errore nella verifica del link Installer: {e}")
        return None

# Ottiene il link dell'universal per la versione di Forge specificata
def get_universal_link(game_version, forge_version):
    universal_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-universal.zip"
    try:
        # Richiesta HEAD per verificare il link
        response = requests.head(universal_url)
        logger.debug(f"Richiesta HEAD inviata a {universal_url}")

        # Log della risposta
        logger.debug(f"Risposta per il link Universal: {response.status_code}")

        # Controllo dello status code della risposta
        if response.status_code == 200:
            logger.info(f"Link Universal trovato: {universal_url}")
            return universal_url
        else:
            logger.warning(f"Link Universal non trovato o non raggiungibile: Status Code {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Errore nella verifica del link Universal: {e}")
        return None

# Ottiene il link del server vanilla per la versione di Minecraft specificata
def get_vanilla_link(game_version):
    vanilla_url = f"http://www.multicraft.org/download/jar/?file=minecraft&version={game_version}&client=multicraft"
    try:
        # Richiesta HEAD per verificare il link
        response = requests.head(vanilla_url, allow_redirects=True)
        logger.debug(f"Richiesta HEAD inviata a {vanilla_url}")
        
        # Log della risposta
        logger.debug(f"Risposta per il link Vanilla: {response.status_code}, URL: {response.url}")
        
        # Se lo status code è 200 o 302 (redirect), restituisce l'URL effettivo
        if response.status_code in [200, 302]:
            logger.info(f"Link Vanilla trovato: {response.url}")
            return response.url
        else:
            logger.warning(f"Link Vanilla non trovato o non raggiungibile: Status Code {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Errore nella verifica del link Vanilla: {e}")
        return None

# Scarica un file dall'URL specificato e lo salva in una directory temporanea
def download_to_temp_folder(download_url, filename):
    """
    Scarica un file dall'URL specificato e lo salva in una directory temporanea con un nome specifico.
    Ritorna il percorso del file scaricato.
    """
    # Crea una directory temporanea con un nome specifico
    temp_dir_name = "multicraft-forge-installer"
    system_temp_dir = tempfile.gettempdir()
    temp_dir = os.path.join(system_temp_dir, temp_dir_name)

    logger.debug(f"Preparazione per il download nella directory temporanea: {temp_dir}")

    # Crea la directory se non esiste
    if not os.path.exists(temp_dir):
        try:
            os.makedirs(temp_dir)
            logger.info(f"Creata directory temporanea: {temp_dir}")
        except Exception as e:
            logger.error(f"Errore nella creazione della directory temporanea {temp_dir}: {e}")
            return None

    file_path = os.path.join(temp_dir, filename)

    try:
        response = requests.get(download_url)
        response.raise_for_status()
        logger.debug(f"Inizio download del file da {download_url}")

        with open(file_path, 'wb') as file:
            file.write(response.content)

        logger.info(f"Download completato: {file_path}")
        return file_path
    except requests.RequestException as e:
        logger.error(f"Errore nel download del file da {download_url}: {e}")
        return None

# Scarica un file dall'URL specificato e lo salva nella directory target specificata
def download_to_target_folder(download_url, filename, install_directory, game_version, forge_version):
    """
    Scarica un file dall'URL specificato e lo salva nella directory target specificata.
    Ritorna il percorso del file scaricato.
    """
    # Costruisci il percorso della directory target
    target_directory = os.path.join(install_directory, f"forge-{game_version}-{forge_version}")
    
    logger.debug(f"Preparazione download in: {target_directory}")

    # Verifica e crea la directory target se non esiste
    if not os.path.exists(target_directory):
        try:
            os.makedirs(target_directory)
            logger.info(f"Creata directory target: {target_directory}")
        except Exception as e:
            logger.error(f"Errore nella creazione della directory target {target_directory}: {e}")
            return None

    # Percorso completo dove il file sarà salvato
    file_path = os.path.join(target_directory, filename)

    try:
        response = requests.get(download_url)
        response.raise_for_status()

        with open(file_path, 'wb') as file:
            file.write(response.content)

        logger.info(f"Download completato: {file_path}")
        return file_path
    except requests.RequestException as e:
        logger.error(f"Errore nel download del file da {download_url}: {e}")
        return None

# Calcola l'hash di un file
def calculate_file_hash(file_path, hash_type):
    """
    Calcola l'hash di un file.
    :param file_path: Percorso del file da esaminare.
    :param hash_type: Tipo di hash, 'md5' o 'sha1'.
    :return: Valore hash del file.
    """
    try:
        hash_obj = hashlib.new(hash_type)
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_obj.update(chunk)

        hash_value = hash_obj.hexdigest()
        logger.info(f"Calcolato hash {hash_type} per il file {file_path}: {hash_value}")
        return hash_value
    except Exception as e:
        logger.error(f"Errore nel calcolo dell'hash {hash_type} del file {file_path}: {e}")
        return None

# Estrae gli hash MD5 e SHA1 dal contenuto HTML della pagina di download
def extract_hashes(html_content, installer_url):
    logger.debug(f"Inizio estrazione degli hash da {installer_url}")
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        if installer_url in link['href']:
            info_div = link.find_next_sibling("div", class_="info-tooltip")
            if info_div:
                md5 = sha1 = None
                for line in info_div.get_text().split("\n"):
                    if "MD5:" in line:
                        md5 = line.split("MD5:")[1].strip()
                    elif "SHA1:" in line:
                        sha1 = line.split("SHA1:")[1].strip()
                if md5 and sha1:
                    logger.info(f"Estratti hash MD5: {md5} e SHA1: {sha1} per {installer_url}")
                else:
                    logger.warning(f"Non sono stati trovati hash MD5 o SHA1 validi per {installer_url}")
                return md5, sha1
            else:
                logger.warning(f"Nessun div di informazioni trovato accanto al link per {installer_url}")
    logger.error(f"Hash MD5 e SHA1 non trovati per {installer_url}")
    return None, None

# Verifica che gli hash MD5 e SHA1 del file corrispondano ai valori attesi
def verify_file_hash(file_path, expected_md5, expected_sha1):
    """
    Verifica che gli hash MD5 e SHA1 del file corrispondano ai valori attesi.
    """
    try:
        md5_hash = calculate_file_hash(file_path, "md5")
        sha1_hash = calculate_file_hash(file_path, "sha1")

        if md5_hash == expected_md5 and sha1_hash == expected_sha1:
            logger.info(f"Verifica hash per {file_path} riuscita: MD5 e SHA1 corrispondono.")
            return True
        else:
            logger.warning(f"Verifica hash fallita per {file_path}: MD5 o SHA1 non corrispondono. Attesi: MD5={expected_md5}, SHA1={expected_sha1}, Ottenuti: MD5={md5_hash}, SHA1={sha1_hash}")
            return False
    except Exception as e:
        logger.error(f"Errore nella verifica degli hash del file {file_path}: {e}")
        return False

# Crea una directory se non esiste già
def create_directory_if_not_exists(directory):
    """
    Crea una directory se non esiste già.
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Creata directory: {directory}")
        else:
            logger.debug(f"La directory {directory} esiste già.")
    except OSError as e:
        logger.error(f"Errore nella creazione della directory {directory}: {e}")

# Estrae il contenuto di forge-universal.zip e lo copia in server.jar
def copy_contents_to_jar(zip_path, jar_path, exclude_dir="META-INF"):
    logger.debug(f"Inizio dell'estrazione e della copia del contenuto di {zip_path} in {jar_path}")

    # Estrai il contenuto di forge-universal.zip
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("temp_universal")
            logger.info(f"Contenuto di {zip_path} estratto in una directory temporanea")
    except zipfile.BadZipFile as e:
        logger.error(f"Errore nell'apertura di {zip_path} come archivio ZIP: {e}")
        return

    # Apri server.jar come archivio ZIP
    try:
        with zipfile.ZipFile(jar_path, 'a') as jar_zip:
            # Percorri i file nella directory temporanea
            for foldername, subfolders, filenames in os.walk("temp_universal"):
                for filename in filenames:
                    # Assicurati di non includere i file nella cartella esclusa
                    if exclude_dir not in foldername:
                        file_path = os.path.join(foldername, filename)
                        jar_zip.write(file_path, os.path.relpath(file_path, "temp_universal"))
                        logger.debug(f"File {file_path} aggiunto a {jar_path}")
            logger.info(f"Contenuto di {zip_path} copiato con successo in {jar_path}")
    except zipfile.BadZipFile as e:
        logger.error(f"Errore nell'apertura di {jar_path} come archivio ZIP: {e}")
        return

    # Pulisci eliminando la directory temporanea
    try:
        shutil.rmtree("temp_universal")
        logger.debug("Directory temporanea 'temp_universal' rimossa")
    except OSError as e:
        logger.error(f"Errore nella rimozione della directory temporanea 'temp_universal': {e}")

# Esegue l'installazione del server con il file jar specificato
def execute_java_installation(jar_file_path, game_version, forge_version, install_directory):
    """
    Esegue l'installazione del server Java con il file jar specificato.
    """
    original_directory = os.getcwd()
    specific_dir = f"forge-{game_version}-{forge_version}"
    target_directory = os.path.join(install_directory, specific_dir)
    logger.debug(f"Creazione della directory per l'installazione: {target_directory}")
    create_directory_if_not_exists(target_directory)

    install_command = f"--installServer={target_directory}"

    try:
        if version.parse(game_version) >= version.parse("1.5.2"):
            logger.info(f"Esecuzione dell'installazione per la versione {game_version}")
            subprocess.run(["java", "-jar", jar_file_path, install_command], check=True)
            logger.info("Installazione completata con successo per versioni superiori alla 1.5.2")

            if version.parse(game_version) >= version.parse("1.17.1"):
                files_to_remove = ["README.txt", "run.sh", "run.bat", "user_jvm_args.txt"]
                remove_files(target_directory, files_to_remove)
                logger.debug("File non necessari rimossi")

                libraries_directory = os.path.join(target_directory, "libraries")
                find_and_copy_file(libraries_directory, target_directory, "unix_args.txt")
                modify_unix_args_file(game_version, forge_version, install_directory)
        
            logger.debug("Pulizia della cartella temporanea e dei log in corso")
            remove_temp_directory("multicraft-forge-installer")
            remove_log_files(os.getcwd())

        elif version.parse(game_version) < version.parse("1.5.2"):
            logger.info(f"Esecuzione dell'installazione per la versione {game_version}")
            # Cambia la directory di lavoro alla target_directory prima di eseguire il comando Java
            os.chdir(target_directory)
            subprocess.run(["java", "-jar", jar_file_path], check=True)
            # Ripristina la directory di lavoro originale dopo l'esecuzione
            os.chdir(original_directory)
            logger.info("Installazione completata con successo per versioni inferiori alla 1.5.2")
            files_to_remove = ["eula.txt", "server.properties"]
            remove_files(target_directory, files_to_remove, ["logs"])

        config_url = "http://www.multicraft.org/download/conf/?file=craftbukkit.jar.conf"
        config_filename = f"forge-{game_version}-{forge_version}.jar.conf"
        download_and_modify_config(config_url, config_filename, game_version, forge_version, install_directory)

        user, group = get_directory_owner(install_directory)
        config_file_path = os.path.join(install_directory, config_filename)
        change_owner_recursively(target_directory, user, group, additional_files=[config_file_path])
        logger.debug("Proprietario di directory e file di configurazione aggiornato")

    except subprocess.CalledProcessError as e:
        logger.error(f"Errore nell'esecuzione dell'installazione: {e}")

# Rimuove i file specificati da una directory
def remove_files(directory, file_list, folder_list=None):
    """
    Rimuove file e cartelle specificati da una directory.
    """
    logger.debug(f"Inizio della rimozione di file e cartelle in: {directory}")

    # Rimuovi i file
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                logger.info(f"File rimosso: {file_path}")
            except OSError as e:
                logger.error(f"Errore nella rimozione del file {file_path}: {e}")

    # Rimuovi le cartelle, se specificate
    if folder_list:
        for folder_name in folder_list:
            folder_path = os.path.join(directory, folder_name)
            if os.path.isdir(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    logger.info(f"Cartella rimossa: {folder_path}")
                except OSError as e:
                    logger.error(f"Errore nella rimozione della cartella {folder_path}: {e}")

    logger.debug("Rimozione di file e cartelle completata")

# Cerca un file nel source_directory e nelle sue sottodirectory e lo copia nel target_directory
def find_and_copy_file(source_directory, target_directory, filename):
    """
    Cerca un file nel source_directory e nelle sue sottodirectory.
    Se trovato, copia il file nel target_directory.
    """
    logger.debug(f"Ricerca del file '{filename}' in: {source_directory}")

    file_found = False
    for root, dirs, files in os.walk(source_directory):
        if filename in files:
            file_path = os.path.join(root, filename)
            try:
                shutil.copy(file_path, target_directory)
                logger.info(f"File '{filename}' copiato da {file_path} a {target_directory}")
                file_found = True
                break  # Interrompe il ciclo dopo aver trovato e copiato il file
            except OSError as e:
                logger.error(f"Errore nella copia del file {file_path} a {target_directory}: {e}")
                break

    if not file_found:
        logger.warning(f"File '{filename}' non trovato in {source_directory}")

# Modifica il file unix_args.txt
def modify_unix_args_file(game_version, forge_version, install_directory):
    """
    Modifica il file unix_args.txt sostituendo 'libraries' con il percorso delle 'libraries' nella directory di Forge.
    """
    specific_dir = f"forge-{game_version}-{forge_version}"
    target_directory = os.path.join(install_directory, specific_dir)
    file_path = os.path.join(target_directory, "unix_args.txt")

    logger.debug(f"Modifica del file unix_args.txt in: {file_path}")

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            logger.debug("File unix_args.txt letto con successo")

        new_content = content.replace('libraries', f'{target_directory}/libraries')
        logger.debug("Contenuto del file modificato per includere il percorso corretto delle libraries")

        with open(file_path, 'w') as file:
            file.write(new_content)
            logger.info("File unix_args.txt modificato e salvato con successo")

    except OSError as e:
        logger.error(f"Errore nella modifica del file {file_path}: {e}")

# Ottiene l'utente proprietario e il gruppo di una directory
def get_directory_owner(directory):
    """
    Ottiene l'utente proprietario della directory.
    """
    logger.debug(f"Ottieni il proprietario della directory: {directory}")
    try:
        stat_info = os.stat(directory)
        uid = stat_info.st_uid
        gid = stat_info.st_gid

        user = pwd.getpwuid(uid).pw_name
        group = grp.getgrgid(gid).gr_name

        logger.info(f"Proprietario della directory {directory}: utente {user}, gruppo {group}")
        return user, group
    except Exception as e:
        logger.error(f"Errore nell'ottenere il proprietario della directory {directory}: {e}")
        return None, None

# Cambio del proprietario di una directory e del suo contenuto ricorsivamente
def change_owner_recursively(directory, user, group, additional_files=None):
    """
    Cambia il proprietario di una directory e del suo contenuto ricorsivamente.
    Cambia anche il proprietario di eventuali file aggiuntivi specificati nella lista additional_files.
    """
    logger.debug(f"Inizio del cambio di proprietario per la directory: {directory}")
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        os.chown(directory, uid, gid)
        logger.info(f"Proprietario cambiato per la directory: {directory}")

        for root, dirs, files in os.walk(directory):
            for dir in dirs:
                os.chown(os.path.join(root, dir), uid, gid)
            for file in files:
                os.chown(os.path.join(root, file), uid, gid)

        logger.debug("Proprietario cambiato per tutti i file e le sottocartelle.")

        if additional_files:
            for file_path in additional_files:
                if os.path.exists(file_path):
                    os.chown(file_path, uid, gid)
                    logger.info(f"Proprietario cambiato per il file aggiuntivo: {file_path}")

        logger.info(f"Proprietario cambiato con successo per {directory} e il suo contenuto.")
    except OSError as e:
        logger.error(f"Errore nel cambiare il proprietario per {directory}: {e}")

    logger.debug("Fine del cambio di proprietario")

# Funzione per trovare il file .jar di forge nella sua directory del daemon jar
def find_forge_jar(install_directory, game_version, forge_version):
    """
    Trova il file .jar di Forge che contiene 'forge' nel nome, nella directory specificata.
    """
    pattern = f"{install_directory}/forge-{game_version}-{forge_version}/*forge*.jar"
    logger.debug(f"Cercando file jar di Forge con pattern: {pattern}")  # Aggiunto log per il debug
    
    jar_files = glob.glob(pattern)
    logger.debug(f"File jar trovati: {jar_files}")  # Log dei file trovati

    if jar_files:
        logger.info(f"File jar di Forge trovato: {jar_files[0]}")  # Log del file selezionato
        return jar_files[0]  # Restituisce il primo file trovato che corrisponde al pattern
    else:
        logger.error("File jar di Forge non trovato.")  # Log in caso di errore
        return None

# Scarica e modifica il file di configurazione
def download_and_modify_config(config_url, config_filename, game_version, forge_version, install_directory):
    """
    Scarica e modifica il file di configurazione.
    """
    logger.debug("Inizio della funzione download_and_modify_config")
    config_path = os.path.join(install_directory.rstrip("/"), config_filename)
    logger.debug(f"Percorso del file di configurazione: {config_path}")
    category_value = f"[Forge] {game_version}"

    command_value = ""
    # Comando per le versioni tra 1.5.2 e 1.17.1
    if version.parse("1.5.2") <= version.parse(game_version) < version.parse("1.17.1"):
        forge_jar_path = find_forge_jar(install_directory, game_version, forge_version)
        if forge_jar_path is None:
            logger.error("File jar di Forge non trovato.")
            return False
        forge_jar_file = os.path.basename(forge_jar_path)
        command_value = f'"{{JAVA}}" -Xmx{{MAX_MEMORY}}M -Xms{{START_MEMORY}}M -Djline.terminal=jline.UnsupportedTerminal -jar "{{JAR_DIR}}/forge-{game_version}-{forge_version}/{forge_jar_file}" nogui'
    # Comando per le versioni senza file .jar, uguali o superiori alla 1.17.1
    elif version.parse(game_version) >= version.parse("1.17.1"):
        command_value = f'"{{JAVA}}" -Xmx{{MAX_MEMORY}}M -Xms{{START_MEMORY}}M -Djline.terminal=jline.UnsupportedTerminal "@{{JAR_DIR}}/forge-{game_version}-{forge_version}/unix_args.txt"'
    # Comando per le versioni inferiori alla 1.5.2
    else:
        command_value = f'"{{JAVA}}" -Xmx{{MAX_MEMORY}}M -Xms{{START_MEMORY}}M -Djline.terminal=jline.UnsupportedTerminal -jar "{{JAR_DIR}}/forge-{game_version}-{forge_version}/server.jar" nogui'

    try:
        logger.debug(f"Tentativo di scaricare il file di configurazione da: {config_url}")
        response = requests.get(config_url)
        response.raise_for_status()
        logger.info("File di configurazione scaricato con successo.")

        content = response.text.splitlines()
        modified_content = []
        for line in content:
            if line.startswith("name ="):
                modified_content.append(f"name = {forge_version}")
            elif line.startswith("category ="):
                modified_content.append(f"category = {category_value}")
            elif line.startswith("command ="):
                modified_content.append(f"command = {command_value}")
            elif line.startswith("source =") or line.startswith("configSource ="):
                modified_content.append(line.split('=')[0] + "= ")
            else:
                modified_content.append(line)

        with open(config_path, 'w') as file:
            file.write("\n".join(modified_content))
        logger.info(f"File di configurazione modificato e salvato in: {config_path}")

    except requests.RequestException as e:
        logger.error(f"Errore durante il download del file di configurazione: {e}")
        return False
    except Exception as e:
        logger.error(f"Errore generico durante la modifica del file di configurazione: {e}")
        return False

    logger.debug("Fine della funzione download_and_modify_config")
    return True

# Rimuove la directory temporanea specificata e tutto il suo contenuto
def remove_temp_directory(temp_dir_name):
    """
    Rimuove la directory temporanea specificata e tutto il suo contenuto.
    """
    logger.debug("Inizio della procedura di rimozione della directory temporanea")
    system_temp_dir = tempfile.gettempdir()
    temp_dir = os.path.join(system_temp_dir, temp_dir_name)

    logger.debug(f"Directory temporanea da rimuovere: {temp_dir}")
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.info(f"Directory temporanea rimossa: {temp_dir}")
        except OSError as e:
            logger.error(f"Errore nella rimozione della directory temporanea {temp_dir}: {e}")
    else:
        logger.warning(f"La directory temporanea {temp_dir} non esiste.")

    logger.debug("Fine della procedura di rimozione della directory temporanea")

# Rimuove tutti i file .log nella directory specificata
def remove_log_files(directory):
    """
    Rimuove tutti i file .log nella directory specificata.
    """
    logger.debug(f"Cercando file .log in: {directory}")
    log_files = glob.glob(os.path.join(directory, "*.log"))

    if not log_files:
        logger.info("Nessun file .log trovato per la rimozione.")
        return

    for file in log_files:
        try:
            os.remove(file)
            logger.info(f"File log rimosso: {file}")
        except OSError as e:
            logger.error(f"Errore nella rimozione del file log {file}: {e}")

# Stampa il sottomenu per la selezione della versione di Forge e poi procede con l'installazione
def print_submenu(selected_version_links, game_version, install_directory):
    logger.debug("Inizio della funzione print_submenu")
    
    while True:
        forge_versions = []
        for version_url in selected_version_links:
            logger.info(f"Recupero versioni di Forge da: {version_url}")
            versions = get_version_data(version_url)
            logger.debug(f"Versioni trovate: {versions}")
            forge_versions.extend(versions)

        for i, forge_version in enumerate(forge_versions, start=1):
            print(f"{i}. {forge_version}")

        print("0. Torna al menu principale")
        choice = input("Inserisci il numero dell'opzione desiderata: ")

        if choice == "0":
            logger.debug("Uscita dalla funzione print_submenu - Torna al menu principale")
            return True

        if choice.isdigit() and 1 <= int(choice) <= len(forge_versions):
            selected_forge_version = forge_versions[int(choice) - 1]
            logger.info(f"Versione di Forge selezionata: {selected_forge_version}")

            if version.parse(game_version) >= version.parse("1.5.2"):
                installer_link = get_installer_link(game_version, selected_forge_version)
                logger.debug(f"Link Installer: {installer_link}")

                if installer_link:
                    print(f"\nHai scelto la versione di Forge: {selected_forge_version}")
                    print(f"Link Installer: {installer_link}\n")

                    filename = f"forge-{game_version}-{selected_forge_version}-installer.jar"
                    downloaded_file_path = download_to_temp_folder(installer_link, filename)

                    if downloaded_file_path:
                        print(f"Installer scaricato con successo in: {downloaded_file_path}")
                        execute_java_installation(downloaded_file_path, game_version, selected_forge_version, install_directory)
                    else:
                        logger.error("Non è stato possibile scaricare l'installer.")
                    return False
                else:
                    logger.error(f"Link Installer non trovato per {selected_forge_version}")

            elif version.parse(game_version) < version.parse("1.5.2"):
                universal_link = get_universal_link(game_version, selected_forge_version)
                vanilla_link = get_vanilla_link(game_version)
                logger.debug(f"Link Universal: {universal_link}, Link Vanilla: {vanilla_link}")

                if universal_link and vanilla_link:
                    print(f"\nHai scelto la versione di Forge: {selected_forge_version}")
                    print(f"Link Universal: {universal_link}\n")

                    universal_filename = f"forge-{game_version}-{selected_forge_version}-universal.zip"
                    downloaded_universal_path = download_to_temp_folder(universal_link, universal_filename)
                    vanilla_filename = "server.jar"
                    downloaded_vanilla_path = download_to_target_folder(vanilla_link, vanilla_filename, install_directory, game_version, selected_forge_version)

                    if downloaded_universal_path and downloaded_vanilla_path:
                        print(f"Universal e server vanilla scaricati con successo.")
                        copy_contents_to_jar(downloaded_universal_path, downloaded_vanilla_path)
                        execute_java_installation(downloaded_vanilla_path, game_version, selected_forge_version, install_directory)
                        logger.info("Installazione completata con successo.")
                    else:
                        logger.error("Non è stato possibile scaricare l'installer o il server vanilla.")
                    return False
                else:
                    logger.error(f"Link Universal o Vanilla non trovato per {selected_forge_version}")

        else:
            logger.warning("Scelta non valida nella funzione print_submenu")
            print("Scelta non valida. Riprova.")

    logger.debug("Fine della funzione print_submenu")

# Stampa il menu principale
def print_menu(base_url):
    logger.debug(f"Caricamento del menu dalla URL: {base_url}")
    html = get_html(base_url)

    if html:
        soup = BeautifulSoup(html, 'html.parser')
        version_elements_li = soup.select('.li-version-list li')
        sub_versions = []
        for element in version_elements_li:
            version_text = element.a.text.strip() if element.a else element.text.strip()
            sub_versions.append(version_text)
            logger.debug(f"Trovata versione: {version_text}")

        sub_versions_links = [f"{base_url}index_{version}.html" for version in sub_versions]
        sub_versions.append("ALL")
        logger.info("Versioni e link disponibili caricati con successo")

        for index, version in enumerate(sub_versions, start=1):
            print(f"{index}. {version}")

        print("0. Esci")
        choice = input("Inserisci il numero dell'opzione desiderata: ")

        if choice == "0":
            logger.debug("Scelta di uscire dal menu")
            return None
        elif choice.isdigit() and 1 <= int(choice) <= len(sub_versions):
            selected_version = sub_versions[int(choice) - 1]
            logger.info(f"Versione selezionata: {selected_version}")

            if selected_version != "ALL":
                selected_version_links = [link for link in sub_versions_links if f"index_{selected_version}" in link]
                logger.debug(f"Link selezionati per la versione {selected_version}: {selected_version_links}")
                return selected_version_links, selected_version
        else:
            logger.warning("Scelta non valida nel menu")
            print("Scelta non valida. Riprova.")

        return None
    else:
        logger.error("Errore nel caricare la pagina principale.")
        return None

# Funzione principale
def main():
    logger.debug("Inizio esecuzione del programma")
    base_url = "https://files.minecraftforge.net/net/minecraftforge/forge/"
    install_directory = ask_install_directory()
    logger.info(f"Directory di installazione scelta: {install_directory}")

    while True:
        logger.debug("Visualizzazione del menu principale")
        menu_result = print_menu(base_url)

        if menu_result:
            selected_version_links, selected_version = menu_result
            logger.debug(f"Versione selezionata: {selected_version}, Link: {selected_version_links}")
            
            if print_submenu(selected_version_links, selected_version, install_directory):
                logger.debug("Tornando al menu principale")
                continue  # Torna al menu principale
            else:
                logger.debug("Terminazione del programma dopo print_submenu")
                break  # Termina il programma
        else:
            logger.debug("Uscita dal menu principale, terminazione del programma")
            break  # Termina il programma se l'utente sceglie di uscire dal menu principale

    logger.debug("Programma terminato")

if __name__ == "__main__":
    main()
