# Cedolib V0.0.7
# Author: Rosario Moscato
import PyPDF2
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

import re




def last_page(pdf_document):
  """
  Recupero l'ultima pagina di un PDF.
  """
  # Estraggo l'ultima pagina e la salvo in un file temporaneo  
  pdf_file = open(pdf_document, 'rb')
  read_pdf = PyPDF2.PdfReader(pdf_file)
  last_page = read_pdf.pages[-1]
  output = PyPDF2.PdfWriter()
  output.add_page(last_page)
  with open("ultima_pagina.pdf", 'wb') as out:
    output.write(out)
  input_file = "ultima_pagina.pdf"
  return input_file



def zucchetti(count_pages, numero_altro_pdf, input_file, pdf_document, outcome, final_result):
  """
  Estraggo le informazioni su Ferie e Permessi dai cedolini ZUCCHETTI 
  e le salvo (append) in una lista in output.
  """
  outcome = []
  numero_altro_pdf += 1
  #print("Documento Zucchetti\n")
  
  # Check numero pagine
  if count_pages > 1:
    input_file = last_page(pdf_document)

  codice_f = "" 
  mese = ""
  ferie_ap = ""
  ferie_maturate = ""
  ferie_godute = ""
  ferie_saldo = ""
  permessi_ap = ""
  permessi_maturati = ""
  permessi_goduti = ""
  permessi_saldo = ""
  
  
  # Estraggo Codice Fiscale
  for page_layout in extract_pages(input_file):
      for element in page_layout:
          if isinstance(element, LTTextContainer):
              tok = element.get_text()
              #Cerco il codice fiscale
              result = re.search(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]", tok)
              if result:
                codice_f = result.group(0)
                # Salvo Codice Fiscale
                outcome.append(codice_f)
                #print(result.group(0))
                break

  # Estraggo Data
  for page_layout in extract_pages(input_file):
      for element in page_layout:
          if isinstance(element, LTTextContainer):
              tok = element.get_text()
              mesi = ["Gennaio 2023" , "Febbraio 2023", "Marzo 2023", "Aprile 2023", "Maggio 2023", "Giugno 2023", "Luglio 2023", "Agosto 2023", "Settembre 2023", "Ottobre 2023", "Novembre 2023", "Dicembre 2023"]
              for mese in mesi:
                if mese in tok:
                  #print(element.get_text())
                  mese = element.get_text().replace("\n", " ")
                  # Salvo Data
                  outcome.append(mese.lower())
                  #print(f"Mese: {mese}")

  # Estraggo stato ferie e permessi
  for page_layout in extract_pages(input_file):
      for element in page_layout:
          if isinstance(element, LTTextContainer):
              tok = element.get_text()
              # CHECK RESIDUO ANNO PRECEDENTE
              if "Residuo AP" in tok:
                risultato = element.get_text().split()
                #print(f"RISULTATO:{risultato}")
                if len(risultato)<=2:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_ap = 0
                  permessi_ap = 0
                elif len(risultato) < 4:
                  #print(f"\nRisultato: {risultato}")
                  if float(risultato[2].replace(',', '.')) > 10.0:
                    ferie_ap = 0
                    permessi_ap = risultato[2]
                  else:
                    ferie_ap = risultato[2]
                    permessi_ap = 0
                else:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_ap = risultato[2]
                  permessi_ap = risultato[3]
                  #print(element.get_text().split())
              # CHECK MATURATO
              elif "Maturato" in tok:
                risultato = element.get_text().split()
                #print(f"\nLen Risultato: {len(risultato)}")
                if len(risultato)==1:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_maturate = 0
                  permessi_maturati = 0
                elif len(risultato) < 3:
                  #print(f"\nRisultato: {element.get_text()}")
                  if float(risultato[1].replace(',', '.')) > 10.0:
                    ferie_maturate = 0
                    permessi_maturati = risultato[1]
                  else:
                    ferie_maturate = risultato[1]
                    permessi_maturati = 0
                else:
                  #print(f"\nRisultato: {risultato}")
                  ferie_maturate = risultato[1]
                  permessi_maturati = risultato[2]
              # CHECK GODUTO    
              elif "Goduto" in tok:
                risultato = element.get_text().split()
                #print(f"\nLen Risultato: {len(risultato)}")
                #print(f"\nRisultato: {element.get_text()}")
                if len(risultato)==1:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_godute = 0
                  permessi_goduti = 0
                elif len(risultato) < 3:
                  #print(f"\nGoduti: {element.get_text()}")
                  if float(risultato[1].replace(',', '.')) > 10.0:
                    ferie_godute = 0
                    permessi_goduti = risultato[1]
                  else:
                    ferie_godute = risultato[1]
                    permessi_goduti = 0
                else:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_godute = risultato[1]
                  permessi_goduti = risultato[2]
              #CHECK SALDO
              elif "Saldo" in tok: 
                risultato = element.get_text().split()
                if len(risultato)==1:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_saldo = 0
                  permessi_saldo = 0
                elif len(risultato) < 3:
                  #print(f"\nRisultato: {element.get_text()}")
                  if float(risultato[1].replace(',', '.')) > 10.0:
                    ferie_saldo = 0
                    permessi_saldo = risultato[1]
                  else:
                    ferie_saldo = risultato[1]
                    permessi_saldo = 0
                else:
                  #print(f"\nRisultato: {element.get_text()}")
                  ferie_saldo = risultato[1]
                  permessi_saldo = risultato[2]

  # Aggiorno CONTEGGI
  outcome.append(ferie_ap)
  outcome.append(ferie_maturate)
  outcome.append(ferie_godute)
  outcome.append(ferie_saldo)
  outcome.append(permessi_ap)
  outcome.append(permessi_maturati)
  outcome.append(permessi_goduti)
  outcome.append(permessi_saldo)
  
  final_result.append(outcome)
  
  #print(final_result)
  #print("")

  return numero_altro_pdf, final_result  



def seac(text, numero_altro_pdf, input_file, outcome, final_result):
  """
  Estraggo le informazioni su Ferie e Permessi dai cedolini SEAC 
  e le salvo (append) in una lista in output.
  """
  ### SEAC ###
  SEAC_MONTHS = ['GENNAIO  19', 'FEBBRAIO  19', 'MARZO  19', 'APRILE  19', 'MAGGIO  19', 'GIUGNO  19', 'LUGLIO  19', 'AGOSTO  19', 'SETTEMBRE  19', 'OTTOBRE  19', 'NOVEMBRE  19', 'DICEMBRE  19', 'GENNAIO  20', 'FEBBRAIO  20', 'MARZO  20', 'APRILE  20', 'MAGGIO  20', 'GIUGNO  20', 'LUGLIO  20', 'AGOSTO  20', 'SETTEMBRE  20', 'OTTOBRE  20', 'NOVEMBRE  20', 'DICEMBRE  20', 'GENNAIO  21', 'FEBBRAIO  21', 'MARZO  21', 'APRILE  21', 'MAGGIO  21', 'GIUGNO  21', 'LUGLIO  21', 'AGOSTO  21', 'SETTEMBRE  21', 'OTTOBRE  21', 'NOVEMBRE  21', 'DICEMBRE  21', 'GENNAIO 19', 'FEBBRAIO 19', 'MARZO 19', 'APRILE 19', 'MAGGIO 19', 'GIUGNO 19', 'LUGLIO 19', 'AGOSTO 19', 'SETTEMBRE 19', 'OTTOBRE 19', 'NOVEMBRE 19', 'DICEMBRE 19', 'GENNAIO 20', 'FEBBRAIO 20', 'MARZO 20', 'APRILE 20', 'MAGGIO 20', 'GIUGNO 20', 'LUGLIO 20', 'AGOSTO 20', 'SETTEMBRE 20', 'OTTOBRE 20', 'NOVEMBRE 20', 'DICEMBRE 20', 'GENNAIO 21', 'FEBBRAIO 21', 'MARZO 21', 'APRILE 21', 'MAGGIO 21', 'GIUGNO 21', 'LUGLIO 21', 'AGOSTO 21', 'SETTEMBRE 21', 'OTTOBRE 21', 'NOVEMBRE 21', 'DICEMBRE 21']
  # Estraggo Data
  outcome = []
  for month in SEAC_MONTHS:
    if str(month) in text:
      #print("Documento SEAC\n")
      numero_altro_pdf += 1
      #print(month)

      # Estraggo Codice Fiscale
      for page_layout in extract_pages(input_file):
          for element in page_layout:
              if isinstance(element, LTTextContainer):
                  tok = element.get_text()
                  #Cerco il codice fiscale
                  result = re.search(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]", tok)
                  if result:
                    outcome.append(result.group(0))
                    #Aggiungo Data
                    mese = month.split()
                    #print(f"MESE: {mese}")
                    mese[0] = mese[0].lower()
                    mese[1] = "20"+str(mese[1])
                    mese = " ".join(mese)
                    #print(f"MESE: {mese}\n")
                    outcome.append(mese)
                    #print(result.group(0))
                    break

      # Estraggo stato ferie e permessi
      for page_layout in extract_pages(input_file):
        for element in page_layout:
          if isinstance(element, LTTextContainer):
            tok = element.get_text()
            if "          G  " in tok :
              stats = element.get_text().strip().split('\n')
              #print(stats[0].split())
              ferie = stats[0].split()
              #print(stats[1].replace("          ", "").split())
              permessi = stats[1].replace("          ", "").split()
              ferie_ap = ferie[1]
              #print("FERIE AP", ferie_ap)
              ferie_maturate = ferie[2]
              ferie_godute = ferie[3]
              ferie_saldo = ferie[4]
              permessi_ap = permessi[1]
              permessi_maturati = permessi[2]
              permessi_goduti = permessi[3]
              permessi_saldo = permessi[4]

              outcome.append(ferie_ap)
              outcome.append(ferie_maturate)
              outcome.append(ferie_godute)
              outcome.append(ferie_saldo)
              outcome.append(permessi_ap)
              outcome.append(permessi_maturati)
              outcome.append(permessi_goduti)
              outcome.append(permessi_saldo)
      
      final_result.append(outcome) 
      
      return numero_altro_pdf, final_result


def salciarini_core(input_file, page_num=0):
  """
  Estraggo le informazioni su Ferie e Permessi dai cedolini Salciarini 
  e restituisco tutto il testo contenuto nel PDF, una lista per le Ferie e una lista per i Permessi.
  """
  with open(input_file, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
  
    righe = []
    #Estraggo il testo riga per riga
    for i,line in enumerate(reader.pages[page_num].extract_text().split('\n')):
      #print(i,line)
      righe.append(line)
      
    testo = " ".join(righe)
    riferimento_riga = 0

    # Cerco la riga contenente "SALCIARINI" che vale per riferimento
    # La riga immediatamente successiva contiene le Ferie
    # 3 righe successive contengono i Permessi
    for i in range(10):
      if "SALCIARINI" in righe[-i]:
        #print(f"RIGA -{i}: {righe[-i]}")
        riferimento_riga = i

    riga_ferie = righe[-(riferimento_riga+1)][:40]
    riga_ferie = riga_ferie.split()
    riga_permessi = righe[-(riferimento_riga+3)][:40]
    riga_permessi = riga_permessi.split()
  
    return testo, riga_ferie, riga_permessi




def salciarini(text, numero_altro_pdf, input_file, outcome, final_result):
  # Open the PDF file in read binary mode
  outcome = []

  numero_altro_pdf += 1
  testo = ""
  ferie = []
  permessi = []

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

  testo, ferie, permessi = salciarini_core(input_file)
  #print("FERIE",ferie)
  #print("PERMESSI",permessi)

  if len(ferie) < 3:
    ferie_ap = 0
    ferie_maturate = 0
    ferie_godute = 0
    ferie_saldo = 0
  elif len(ferie) < 4:
    if (float(ferie[0].replace(',', '.')) +
        float(ferie[1].replace(',', '.'))) == float(ferie[2].replace(
          ',', '.')):
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
    if (float(permessi[0].replace(',', '.')) +
        float(permessi[1].replace(',', '.'))) == float(
          permessi[2].replace(',', '.')):
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
        result = re.search(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]",
                           tok)
        if result:
          #outcome.append(result.group(0))
          #print(f"Codice F.: {result.group(0)}")
          codice_f = result.group(0)
  '''
  result = re.search(r"[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]", testo)
  if result:
    #outcome.append(result.group(0))
    #print(f"Codice F.: {result.group(0)}")
    codice_f = result.group(0)
  '''


  
  # Estraggo Data
  for page_layout in extract_pages(input_file):
    #print("S1")
    for element in page_layout:
      #print("S2")
      if isinstance(element, LTTextContainer):
        #print("S3")
        tok = element.get_text()
        #print(tok)

        lista_mesi = [
          "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
          "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre",
          "Dicembre"
        ]

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

  return numero_altro_pdf, final_result
