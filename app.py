import os
import streamlit as st
import base64
from openai import OpenAI
import platform

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# Page configuration
st.set_page_config(page_title="Análisis de Imagen", layout="centered")

# Título
st.title("🤖🏞️ Análisis de Imagen")
st.write(f"🖥️ Python: {platform.python_version()}")

# Clave de API
ek = st.text_input('🔑 Ingresa tu API Key de OpenAI', type="password")
if ek:
    os.environ['OPENAI_API_KEY'] = ek
else:
    st.warning("Por favor ingresa tu API Key.")

# Cliente OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

# Carga de imagen
dfile = st.file_uploader("📤 Sube una imagen (jpg, png)", type=["jpg","png","jpeg"])

if dfile and ek:
    # Mostrar la imagen
    with st.expander("📷 Imagen cargada", expanded=True):
        st.image(dfile, caption=dfile.name, use_column_width=True)

    # Opcional: contexto adicional
details = st.text_area("✍️ Contexto adicional (opcional)", height=80)

    # Botón de análisis
    if st.button("🔎 Analizar imagen"):
        with st.spinner("Analizando..."):
            # Encode image
            b64 = encode_image(dfile)
            # Prompt inicial\ n            prompt = "Describe en español lo que ves en esta imagen."
            if details.strip():
                prompt += f"\nContexto adicional: {details.strip()}"
            # Construir mensajes
            messages = [
                {"role":"user","content":[
                    {"type":"text","text":prompt},
                    {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
                ]}
            ]
            # Llamar al modelo\ n            full_resp = ""
            ph = st.empty()
            for chunk in client.chat.completions.create(
                model="gpt-4o", messages=messages, stream=True, max_tokens=800
            ):
                delta = chunk.choices[0].delta.content
                if delta:
                    full_resp += delta
                    ph.markdown(full_resp + "▌")
            ph.markdown(full_resp)

            # Clasificación automática
            lr = full_resp.lower()
            is_doc = any(k in lr for k in ["documento","pdf","formulario","papel"])
            is_real = not is_doc
            pro = any(k in lr for k in ["cámara profesional","dslr","lens"]) 
            phone = any(k in lr for k in ["celular","móvil","smartphone","iphone","android"])
            ai = any(k in lr for k in ["ia","inteligencia artificial","generado por ai","sintetizado"]) 

            counts = {
                "Documento": int(is_doc),
                "Foto Real": int(is_real),
                "Profesional": int(pro),
                "Celular": int(phone),
                "Generado IA": int(ai)
            }
            # Gráfico de barras
            st.subheader("📊 Clasificación de la imagen")
            st.bar_chart(counts)

else:
    if dfile and not ek:
        st.warning("Por favor ingresa tu API Key para analizar.")
    else:
        st.info("Sube una imagen para comenzar el análisis.")
