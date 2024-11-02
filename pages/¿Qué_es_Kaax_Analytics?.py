import streamlit as st

st.set_page_config(
    page_title="Kaax Analytics",
    page_icon="kaax_logo.png",
    layout="wide"
)

st.sidebar.image("kaax_logo.png")

st.title("¿Qué es Kaax Analytics?")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

st.header("Facilitando el acceso a la información agrícola")
st.write("""
Kaax Analytics es una plataforma abierta al público diseñada para democratizar el acceso a la información analítica y predictiva en el sector agrícola. 
Con el uso de fuentes confiables como SENACYT, nuestro objetivo es ofrecer análisis complejos y modelos de predicción accesibles a todos.
""")

st.image("/Users/tribal/PycharmProjects/KaaxAnalitycs/kaax_analytics/imagen_agricola.jpg", caption="Innovando en la agricultura")

st.subheader("¿Qué ofrecemos?")
st.write("""
En Kaax Analytics, empleamos la inteligencia artificial para transformar el sector agrícola, ofreciendo:
- **Análisis Complejos:** Extraemos insights valiosos de grandes volúmenes de datos.
- **Modelos de Predicción:** Predecimos tendencias del mercado para apoyar la planificación agrícola.
- **Accesibilidad:** Facilitamos herramientas fáciles de usar para agricultores, investigadores y profesionales del sector.
""")

st.subheader("Únete al movimiento")
st.write("""
**Contribuye con datos o conocimientos:** Si tienes acceso a fuentes de datos agrícolas o conocimientos que pueden enriquecer nuestra plataforma, te invitamos a colaborar. Tu participación es fundamental para seguir ampliando nuestro alcance y mejorar nuestras capacidades analíticas.

**Explora oportunidades en el sector privado:** También trabajamos en proyectos específicos para el sector privado. Si estás interesado en colaboraciones más dirigidas o en explorar soluciones personalizadas, [contáctanos](mailto:sales@ahau-x.com).
""")

st.button("Comenzar a explorar")

st.markdown("### ¿Necesitas más información?")
st.markdown("Contacta con nosotros a través de [nuestro formulario de contacto](#) o enviando un correo a [support@ahau-x.com](mailto:sales@ahau-x.com).")
