from turtle import st
import pandas as pd
#
# def traducir_mes(mes):
#   traduccion = {
#       "January":"Enero",
#       "February":"Febrero",
#       "March":"Marzo",
#       "April":"Abril",
#       "May":"Mayo",
#       "June":"Junio",
#       "July":"Julio",
#       "August":"Agosto",
#       "September":"Septiembre",
#       "October":"Octubre",
#       "November":"Noviembre",
#       "December":"Diciembre"
#   }
#   return traduccion[mes]
#
# def convertir_horas_a_minutos(horas):
#     horas_enteras = int(horas)
#     minutos = round((horas - horas_enteras) * 60)
#     return f"{horas_enteras}h {minutos}m"
#
# def clean_actividad_revisores(actividad_revisores):
#     actividad_revisores = actividad_revisores.rename(columns = {"Cliente":"Municipio"})
#     actividad_revisores["Municipio"] = actividad_revisores["Municipio"].str.capitalize()
#     actividad_revisores["Tipo de Cámara"] = actividad_revisores["Tipo de Cámara"].replace({"Luces Bajas":"Luces", "Semáforo Rojo":"Semáforo"})
#     actividad_revisores["Auditor"] = actividad_revisores["Auditor"].map(lambda x: ' '.join(x.split())).map(lambda x:str(x).title())
#     actividad_revisores["Código de cámara"] = actividad_revisores["Código de cámara"].map(lambda x:(x.split("-")[-1]).strip())
#     actividad_revisores["Fecha"] = pd.to_datetime(actividad_revisores["Fecha"])
#     actividad_revisores["Fecha"] = actividad_revisores["Fecha"]
#     actividad_revisores_listo = actividad_revisores.drop(columns = ["Tipo de Revisión","% aceptadas","Recorte","Deshacer","NoOp"])
#     actividad_revisores_listo["Mes"] = actividad_revisores_listo["Fecha"].dt.month_name().map(traducir_mes)
#     return actividad_revisores_listo
# @st.cache_data
# def get_data_from_csv():
#     actividad_auditores = pd.read_csv("Files/01-Actividad de revisores.xlsx")
#     actividad_auditores = clean_actividad_revisores(actividad_auditores)
#     return actividad_auditores
#
#
# @st.cache_data
# def get_data_vulcan_csv():
#     horas_auditores = pd.read_csv("Files/03-Tiempo de revisión.xlsx")
#     return horas_auditores
#
#
# actividad_auditores = get_data_from_csv()
# horas_auditores = get_data_vulcan_csv()
#
# st.dataframe(actividad_auditores)