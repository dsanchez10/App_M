import streamlit as st
import pandas as pd
import datetime
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

# ---- LEER CREDENCIALES DESDE SECRETS ----
cred_json = st.secrets["gcp_service_account"]
with open("credenciales_temp.json", "w") as f:
    json.dump(cred_json, f)

# ---- CONFIGURACIÓN GOOGLE SHEETS ----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_name("credenciales_temp.json", scope)
cliente = gspread.authorize(credenciales)

# 🔄 Abre la hoja correspondiente según el usuario
PIN_USUARIOS = {
    "1234": "Daniel",
    "5678": "Cinthia"
}

# --- Login con PIN ---
st.title("🔐 Acceso a Finanzas")
pin_ingresado = st.text_input("Ingrese su PIN:", type="password")

if pin_ingresado not in PIN_USUARIOS:
    st.warning("Por favor, ingrese un PIN válido.")
    st.stop()

usuario = PIN_USUARIOS[pin_ingresado]
st.success(f"Bienvenido, {usuario} 👋")

# Abre la hoja de ese usuario
try:
    hoja = cliente.open(usuario).sheet1
except Exception as e:
    st.error(f"No se pudo abrir la hoja del usuario '{usuario}': {e}")
    st.stop()

# Carga los datos
datos = hoja.get_all_records()
df = pd.DataFrame(datos)

# --- Menú principal ---
opcion = st.radio("¿Qué desea hacer?", ["Agregar ingreso", "Agregar gasto", "Ver resumen mensual", "Eliminar un registro"])
fecha_actual = datetime.date.today().strftime("%Y-%m-%d")

# --- AGREGAR INGRESO / GASTO ---
if opcion in ["Agregar ingreso", "Agregar gasto"]:
    monto = st.number_input("Monto en colones", min_value=0.0, step=100.0)
    motivo = st.text_input("Motivo del movimiento")

    if st.button("Guardar"):
        nuevo = [fecha_actual, motivo, monto if opcion == "Agregar ingreso" else "", monto if opcion == "Agregar gasto" else ""]
        hoja.append_row(nuevo)
        st.success("✅ Movimiento guardado correctamente.")

# --- RESUMEN MENSUAL ---
elif opcion == "Ver resumen mensual":
    if not df.empty:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors='coerce')
        df["Ingreso"] = pd.to_numeric(df["Ingreso"], errors='coerce')
        df["Gasto"] = pd.to_numeric(df["Gasto"], errors='coerce')

        mes_actual = datetime.date.today().month
        df_mes = df[df["Fecha"].dt.month == mes_actual]

        total_ingreso = df_mes["Ingreso"].sum()
        total_gasto = df_mes["Gasto"].sum()
        saldo = total_ingreso - total_gasto

        st.subheader("📊 Resumen mensual")
        st.write(f"**Total ingresos:** ₡{total_ingreso:,.2f}")
        st.write(f"**Total gastos:** ₡{total_gasto:,.2f}")
        st.write(f"**Saldo a favor:** ₡{saldo:,.2f}")
    else:
        st.info("Aún no hay datos registrados.")

# --- ELIMINAR REGISTRO ---
elif opcion == "Eliminar un registro":
    if df.empty:
        st.info("No hay datos registrados aún.")
    else:
        st.subheader("🗑 Eliminar un registro")
        df.index += 2  # Ajustar por encabezado + 1
        st.dataframe(df)
        fila = st.number_input("Indique el número de fila que desea eliminar (según la tabla):", min_value=2, max_value=len(df)+1)
        if st.button("Eliminar"):
            hoja.delete_rows(fila)
            st.success("✅ Registro eliminado correctamente.")

# 🔚 Eliminar el archivo temporal con las credenciales
os.remove("credenciales_temp.json")
