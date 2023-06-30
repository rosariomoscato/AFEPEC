# Semplice funzione per la creazione di password
# Dato un nome, lo converte in lowercase e sostituisce a ogni lettera l'equivalente numerico
# quindi: a-1, b-2, c-3, ecc...

def psw_gen(name: str):
    risultato = ""
    for char in name.lower():
        risultato += str((ord(char) - 96))
      
    return risultato