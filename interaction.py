import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit_extras.metric_cards
import seaborn as sns
# from google.colab import drive, files
# drive.mount('/content/drive')
st.set_page_config(page_title="Auditores Data", page_icon=":bar_chart:", layout="wide")

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
            .block-container {
            padding-top: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* Opcional: reducir padding general */
        .main {
            padding-top: 0px !important;
        }
        .custom-div {
        border: 2px solid #4CAF50; /* Color del borde */
        border-radius: 10px; /* Bordes redondeados */
        padding: 10px;
        margin-bottom: 2px;
        background-color: #f9f9f9; /* Color de fondo opcional */
    }
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

def traducir_mes(mes):
  traduccion = {
      "January":"Enero",
      "February":"Febrero",
      "March":"Marzo",
      "April":"Abril",
      "May":"Mayo",
      "June":"Junio",
      "July":"Julio",
      "August":"Agosto",
      "September":"Septiembre",
      "October":"Octubre",
      "November":"Noviembre",
      "December":"Diciembre"
  }
  return traduccion[mes]

def convertir_horas_a_minutos(horas):
    horas_enteras = int(horas)
    minutos = round((horas - horas_enteras) * 60)
    return f"{horas_enteras}h {minutos}m"

def semana_del_mes(fecha):
    dia_del_mes = fecha.day

    if 1 <= dia_del_mes <= 7:
        return 1
    elif 8 <= dia_del_mes <= 15:
        return 2
    elif 16 <= dia_del_mes <= 23:
        return 3
    elif 24 <= dia_del_mes <= 31:
        return 4


def clean_actividad_revisores(actividad_revisores):
    actividad_revisores = actividad_revisores.rename(columns = {"Cliente":"Municipio"})
    actividad_revisores["Municipio"] = actividad_revisores["Municipio"].str.capitalize()
    actividad_revisores["Tipo de Cámara"] = actividad_revisores["Tipo de Cámara"].replace({"Luces Bajas":"Luces", "Semáforo Rojo":"Semáforo"})
    actividad_revisores["Auditor"] = actividad_revisores["Auditor"].map(lambda x: ' '.join(x.split())).map(lambda x:str(x).title())
    actividad_revisores["Auditor"] = actividad_revisores["Auditor"].replace("Mayra Yanel Chamorro", "Yanina Denise Ybarra")
    actividad_revisores["Código de cámara"] = actividad_revisores["Código de cámara"].map(lambda x:(x.split("-")[-1]).strip())
    actividad_revisores["Fecha"] = pd.to_datetime(actividad_revisores["Fecha"])
    actividad_revisores = actividad_revisores.sort_values(by="Fecha")
    actividad_revisores_listo = actividad_revisores.drop(columns = ["Tipo de Revisión","% aceptadas","Recorte","Deshacer","NoOp"])
    actividad_revisores_listo["Mes"] = actividad_revisores_listo["Fecha"].dt.month_name().map(traducir_mes)
    actividad_revisores_listo['Aceptadas'] = pd.to_numeric(actividad_revisores_listo['Aceptadas'], errors='coerce')
    actividad_revisores_listo['Rechazadas'] = pd.to_numeric(actividad_revisores_listo['Rechazadas'], errors='coerce')
    actividad_revisores_listo['Semana'] = actividad_revisores_listo['Fecha'].map(semana_del_mes)

    return actividad_revisores_listo

def clean_horas_revisores(horas_de_revisores):
    horas_de_revisores = horas_de_revisores.rename(columns={"Cliente": "Municipio"})
    horas_de_revisores["Municipio"] = horas_de_revisores["Municipio"].str.capitalize()
    horas_de_revisores["Tipo de Cámara"] = horas_de_revisores["Tipo de Cámara"].replace(
        {"Luces Bajas": "Luces", "Semáforo Rojo": "Semáforo"})
    horas_de_revisores["Auditor"] = horas_de_revisores["Auditor"].map(lambda x: ' '.join(x.split())).map(
        lambda x: str(x).title())
    horas_de_revisores['Total (en horas)'] = pd.to_numeric(horas_de_revisores['Total (en horas)'], errors='coerce')
    horas_de_revisores["Total (en horas)"] = horas_de_revisores[
                                                 "Total (en horas)"] / 100  # Esto lo hago porque se ve que cuando se carga el excel lo pasa a entero y se pierde el tiempo real
    horas_de_revisores["Mes"] = pd.to_datetime(horas_de_revisores["Fecha"]).dt.month_name().map(traducir_mes)
    horas_de_revisores = horas_de_revisores.drop(columns=["Tipo de Revisión", "Nivel de Revisión"])
    return horas_de_revisores

@st.cache_data
def get_data_from_csv():
    actividad_auditores = pd.read_excel("Files/01-Actividad de revisores.xlsx")
    actividad_auditores = clean_actividad_revisores(actividad_auditores)
    return actividad_auditores

@st.cache_data
def get_data_horas_csv():
    horas_auditores = pd.read_excel("Files/03-Tiempo de revisión.xlsx")
    horas_auditores = clean_horas_revisores(horas_auditores)

    return horas_auditores


def bar_horizontal(dataframe):
    if (len(auditor) != 1):
        actividad_general = dataframe.groupby(
            ["Auditor", "Tipo de Cámara"]).agg({"Aceptadas": ["sum"], "Rechazadas": ["sum"]}).unstack().reset_index()
        actividad_general.columns = ["Auditor", "Luces Aceptadas", "Semáforos Aceptados", "Luces Rechazadas",
                                     "Semáforos Rechazados"]
        melted = actividad_general.melt(id_vars="Auditor", var_name="Tipo", value_name="Valor")
        fig = px.bar(melted.sort_values(by="Valor"), y="Auditor", x="Valor", text_auto=".2s", color="Tipo",
                     color_discrete_sequence=paleta_colores)
        fig.update_traces(textfont_size=18, textposition="inside", marker=dict(line=dict(color='black', width=.5)))
        fig.update_layout(legend_title="Presuncion", legend_y=0.9)
        st.plotly_chart(fig, use_container_width=True)
    else:
        actividad_general = dataframe.groupby(
            ["Fecha", "Tipo de Cámara"]).agg({"Total":["sum"]}).unstack().reset_index()
        actividad_general.columns = ["Fecha", "Luces", "Semáforos"]
        melted = actividad_general.melt(id_vars="Fecha", var_name="Tipo", value_name="Valor")
        fig = px.bar(melted.sort_values(by="Valor"), x="Fecha", y="Valor", text_auto=".2s", color="Tipo",
                     color_discrete_sequence=paleta_colores, barmode="group")
        fig.update_traces(textfont_size=18, textposition="inside", marker=dict(line=dict(color='black', width=.5)))
        fig.update_layout(legend_title="Presuncion", legend_y=0.9)
        st.plotly_chart(fig, use_container_width=True)

def bar_vertical(dataframe, periodo):
    actividad_municipios = dataframe.groupby([f"{periodo}", "Municipio"]).agg({"Total": "sum"}).reset_index()
    actividad_municipios.columns = ["Semana", "Municipio", "Imágenes Captadas"]
    fig = px.bar(actividad_municipios, x="Semana", y="Imágenes Captadas", color="Municipio", barmode="group",text_auto=".2s",
                 color_discrete_sequence=paleta_colores)
    fig.update_traces(textfont_size=18, textposition="inside", marker=dict(line=dict(color='black', width=.5)))
    fig.update_layout(legend_title="Municipio", legend_y=0.9)
    st.plotly_chart(fig, use_container_width=True)

actividad_auditores = get_data_from_csv()
horas_auditores = get_data_horas_csv()

# --- SIDEBAR ----
#st.header("Filtra acá:")

with st.expander("🔍 Filtros", expanded=False):
    mes = st.multiselect("Selecciona el mes:", actividad_auditores["Mes"].unique(),default=actividad_auditores["Mes"].unique()[-1])
    data_filtrada_por_mes = actividad_auditores.query("Mes == @mes") if mes else actividad_auditores
    auditor = st.multiselect("Selecciona el auditor:", actividad_auditores["Auditor"].unique())
    fecha = st.multiselect("Selecciona la fecha:", data_filtrada_por_mes["Fecha"].unique())
    colores_disponibles = {
        "Pastel": px.colors.qualitative.Pastel,
        "Estandar": px.colors.qualitative.Set1,
        "G10": px.colors.qualitative.G10,
        "Antiguo": px.colors.qualitative.Antique,
        "Vívido": px.colors.qualitative.Vivid,
        "Prisma": px.colors.qualitative.Prism,
        "Notorio": px.colors.qualitative.Light24,
    }

    tema_seleccionado = st.selectbox('Selecciona una paleta de colores', list(colores_disponibles.keys()))
    paleta_colores = colores_disponibles[tema_seleccionado]
# # Filtro de Mes
data_filtrada_por_mes = actividad_auditores.query("Mes == @mes") if mes else actividad_auditores
horas_filtradas_por_mes = horas_auditores.query("Mes == @mes") if mes else actividad_auditores


# Filtrar por Auditor y Mes
data_filtrada_por_auditor = data_filtrada_por_mes.query("Auditor == @auditor") if auditor else data_filtrada_por_mes
horas_filtrada_por_auditor = horas_filtradas_por_mes.query("Auditor == @auditor") if auditor else horas_filtradas_por_mes


# Filtrado con mes, auditor y fecha
df_seleccionado = data_filtrada_por_auditor.query("Fecha == @fecha") if fecha else data_filtrada_por_auditor
df_seleccionado_horas = horas_filtrada_por_auditor.query("Fecha == @fecha") if fecha else horas_filtrada_por_auditor


if mes and auditor and fecha:
    infracciones_auditor = df_seleccionado["Total"].sum()
    horas_auditor = df_seleccionado_horas["Total (en horas)"].sum()
elif mes and auditor:
    infracciones_auditor = data_filtrada_por_auditor["Total"].sum()
    horas_auditor = horas_filtrada_por_auditor["Total (en horas)"].sum()

else:
    infracciones_auditor = 0
    horas_auditor = 0

def metrics(auditor, fecha):
    from streamlit_extras.metric_cards import style_metric_cards
    left, middle, right, border = st.columns(4)
    left.metric(f"Imágenes desde {(actividad_auditores.Fecha.min())}", value=int(actividad_auditores.Total.sum()))
    middle.metric("Total auditado del Mes", value=int(data_filtrada_por_mes.Total.sum()))
    right.metric("Presunciones de auditores elegidos", value=int(infracciones_auditor))
    border.metric("Horas trabajadas de auditores elegidos", value = convertir_horas_a_minutos(horas_auditor))
    style_metric_cards(background_color="#f9f9f9", border_left_color="black")
    div1, div2 = st.columns([6, 7])
    if len(auditor) > 1:
        with div2:
            comparative_dataset = data_filtrada_por_auditor.groupby(["Auditor","Fecha"]).agg({"Total": ["sum"]}).reset_index()
            comparative_dataset.columns = ["Auditor","Fecha" ,"Total"]
            comparative_dataset_horas = horas_filtrada_por_auditor.groupby(["Auditor","Fecha"]).agg({"Total (en horas)": ["sum"]}).reset_index()
            comparative_dataset_horas.columns = ["Auditor","Fecha","Total"]
            for auditor in df_seleccionado.Auditor.unique():
                    if len(fecha) > 0:
                        st.markdown(f'<div class="custom-div">{auditor.title()}<br>Presunciones Captadas: {int(df_seleccionado.loc[(df_seleccionado["Auditor"] == auditor) & (df_seleccionado["Fecha"].isin(fecha))].Total.sum())}<br>Horas Trabajadas: '
                                    f'{convertir_horas_a_minutos(
                            df_seleccionado_horas.loc[(df_seleccionado_horas["Auditor"] == auditor) & (df_seleccionado_horas["Fecha"].isin(fecha))]["Total (en horas)"].sum())}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="custom-div">{auditor.title()}<br>Presunciones Captadas: {int(comparative_dataset.loc[comparative_dataset["Auditor"] == auditor].Total.sum())}<br>Horas Trabajadas: '
                                    f'{convertir_horas_a_minutos(comparative_dataset_horas.loc[comparative_dataset_horas["Auditor"] == auditor].Total.sum())}</div>', unsafe_allow_html=True)

    with div1:
        thme_plotly = None
        df_pie= df_seleccionado.copy()
        df_pie = df_pie.rename(columns={"Total": "Presunciones Captadas"})
        fig = px.pie(df_pie, values="Presunciones Captadas", names="Auditor", color_discrete_sequence=paleta_colores)
        fig.update_layout(legend_title="Auditores", legend_y=0.9)
        fig.update_traces(textinfo=None, textposition="inside", marker=dict(line=dict(color='black', width=.6)))
        st.plotly_chart(fig, use_container_width=True, theme=thme_plotly)
    bar_horizontal(df_seleccionado)
    div1, div2 = st.columns(2)

    with div1:
        if len(fecha) < 1:
            bar_vertical(df_seleccionado, "Semana")
            tabla_semanal = df_seleccionado.groupby(["Semana", "Auditor", "Municipio"]).agg({"Total": ["sum"]}
                                                                                            ).unstack(
            ).reset_index().fillna(0)
            tabla_semanal.columns = ["Semana", "Auditor", "Berisso", "Ezeiza", "Lanus"]
        else:
            bar_vertical(df_seleccionado, "Fecha")
            tabla_semanal = df_seleccionado.groupby(["Fecha", "Auditor", "Municipio"]).agg({"Total": ["sum"]}
                                                                                            ).unstack(
            ).reset_index().fillna(0)
            tabla_semanal.columns = ["Fecha", "Auditor", "Berisso", "Ezeiza", "Lanus"]
    with div2:
        st.dataframe(tabla_semanal)
metrics(auditor, fecha)
#st.dataframe(df_seleccionado)
#st.dataframe(df_seleccionado_horas)
# #Filtrar por Mes y Municipio
# municipio = st.sidebar.multiselect("Selecciona el municipio: ", options=actividad_auditores["Municipio"].unique())
# dataframe_solo_municipio = actividad_auditores.query("Municipio == @municipio")
# data_filtrada_por_municipio = data_filtrada_por_mes.query("Municipio == @municipio") if mes else dataframe_solo_municipio