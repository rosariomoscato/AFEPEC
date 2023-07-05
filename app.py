# Import pacchetti
import streamlit as st
import streamlit_authenticator as stauth #pip install streamlit_authenticator==0.1.5
from streamlit_lottie import st_lottie

import os
import json
import pickle
from pathlib import Path
import csv
import datetime
import time

import pandas as pd
import pygwalker as pyg

import cedolib as clib

# import PyPDF2
import PyPDF2

# import pdfminer.six
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

versione = "0.0.7"


# Configurazione PAGINA
st.set_page_config(
  page_title="AFEPEC",
  page_icon="📊",
  layout="wide",
  initial_sidebar_state="expanded",
  menu_items={
    'Get Help': None,
    'Report a bug': 'mailto:r.moscato@ilivetech.it',
    'About': f'AFEPEC v{versione} - ROSARIOSoft - Un software MIRACOLOSO!'
      }
  )

# Nascondo Hamburger Menu e Footer
hide_st_style = """
              <style>
              #MainMenu {visibility: visible;}
              footer {visibility: hidden;}
              header {visibility: hidden;}
              </style>
              """

st.markdown(hide_st_style, unsafe_allow_html=True)              

# Load Data
def load_data(url):
  df = pd.read_csv(url)
  return df


# Display PyGWalker
def load_config(file_path):
  with open(file_path, 'r') as config_file:
    config_str = config_file.read()
  return config_str


# Loading Lottie Files
def load_lottiefile(filepath: str):
  with open(filepath, "r") as f:
    return json.load(f)
    

def get_files(path):
  files = []
  for file in os.listdir(path):
      if os.path.isfile(os.path.join(path, file)):
          files.append(file)
  return files

def remove_files(path, files):
  for file in files:
      os.remove(os.path.join(path, file))


def download_file(file_path="check_cedolini.csv"):
	with open(file_path, 'rb') as file:
		file_data = file.read()
	st.sidebar.download_button('Download Risultati', file_data, file_name="check_cedolini.csv", mime="text/csv")


# Funzione che cancella tutti i file di una directory
def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# INIZIO MAIN (Parte di FRONT-END)
def main():
  st.sidebar.image('./immagini/logo')
  authenticator.logout("Logout", "sidebar")
  st.sidebar.subheader(f"Buongiorno {name}")


  st.title("AFEPEC")
  st.header("Analizzatore FErie e PErmessi dai Cedolini")

  folder_path = "./Cedolini"

  if not os.path.exists("Cedolini"):
    os.makedirs("Cedolini")


  menu_principale = st.sidebar.selectbox("Selezionare una voce", ["Home", "Gestione File", "Elaborazione", "Download", "Analisi"])

  if menu_principale == "Home":
    # Menu Gestione File
    lottie_hr = load_lottiefile("./immagini/human-resources-approval-animation.json")
    st_lottie(
      lottie_hr,
      reverse=False,
      loop=True,
      quality="medium",
      height=640,
      width=800,
      key="hello")


  elif menu_principale == "Gestione File":
    # Menu Gestione File
    st.subheader("Gestione File")
    spiega_file = """
    In questa sezione è possibile:
    <ul>
      <li>Importare i file da elaborare successivamente</li>
      <li>Cancellare uno alla volta i file che non interessano più</li>
      <li>Cancellare in una volta tutti i file importati precedentemente</li>
    </ul>
    """
    st.markdown(spiega_file, unsafe_allow_html=True)
    selected_option = st.sidebar.selectbox("", ("Upload", "Eliminazione"))
    
    if selected_option == "Upload":
      
      files = st.sidebar.file_uploader("Selezionare i files da importare", type = ['pdf'], accept_multiple_files=True)
      if files is not None:
        for file in files:
          with open(os.path.join(folder_path, file.name), "wb") as f:
            f.write(file.getbuffer())
        
    elif selected_option == "Eliminazione":
      
      files = get_files(folder_path)
      if files is not None:
        tipo_canc = st.sidebar.radio("Selezionare il tipo di eliminazione:", ("Tutti i File", "File Singoli"))
        if tipo_canc=="Tutti i File":
          if st.sidebar.button("Cancella TUTTO"):
            delete_files_in_directory('./Cedolini')
            st.sidebar.success("Eliminazione completata")
        else:  
          selected_files = st.sidebar.multiselect("Selezionare i files da eliminare singolarmente:", files)
          if st.sidebar.button("Eliminazione file selezionato/i"):
            remove_files(folder_path, selected_files)
            st.sidebar.success("Eliminazione completata")
            files = get_files(folder_path)


  elif menu_principale == "Elaborazione":
    presenza_file = get_files(folder_path)
    st.subheader("Elaborazione Cedolini")
    spiega_elaborazione = """
    In questa sezione è possibile esegure la ricerca di **ferie** e **permessi** all'interno dei **cedolini** importati in precedenza.
    Il risultato di tale operazione sarà un file *csv* (da aprire con excel) scaricabile selezionando la voce **Download** del menu.
    Per una sua rapida analisi selezionare, invece, la voce **Analisi**.
    """
    st.markdown(spiega_elaborazione, unsafe_allow_html=True)

    if len(presenza_file)==0:
      st.sidebar.warning("Importare dei file da gestire")
    else:
      start_time = time.time()
      # Specifico la directory dei Cedolini
      directory = "Cedolini"
      # Get all file names in the directory
      files = os.listdir(directory)

      # Inizializzazioni
      final_result = [['Codice F.', 'Mese', 'Ferie AP', 'Ferie Maturate', 'Ferie Godute', 'Ferie Saldo', 'Permessi AP', 'Permessi Maturati', 'Permessi Goduti', 'Permessi Saldo']]
      
      scartati = []
      
      count_pages = 0
      numero_processamenti = 0
      numero_scartati = 0 
      numero_altro_pdf = 0 #In realtà è il numero di pdf che sono cedolini

      print("Elaborazione in corso...")
      # Cerco in tutti i files della directory
      for file in files:
        if file.endswith(".pdf"):
      
          input_file = os.path.join(directory, file)
          #st.write(input_file)
          pdf_document = input_file
      
          # Conto il numero di  pagine
          with open(pdf_document, "rb") as file:
            pdf_file = PyPDF2.PdfReader(file)
            count_pages = len(pdf_file.pages)
            #st.write(count_pages)
            #print(f"Documento: {input_file} - Numero di pagine:{count_pages}")
  
          #Estraggo gli elementi da ogni documento incluso nella directory
          text = ""
          for page_layout in extract_pages(input_file):
            for element in page_layout:
              if isinstance(element, LTTextContainer):
                text += element.get_text()
                #Stampa tutto il contenuto
                #print(text)
                #Stampa tutti gli elementi individuati
                #print(element)

          outcome = []
      
          try:
            numero_processamenti += 1
            
            ### ZUCCHETTI ###
            if "Zucchetti" in text:
              #st.write(count_pages, numero_altro_pdf, input_file, pdf_document, outcome, final_result)
              numero_altro_pdf, final_result =  clib.zucchetti(count_pages, numero_altro_pdf, input_file, pdf_document, outcome, final_result)
              #st.write(numero_altro_pdf)
    
            ### SALCIARINI
            elif "SALCIARINI" in text:
              numero_altro_pdf, final_result = clib.salciarini(text, numero_altro_pdf, input_file, outcome, final_result)
        
            ### SEAC
            else:
              numero_altro_pdf, final_result = clib.seac(text, numero_altro_pdf, input_file, outcome, final_result)
    
        
          # Gestione File PDF NON Riconosciuti
          except:
            #print(f"\n!Errore: documento: {file} NON RICONOSCIUTO\n")
            scartati.append(input_file)
            numero_scartati += 1


      # Creazione REPORT
      current_date = datetime.date.today()
      end_time = time.time()
      execution_time = end_time - start_time
      report =f"""
      ==REPORT ESECUZIONE PROCESSO ===================================
      - Data Esecuzione: {current_date}
      - Tempo Esecuzione: circa {round(execution_time)} secondi
      - Numero totale pdf processati:{numero_processamenti}
      - Numero cedolini gestiti: {numero_altro_pdf}
      - Numero pdf altro tipo: {numero_processamenti-numero_altro_pdf}
      - Numero documenti non letti: {numero_scartati}
      """
      st.markdown(report, unsafe_allow_html=True)
      
      if numero_scartati > 0:
        st.write("- Documenti scartati:", str(len(scartati)))
        st.write("\t",scartati)



      # Scrittura file di OUTPUT
      with open('check_cedolini.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(final_result)

      # Gestione DATE e formattazione file OUTPUT
      esito_conversione = "" 			    
      try:		    
      	esito_conversione = clib.converti_date("check_cedolini.csv")
      except:	      
        esito_conversione = "Negativo"
	      
      st.write(f"- Conversione Formato: {esito_conversione}")
      st.write("- Output file: 'check_cedolini.csv'")
      st.write("== FINE REPORT ===================================================")
      
      print("\nEsecuzione terminata:")
      print(f"- Esito Conversione: {esito_conversione}")
      print("- Output file: check_cedolini.csv")
      print("- Report file: report_cedolini.txt\n")
      


  elif menu_principale == "Download":
    st.subheader("Download File")
    st.markdown("Cliccare sul bottone laterale per scaricare il file **csv** con i risultati dell'elaborazione.")
    if os.path.isfile("check_cedolini.csv"):
      download_file()
      #data = pd.read_csv("./check_cedolini.csv", encoding='utf-8', sep=";")
      #st.title("Data Editor")
      #edited_data = st.data_editor(data)
      #st.table(data)
    else:
      st.sidebar.warning("Non risultano presenti file da scaricare.")

  #elif menu_principale == "Analisi":
  else:
    st.subheader("Analisi dei Risultati")
    if os.path.isfile("check_cedolini.csv"):
      try:	    
        df = load_data("check_cedolini.csv")
        #config = load_config('config.json')
        pyg.walk(df, env='Streamlit', dark='light')#, spec=config)
      except:
        st.warning("Problemi con la visualizzazione del file di output. Si consiglia di scaricarlo e analizzarlo con un foglio di calcolo.")      
    else:
      st.sidebar.warning("Non risultano presenti file da analizzare.")

  


# --- USER AUTHENTICATION ---
names = ["Rosario Moscato", "Mario Mastroianni", "Elvira Floridi", "Arianna D'Urbano", "Giorgio Grappelli"]
usernames = ["rmos", "mmas", "eflo", "adur", "ggra"]

# Load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
  hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "afepec_webapp", "abcdef", cookie_expiry_days = 30)

name, authentication_status, username = authenticator.login("AFEPEC - Login", "main")

if authentication_status == False:
  st.error("Username e/o Password non corretti")

if authentication_status == None:
  st.warning("Inserire Username e Password")

if authentication_status:

      
  if __name__ == "__main__":
      main()

