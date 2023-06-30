#Generatore di "hash passwords" da utilizzare in "streamlit_authenticator"
#Output: un file psw.txt (password in chiaro), un file hashed_pw.pkl (hash passwords)

import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import psw_gen


names = ["Rosario Moscato", "Mario Mastroianni", "Elvira Floridi", "Arianna D'Urbano", "Giorgio Grappelli"]
usernames = ["rmos", "mmas", "eflo", "adur", "ggra"]

passwords = []

for name in usernames:
    passwords.append(psw_gen.psw_gen(name))

with open("psw.txt", "w") as file:
    for username, password in zip(usernames, passwords):
        file.write(f"{username}:{password}\n")

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
	pickle.dump(hashed_passwords, file)

