# App Streamlit per gestione CAP brand Carrera
# Collegata a Google Sheet

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# --- CONFIGURAZIONE GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zj53jmrEaWdOq4UR8aiNg24TrtLZrr1AUWMbuWVHPh0"

# --- AUTHENTICATION ---
# Serve file JSON delle credenziali di servizio (da caricare su Streamlit Cloud come secret)
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gcreds.json", scope)
client = gspread.authorize(creds)

sheet = client.open_by_url(SHEET_URL)
df_cap = pd.DataFrame(sheet.worksheet("cap_europa").get_all_records())
df_zone = pd.DataFrame(sheet.worksheet("zone_abilitate").get_all_records())
df_prenotazioni = pd.DataFrame(sheet.worksheet("prenotazioni").get_all_records())
df_agenti = pd.DataFrame(sheet.worksheet("agent_list").get_all_records())

# --- UI ---
st.image("Logo Brand Selection.png", width=250)
st.title("Gestione CAP - Brand Carrera")

codice = st.text_input("Inserisci il tuo codice agente")

if codice:
    if codice not in df_agenti['codice_agente'].values:
        st.error("Codice agente non valido")
        st.stop()

    agente_row = df_agenti[df_agenti['codice_agente'] == codice].iloc[0]
    st.success(f"Benvenuto {agente_row['nome']}")

    nazione = st.selectbox("Seleziona Nazione", sorted(df_cap['Nazione_ISO'].unique()))
    cap_input = st.text_input("Inserisci CAP")

    if cap_input:
        cap_match = df_cap[(df_cap['Nazione_ISO'] == nazione) & (df_cap['CAP'] == cap_input)]

        if cap_match.empty:
            st.warning("CAP non trovato")
        else:
            zona_bloccata = df_zone[(df_zone['brand_id'] == 'carrera') & (df_zone['Nazione_ISO'] == nazione)]
            if not zona_bloccata.empty:
                st.error("Zona non abilitata per questo brand")
                st.stop()

            # Check prenotazioni attive
            oggi = datetime.today()
            df_prenotazioni['scadenza'] = pd.to_datetime(df_prenotazioni['scadenza'], errors='coerce')
            df_prenotazioni = df_prenotazioni[df_prenotazioni['scadenza'] > oggi]
            prenotazioni_attive = df_prenotazioni[(df_prenotazioni['CAP'] == cap_input) & (df_prenotazioni['brand_id'] == 'carrera')]

            if not prenotazioni_attive.empty:
                st.warning("Questo CAP è già prenotato")
            else:
                st.success("CAP disponibile! Puoi prenotarlo per 7 giorni")

                if st.button("Prenota questo CAP"):
                    if len(df_prenotazioni[df_prenotazioni['codice_agente'] == codice]) >= 5:
                        st.error("Hai già 5 prenotazioni attive")
                    else:
                        nuova = {
                            "CAP": cap_input,
                            "brand_id": "carrera",
                            "codice_agente": codice,
                            "data_prenotazione": oggi.strftime("%d/%m/%Y"),
                            "scadenza": (oggi + timedelta(days=7)).strftime("%d/%m/%Y")
                        }
                        st.write("Prenotazione registrata (simulata). Salvataggio da implementare su Sheets.")
                        st.json(nuova)
else:
    st.info("Inserisci il codice agente per iniziare")
