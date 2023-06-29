import streamlit as st
from streamlit_lottie import st_lottie
import os
import json

import re
import csv
import datetime

import pandas as pd
import pygwalker as pyg

import cedolib as clib

# import da PyPDF2
import PyPDF2

# import da pdfminer.six
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

# PAGE CONFIGURATION
st.set_page_config(
  page_title="AFEPEC",
  page_icon="📊",
  layout="wide",
  initial_sidebar_state="expanded",
  menu_items={
    'Get Help': None,
    'Report a bug': 'mailto:r.moscato@ilivetech.it',
    'About': 'AFEPEC v0.0.6 - ROSARIOSoft - Un software MIRACOLOSO!'
      }
  )

# Hide Hamburger Menu and Footer
hide_st_style = """
              <style>
              #MainMenu {visibility: visible;}
              footer {visibility: hidden;}
              header {visibility: hidden;}
              </style>
              """

st.markdown(hide_st_style, unsafe_allow_html=True)              

versione = "0.0.6"

# Load Data
#@st.cache_data
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


# Function to delete all files in a directory
def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def main():
  st.sidebar.image('./immagini/logo')
  st.title("AFEPEC")
  st.header("Analisi FErie e PErmessi dai Cedolini")

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
      # Specifico la directory dei Cedolini
      directory = "Cedolini"
      # Get all file names in the directory
      files = os.listdir(directory)

      # Inizializzazioni
      final_result = [['Codice F.', 'Mese', 'Ferie AP', 'Ferie Maturate', 'Ferie Godute', 'Ferie Saldo', 'Permessi AP', 'Permessi Maturati', 'Permessi Goduti', 'Permessi Saldo']]
      
      SEAC_MONTHS = ['GENNAIO  19', 'FEBBRAIO  19', 'MARZO  19', 'APRILE  19', 'MAGGIO  19', 'GIUGNO  19', 'LUGLIO  19', 'AGOSTO  19', 'SETTEMBRE  19', 'OTTOBRE  19', 'NOVEMBRE  19', 'DICEMBRE  19', 'GENNAIO  20', 'FEBBRAIO  20', 'MARZO  20', 'APRILE  20', 'MAGGIO  20', 'GIUGNO  20', 'LUGLIO  20', 'AGOSTO  20', 'SETTEMBRE  20', 'OTTOBRE  20', 'NOVEMBRE  20', 'DICEMBRE  20', 'GENNAIO  21', 'FEBBRAIO  21', 'MARZO  21', 'APRILE  21', 'MAGGIO  21', 'GIUGNO  21', 'LUGLIO  21', 'AGOSTO  21', 'SETTEMBRE  21', 'OTTOBRE  21', 'NOVEMBRE  21', 'DICEMBRE  21', 'GENNAIO 19', 'FEBBRAIO 19', 'MARZO 19', 'APRILE 19', 'MAGGIO 19', 'GIUGNO 19', 'LUGLIO 19', 'AGOSTO 19', 'SETTEMBRE 19', 'OTTOBRE 19', 'NOVEMBRE 19', 'DICEMBRE 19', 'GENNAIO 20', 'FEBBRAIO 20', 'MARZO 20', 'APRILE 20', 'MAGGIO 20', 'GIUGNO 20', 'LUGLIO 20', 'AGOSTO 20', 'SETTEMBRE 20', 'OTTOBRE 20', 'NOVEMBRE 20', 'DICEMBRE 20', 'GENNAIO 21', 'FEBBRAIO 21', 'MARZO 21', 'APRILE 21', 'MAGGIO 21', 'GIUGNO 21', 'LUGLIO 21', 'AGOSTO 21', 'SETTEMBRE 21', 'OTTOBRE 21', 'NOVEMBRE 21', 'DICEMBRE 21',]
      
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
              #print("Documento Salciarini")
              # Open the PDF file in read binary mode
              #output = []
              
              numero_altro_pdf += 1
              codice_f = "" 
              mese_estratto = ""
              ferie_ap = ""
              ferie_maturate = ""
              ferie_godute = ""
              ferie_saldo = ""
              permessi_ap = ""
              permessi_maturati = ""
              permessi_goduti = ""
              permessi_saldo = ""
  
              #print(input_file)
              testo, ferie, permessi = clib.salciarini(input_file)
              #print(ferie)
              #print(permessi)
              #print(testo)
              if len(ferie) < 3:
                ferie_ap = 0
                ferie_maturate = 0
                ferie_godute = 0
                ferie_saldo = 0
              elif len(ferie) < 4:
                if (float(ferie[0].replace(',', '.')) + float(ferie[1].replace(',', '.'))) == float(ferie[2].replace(',', '.')):
                  ferie_ap = ferie[0]
                  ferie_maturate = ferie[1]
                  ferie_godute = 0
                  ferie_saldo = ferie[2]
                else:
                  ferie_ap = ferie[0]
                  ferie_maturate = 0
                  ferie_godute = ferie[1]
                  ferie_saldo = ferie[2]
              else:
                ferie_ap = ferie[0]
                ferie_maturate = ferie[1]
                ferie_godute = ferie[2]
                ferie_saldo = ferie[3]
  
              if len(permessi) < 3:
                permessi_ap = 0
                permessi_maturati = 0
                permessi_goduti = 0
                permessi_saldo = 0
              elif len(permessi) < 4:
                if (float(permessi[0].replace(',', '.')) + float(permessi[1].replace(',', '.'))) == float(permessi[2].replace(',', '.')):
                  permessi_ap = permessi[0]
                  permessi_maturati = permessi[1]
                  permessi_goduti = 0
                  permessi_saldo = permessi[2]
                else:
                  permessi_ap = permessi[0]
                  permessi_maturati = 0
                  permessi_goduti = permessi[1]
                  permessi_saldo = permessi[2]
              else:
                permessi_ap = permessi[0]
                permessi_maturati = permessi[1]
                permessi_goduti = permessi[2]
                permessi_saldo = permessi[3]
          
            
              # Estraggo Codice Fiscale
              for page_layout in extract_pages(input_file):
                for element in page_layout:
                  if isinstance(element, LTTextContainer):
                    tok = element.get_text()
                    #Cerco il codice fiscale
                    result = re.search(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]", tok)
                    if result:
                      #outcome.append(result.group(0))
                      #print(f"Codice F.: {result.group(0)}")
                      codice_f = result.group(0)
      
              # Estraggo Data
              for page_layout in extract_pages(input_file):
                #print("S1")
                for element in page_layout:
                  #print("S2")
                  if isinstance(element, LTTextContainer):
                    #print("S3")
                    tok = element.get_text()
                    #print(tok)
                
                    lista_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
      
                    rif_mese = ""
                    for mese_cedolino in lista_mesi:
                      if mese_cedolino in tok:
                        rif_mese = element.get_text()
                        #print(riferimento_mese)
                        index_mese = text.index(rif_mese)
                        #print(f"INDICE MESE: {index_mese}")
                        #print("MESE")
                        result_mese = text[index_mese:index_mese + 130]  
                        result_mese = result_mese.split()
                        result_mese = result_mese[:2]
                        mese_estratto = " ".join(result_mese)
                        mese_estratto = mese_estratto.lower()
                        #print(f"MESE ESTRATTO: {mese_estratto}")

              outcome.append(codice_f)  
              outcome.append(mese_estratto)
              outcome.append(ferie_ap)
              outcome.append(ferie_maturate)
              outcome.append(ferie_godute)
              outcome.append(ferie_saldo)
              outcome.append(permessi_ap)
              outcome.append(permessi_maturati)
              outcome.append(permessi_goduti)
              outcome.append(permessi_saldo)
          
              final_result.append(outcome)
        
            else:
              ### SEAC
              numero_altro_pdf, final_result = clib.seac(SEAC_MONTHS, text, numero_altro_pdf, input_file, outcome, final_result)
    
        
          # Gestione File PDF NON Riconosciuti
          except:
            #print(f"\n!Errore: documento: {file} NON RICONOSCIUTO\n")
            scartati.append(input_file)
            numero_scartati += 1

      with open('report_cedolini.txt', 'w') as file:
        
        ascii_art = """
                                    .-@@@@@@@@@@-@-@@@@@@@@@@-@-@@@@@,
                                  .<                                  @
                        .-@-@@@-@'  `--@@@@@@@@@@-@-@@@@@@@@@@-@-@@@@`
                       -|-
                        |
        """
        file.write(ascii_art)
        file.write("\n")
        file.write("ROSARIOSoft - Un software MIRACOLOSO!\n")
        file.write("AFEPEC - Analisi FErie e PErmessi dai Cedolini\n")
        file.write(f"Versione: {versione}\n")
        file.write("\n")
        file.write("== REPORT ESECUZIONE PROCESSO ===================================")
        current_date = datetime.date.today()
        file.write(f"\n- Data Esecuzione: {current_date}")
        file.write(f"\n- Numero totale pdf processati:{numero_processamenti}")
        file.write(f"\n- Numero cedolini gestiti: {numero_altro_pdf}")
        file.write(f"\n- Numero pdf altro tipo: {numero_processamenti-numero_altro_pdf}")
        file.write(f"\n- Numero documenti non letti: {numero_scartati}")
        if numero_scartati > 0:
           file.write("\n- Documenti scartati:")
           for item in scartati:
              file.write(f"\t{item}")
      
        file.write("\n- Output file: 'check_cedolini.csv'")
        file.write("\n== FINE REPORT ===================================================\n\n")


        report =f"""
        ==REPORT ESECUZIONE PROCESSO ===================================
        - Data Esecuzione: {current_date}
        - Numero totale pdf processati:{numero_processamenti}
        - Numero cedolini gestiti: {numero_altro_pdf}
        - Numero pdf altro tipo: {numero_processamenti-numero_altro_pdf}
        - Numero documenti non letti: {numero_scartati}
        """
        st.markdown(report, unsafe_allow_html=True)
        
        if numero_scartati > 0:
          st.write("- Documenti scartati:", str(len(scartati)))
          st.write("\t",scartati)
        st.write("- Output file: 'check_cedolini.csv'")
        st.write("== FINE REPORT ===================================================")

      with open('check_cedolini.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(final_result)

      clib.converti_date("check_cedolini.csv")
      
      print("\nEsecuzione terminata:")
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
      
      df = load_data("check_cedolini.csv")

      #config = load_config('config.json')
      pyg.walk(df, env='Streamlit', dark='light')#, spec=config)


    else:
      st.sidebar.warning("Non risultano presenti file da analizzare.")

  

      


if __name__ == "__main__":
    main()

