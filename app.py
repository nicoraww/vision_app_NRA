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

# Header
st.title("🤖🏞️ Análisis de Imagen")
st.write(f"🖥️ Python: {platform.python_version()}")

# API Key input
api_key = st.text_input('🔑 Ingresa tu API Key de OpenAI', type='password')
if api_key:
    os.environ['OPENAI_API_KEY'] = api_key
else:
    st.warning("Por favor ingresa tu API Key.")

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))

# File uploader for image
uploaded_file = st.file_uploader("📤 Sube una imagen (jpg, png)", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    # Display uploaded image
    with st.expander("📷 Imagen cargada", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

    # Optional context
    details = st.text_area("✍️ Contexto adicional (opcional)", height=80)

    # Analyze button
    if st.button("🔎 Analizar imagen"):
        with st.spinner("Analizando..."):
            # Encode image
            b64 = encode_image(uploaded_file)

            # Build prompt
            prompt = "Describe en español lo que ves en la imagen."
            if details.strip():
                prompt += f"\nContexto adicional: {details.strip()}"

            # Prepare messages for chat
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }
            ]

            # Stream response
            full_resp = ""
            placeholder = st.empty()
            for chunk in client.chat.completions.create(model="gpt-4o", messages=messages, stream=True, max_tokens=800):
                delta = chunk.choices[0].delta.content
                if delta:
                    full_resp += delta
                    placeholder.markdown(full_resp + "▌")
            placeholder.markdown(full_resp)

            # Automatic classification based on response
            text_lower = full_resp.lower()
            classification = {
                "Documento": int(any(k in text_lower for k in ["documento", "pdf", "formulario", "papel"])),
                "Naturaleza": int(any(k in text_lower for k in ["árbol", "bosque", "rio", "montaña", "naturaleza"])),
                "Mascotas": int(any(k in text_lower for k in ["perro", "gato", "mascota", "animal doméstico"])),
                "Paisaje": int(any(k in text_lower for k in ["paisaje", "panorama", "cielo", "vista"])),
                "Comida": int(any(k in text_lower for k in ["comida", "alimento", "plato", "cocina"])),
                "Personas": int(any(k in text_lower for k in ["persona", "hombre", "mujer", "gente"])),
                "Arquitectura": int(any(k in text_lower for k in ["edificio", "arquitectura", "casa", "monumento"])),
                "Texto": int(any(k in text_lower for k in ["texto", "letras", "escrito", "mensaje"]))
            }

            # Display chart
            st.subheader("📊 Clasificación de la imagen")
            st.bar_chart(classification)

elif uploaded_file and not api_key:
    st.warning("🔒 Por favor ingresa tu API Key para analizar.")
else:
    st.info("⬆️ Sube una imagen para comenzar el análisis.")
