import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---- CONFIGURACIÓN GOOGLE SHEETS ----
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credenciales = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
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

# Abre la hoja del usuario
try:
    hoja = cliente.open(usuario).sheet1
except Exception as e:
    st.error(f"No se pudo abrir la hoja del usuario '{usuario}': {e}")
    st.stop()

# Validar encabezados
encabezados = hoja.row_values(1)
esperados = ["Fecha", "Motivo", "Ingreso", "Gasto"]

if encabezados != esperados:
    st.error("⚠️ La hoja no tiene los encabezados correctos.\nDebe tener: Fecha | Motivo | Ingreso | Gasto")
    st.stop()

# Cargar datos
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
        df_mostrar = df.copy()
        df_mostrar.index = range(2, len(df)+2)  # Para que coincida con las filas reales en Sheets
        st.dataframe(df_mostrar)

        fila = st.number_input("Indique el número de fila que desea eliminar (según la tabla):", min_value=2, max_value=len(df)+1, step=1)
        if st.button("Eliminar"):
            hoja.delete_rows(fila)
            st.success("✅ Registro eliminado correctamente.")
