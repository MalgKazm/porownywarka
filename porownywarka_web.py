import streamlit as st
import pandas as pd
import re

def compare_headers(txt_file, excel_file):
    txt_headers = set()
    
    # Wczytaj plik tekstowy i znajdź 9-cyfrowe liczby
    for line in txt_file.getvalue().decode("utf-8").splitlines():
        matches = re.findall(r"\b\d{9}\b", line)
        txt_headers.update(matches)

    # Wczytaj plik Excel
    xls = pd.ExcelFile(excel_file)
    df_excel = pd.read_excel(xls, sheet_name=xls.sheet_names[1])

    if len(df_excel.columns) > 2:
        excel_headers = set(df_excel.iloc[:, 2].dropna().astype(str).str.strip())
    else:
        excel_headers = set()

    # Znajdź różnice
    missing_in_excel = sorted(txt_headers - excel_headers)
    missing_in_txt = sorted(excel_headers - txt_headers)

    diff_df = pd.DataFrame({
        "Missing in Excel": missing_in_excel + [""] * (max(len(missing_in_txt), len(missing_in_excel)) - len(missing_in_excel)),
        "Missing in Text File": missing_in_txt + [""] * (max(len(missing_in_txt), len(missing_in_excel)) - len(missing_in_txt))
    })

    return diff_df

# Tworzenie interfejsu w Streamlit
st.title("📊 Porównywarka nagłówków")

st.write("Wybierz pliki do porównania:")

txt_file = st.file_uploader("📂 Wybierz plik TXT", type=["txt"])
excel_file = st.file_uploader("📂 Wybierz plik Excel", type=["xlsx"])

if txt_file and excel_file:
    result = compare_headers(txt_file, excel_file)
    
    st.write("🔍 **Wynik porównania:**")
    st.dataframe(result)

    # Pobranie pliku wynikowego
    result.to_excel("differences_web.xlsx", index=False)
    with open("differences_web.xlsx", "rb") as file:
        st.download_button("📥 Pobierz plik wynikowy", file, "differences.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
