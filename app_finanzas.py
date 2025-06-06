import streamlit as st
import pandas as pd
import datetime
import os

# --- PROTECCIÓN POR PIN ---
PIN_CORRECTO = "1234"
st.title("🔐 Acceso")
pin_ingresado = st.text_input("Ingrese su PIN:", type="password")

if pin_ingresado != PIN_CORRECTO:
    st.warning("Por favor, ingrese el PIN correcto para acceder.")
    st.stop()
# ----------------------------

# Ruta del archivo en entorno Streamlit Cloud
archivo_csv = "Finanzas.csv"  # No uses ruta local aquí

# Cargar archivo si existe
if os.path.exists(archivo_csv):
    df = pd.read_csv(archivo_csv, sep=';')
    df.columns = df.columns.str.lower()  # asegurar nombres consistentes
else:
    df = pd.DataFrame(columns=["fecha", "motivo", "ingreso", "gasto"])

# Fecha actual
hoy = datetime.date.today()
fecha_actual = hoy.strftime("%Y-%m-%d")

# Título
st.title("💰 Control")

# Menú principal
opcion = st.radio("¿Qué desea hacer?", ["Agregar ingreso", "Agregar gasto", "Ver resumen mensual", "Eliminar un registro"])

# AGREGAR INGRESO / GASTO
if opcion in ["Agregar ingreso", "Agregar gasto"]:
    monto = st.number_input("Monto en colones", min_value=0.0, step=100.0)
    motivo = st.text_input("Motivo del movimiento")
    
    if st.button("Guardar"):
        nueva_fila = {
            "fecha": f"{fecha_actual}",
            "motivo": motivo,
            "ingreso": monto if opcion == "Agregar ingreso" else "",
            "gasto": monto if opcion == "Agregar gasto" else ""
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df.to_csv(archivo_csv, index=False, sep=';')
        st.success("✅ Dato guardado correctamente.")

# RESUMEN MENSUAL
elif opcion == "Ver resumen mensual":
    st.subheader("📊 Resumen mensual")

    df["fecha"] = df["fecha"].astype(str).str.replace("'", "")
    df["fecha"] = pd.to_datetime(df["fecha"], errors='coerce')
    df["ingreso"] = pd.to_numeric(df["ingreso"], errors='coerce')
    df["gasto"] = pd.to_numeric(df["gasto"], errors='coerce')

    df_mes = df[(df["fecha"].dt.month == hoy.month) & (df["fecha"].dt.year == hoy.year)]

    total_ingresos = df_mes["ingreso"].sum()
    total_gastos = df_mes["gasto"].sum()
    saldo = total_ingresos - total_gastos

    st.write(f"**Total ingresos:** ₡{total_ingresos:,.2f}")
    st.write(f"**Total gastos:** ₡{total_gastos:,.2f}")
    st.write(f"**Saldo a favor:** ₡{saldo:,.2f}")

# ELIMINAR UN REGISTRO
elif opcion == "Eliminar un registro":
    st.subheader("🗑 Eliminar un registro")

    if df.empty:
        st.info("No hay datos registrados aún.")
    else:
        df_preview = df.copy()
        df_preview.index.name = "N°"
        st.dataframe(df_preview)

        fila = st.number_input("Ingrese el número de fila que desea eliminar:", min_value=0, max_value=len(df)-1, step=1)

        if st.button("Eliminar registro"):
            df = df.drop(index=fila).reset_index(drop=True)
            df.to_csv(archivo_csv, index=False, sep=';')
            st.success("✅ Registro eliminado correctamente.")
