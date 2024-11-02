import streamlit as st

st.set_page_config(
    page_title="Kaax Analytics",
    page_icon="kaax_logo.png",
    layout="wide"
)

st.sidebar.image("kaax_logo.png")

st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Bienvenidos a Kaax Analytics")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.image("agricultura_inicio.jpg")

with col2:
    st.markdown("""
    **Kaax Analytics** se esfuerza por hacer accesible la información sobre agricultura en Guatemala.
    - Fundado por [Ahau-x](https://www.linkedin.com/company/ahau-x)
    - Datos confiables del SENACYT
    - Herramientas para tomar decisiones informadas.
    """)

st.divider()

st.subheader("¿Cómo lo hacemos?")
st.write("""
Con la ayuda de la estadística y las gráficas, desenterramos patrones ocultos en los datos, ¿el resultado? Información clara y fácil de entender sobre la variedad de productos, las tendencias del mercado, precios y más. Así puedes estar mejor preparado para tomar decisiones inteligentes y contribuir al crecimiento del sector agrícola guatemalteco.
""")

st.subheader("Únete a nuestra causa")
st.write("""
Únete a nosotros en Kaax Analytics para investigar, descubrir y celebrar la diversidad de productos agrícolas de Guatemala. Juntos, podemos promover el conocimiento y la apreciación por nuestra tierra y nuestra cultura, trabajando hacia un futuro donde cada producto agrícola sea reconocido y valorado por su contribución a nuestra identidad nacional y al bienestar de nuestra comunidad.
""")

st.subheader("Explorar datos históricos")
st.write("""
Interpretar datos estadísticos, especialmente de muchos años atrás, puede resultar complejo, requiere comprender el contexto histórico y desenterrar patrones ocultos a lo largo del tiempo. En [Ahau-x](https://www.linkedin.com/company/ahau-x), buscamos simplificar este proceso, proporcionando herramientas accesibles para que todos puedan comprender y utilizar la información estadística, sin importar su complejidad temporal.
""")

st.divider()

st.subheader("¿Por qué te debería interesar esto?")
st.write("""
Entender el pasado nos ayuda a construir un futuro mejor. Los datos estadísticos históricos son como una ventana al pasado, nos muestran cómo han evolucionado las cosas y nos dan pistas sobre cómo podemos mejorar.
""")

st.video("https://www.youtube.com/watch?v=X43nM9CCnsk")

st.write("Para aquellos interesados en explorar más sobre la agricultura guatemalteca, Kaax Analytics ofrece un tesoro de información lista para ser explorada. ¡No pierdas la oportunidad de sumergirte en este vasto conjunto de datos y conocimientos con nosotros! Consulta nuestra tabla de contenidos y descubre todo lo que tenemos para ofrecer.")
st.subheader("Tabla de Contenidos")
st.write("""
- [Análisis de ventas en productos agropecuarios](Ventas_en_productos_agropecuarios#44541ad1)
- [Uso de tierras](Uso_de_tierras#cobertura-vegetal-y-uso-de-tierra)
""")
