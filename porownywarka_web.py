import streamlit as st
import pandas as pd
import re
import io
import tempfile

def compare_headers(txt_file, excel_file):
    try:
        txt_headers = set()
        
        # Zapisz pliki do katalogu tymczasowego
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_txt:
            temp_txt.write(txt_file.getvalue())
            temp_txt_path = temp_txt.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_xlsx:
            temp_xlsx.write(excel_file.getvalue())
            temp_xlsx_path = temp_xlsx.name

        # Odczytaj plik tekstowy
        with open(temp_txt_path, "r", encoding="utf-8") as file:
            for line in file:
                matches = re.findall(r"\b\d{9}\b", line)
                txt_headers.update(matches)

        # Odczytaj plik Excel
        df_excel = pd.read_excel(temp_xlsx_path, sheet_name=1)

        if len(df_excel.columns) > 2:
            excel_headers = set(df_excel.iloc[:, 2].dropna().astype(str).str.strip())
        else:
            excel_headers = set()

        # Znajdź różnice
        missing_in_excel = sorted(txt_headers - excel_headers)
        missing_in_txt = sorted(excel_headers - txt_headers)

        diff_df = pd.DataFrame({
            "Missing in Excel": missing_in_excel + ["" for _ in range(len(missing_in_txt) - len(missing_in_excel))],
            "Missing in Text File": missing_in_txt + ["" for _ in range(len(missing_in_excel) - len(missing_in_txt))]
        })

        return diff_df
    except Exception as e:
        st.error(f"❌ Wystąpił błąd w compare_headers: {e}")
        return pd.DataFrame()

# Tworzenie interfejsu w Streamlit
st.title("📊 Porównywarka nagłówków")

st.write("Wybierz pliki do porównania:")

txt_file = st.file_uploader("📂 Wybierz plik TXT", type=["txt"])
excel_file = st.file_uploader("📂 Wybierz plik Excel", type=["xlsx"])

if txt_file and excel_file:
    try:
        result = compare_headers(txt_file, excel_file)
        
        st.write("🔍 **Wynik porównania:**")
        st.dataframe(result)

        # Pobranie pliku wynikowego
        result_io = io.BytesIO()
        with pd.ExcelWriter(result_io, engine='xlsxwriter') as writer:
            result.to_excel(writer, index=False)
        result_io.seek(0)

        st.download_button("📥 Pobierz plik wynikowy", result_io, "differences.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error(f"❌ Wystąpił błąd w interfejsie Streamlit: {e}")
