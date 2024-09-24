import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Asignaturas de primer año y fechas de mesas de exámenes
asignaturas_fechas = {
    "Asignatura": ["Matemática", "Economía", "Contabilidad", "Administración General", "Derecho Comercial","Matemática", "Economía", "Contabilidad", "Administración General", "Derecho Comercial"],
    "Fecha de Examen": ["2024-12-02", "2024-12-04","2024-12-05", "2024-12-10", "2024-12-12","2024-12-13", "2024-12-15","2024-12-17","2024-12-18","2024-12-20"]
}
df_asignaturas = pd.DataFrame(asignaturas_fechas)
fechas_asignaturas = pd.to_datetime(df_asignaturas["Fecha de Examen"]).tolist()

# Función para calcular las fechas de exámenes con preferencia de estudiantes y máxima participación
def generar_fechas_examenes(fechas_disponibles, max_examenes_semana, dias_entre_examenes, preferencias, estudiantes_disponibilidad):
    fechas_seleccionadas = []
    semanas_examenes = {}

    # Ordenar fechas según preferencias
    fechas_disponibles.sort(key=lambda x: preferencias.get(x, 0), reverse=True)

    for fecha in sorted(fechas_disponibles):
        # Verificar si cumple con la restricción de no más de dos exámenes por semana
        semana = fecha.isocalendar()[1]  # Obtener el número de semana
        if semana not in semanas_examenes:
            semanas_examenes[semana] = 0

        if semanas_examenes[semana] < max_examenes_semana:
            # Verificar la distancia de días con el último examen programado
            if len(fechas_seleccionadas) == 0 or (fecha - fechas_seleccionadas[-1][0]).days >= dias_entre_examenes:
                # Calcular el porcentaje de estudiantes que pueden presentarse
                total_estudiantes = len(estudiantes_disponibilidad)
                estudiantes_presentes = sum([1 for estudiante in estudiantes_disponibilidad if fecha in estudiante])
                porcentaje_presentes = (estudiantes_presentes / total_estudiantes) * 100

                # Agregar la fecha a la lista de fechas seleccionadas si hay una buena cantidad de estudiantes disponibles
                if estudiantes_presentes > 0:
                    fechas_seleccionadas.append((fecha, porcentaje_presentes))
                    semanas_examenes[semana] += 1

    return fechas_seleccionadas

# Configuración inicial de Streamlit
st.title("Sistema de apoyo para la selección de fechas de exámenes")
st.write("Este sistema ayuda a seleccionar las mejores fechas de exámenes del turno de diciembre, maximizando la participación de los estudiantes.")

# Mostrar la tabla de asignaturas y fechas de examen
st.subheader("Asignaturas de primer año y fechas de mesas de examen")
st.dataframe(df_asignaturas)

# Ingreso de datos: Número de estudiantes
n_estudiantes = st.number_input("Número de estudiantes en el grupo", min_value=1, step=1)

# Ingreso de las preferencias individuales y disponibilidad
preferencias = {}
estudiantes_disponibilidad = []
for i in range(n_estudiantes):
    st.subheader(f"Disponibilidad y preferencias del estudiante {i+1}")
    fechas_estudiante = st.multiselect(f"Seleccione las fechas disponibles para el estudiante {i+1}",
                                       options=fechas_asignaturas,
                                       format_func=lambda x: x.strftime('%Y-%m-%d'))

    # Ingreso de las preferencias para cada fecha
    for fecha in fechas_estudiante:
        preferencia = st.slider(f"Preferencia del estudiante {i+1} para la fecha {fecha.strftime('%Y-%m-%d')}",
                                min_value=1, max_value=5, value=3)
        preferencias[fecha] = preferencia

    # Agregar la disponibilidad del estudiante al grupo
    estudiantes_disponibilidad.append(fechas_estudiante)

# Parámetros de restricción
st.subheader("Restricciones")
max_examenes_semana = st.slider("Máximo de exámenes por semana", min_value=1, max_value=5, value=2)
dias_entre_examenes = st.slider("Mínimo de días entre exámenes", min_value=1, max_value=7, value=2)

# Generar las fechas de exámenes
if st.button("Generar fechas de exámenes"):
    # Recoger todas las fechas disponibles de los estudiantes
    fechas_disponibles = list(preferencias.keys())

    if len(fechas_disponibles) > 0:
        fechas_propuestas = generar_fechas_examenes(fechas_disponibles, max_examenes_semana, dias_entre_examenes, preferencias, estudiantes_disponibilidad)
        if fechas_propuestas:
            st.success("Fechas propuestas y porcentaje de participación de estudiantes:")
            for fecha, porcentaje in fechas_propuestas:
                st.write(f"Examen en: {fecha.strftime('%Y-%m-%d')} - {porcentaje:.2f}% de estudiantes disponibles")
        else:
            st.error("No se pudieron proponer fechas que cumplan con las restricciones.")
    else:
        st.error("Por favor, ingrese fechas disponibles.")
