import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ─── Detectar qué SDK está disponible ───────────────────────────────────────
try:
    import google.generativeai as genai
    PROVIDER = "gemini"
except ImportError:
    PROVIDER = None

try:
    from groq import Groq
    if PROVIDER is None:
        PROVIDER = "groq"
except ImportError:
    pass

# ─── Prompt del sistema ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """
Eres un experto en sistemas Linux con más de 15 años de experiencia.
Tu tarea es analizar el hardware, las aplicaciones y el nivel de experiencia del usuario
y devolver UNA RESPUESTA ESTRICTAMENTE EN JSON válido, sin texto adicional, sin bloques de código markdown, sin explicaciones fuera del JSON.

El JSON debe tener exactamente esta estructura:
{
  "distribucion": {
    "nombre": "Nombre de la distro",
    "razon": "Explicación breve de por qué esta distro es ideal",
    "escritorio": "Nombre del entorno de escritorio recomendado",
    "sitio_web": "URL oficial de la distribución"
  },
  "alternativas": [
    {
      "nombre": "Segunda opción",
      "razon": "Por qué podría ser buena alternativa"
    },
    {
      "nombre": "Tercera opción",
      "razon": "Por qué podría ser buena alternativa"
    }
  ],
  "script_bash": "#!/bin/bash\\n# Script completo de instalación y configuración\\n# Incluir: actualización del sistema, instalación de equivalentes a las apps del usuario, drivers, herramientas útiles\\n# Al menos 25-35 líneas de comandos reales y útiles",
  "consejos": [
    "Consejo detallado 1 específico para el usuario",
    "Consejo detallado 2",
    "Consejo detallado 3",
    "Consejo detallado 4",
    "Consejo detallado 5"
  ],
  "compatibilidad_hardware": "Evaluación breve de compatibilidad con el hardware indicado",
  "tiempo_estimado": "Tiempo estimado de migración"
}
"""

def limpiar_json(texto: str) -> str:
    """Extrae el bloque JSON de la respuesta del modelo."""
    texto = texto.strip()
    # Quitar bloques markdown ```json ... ```
    texto = re.sub(r"^```(?:json)?\s*", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\s*```$", "", texto)
    # Encontrar el primer { y el último }
    inicio = texto.find("{")
    fin = texto.rfind("}")
    if inicio != -1 and fin != -1:
        return texto[inicio:fin+1]
    return texto


def llamar_gemini(hardware: str, apps: str, nivel: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    prompt = f"""
Hardware / Modelo de PC: {hardware}
Aplicaciones que utiliza: {apps}
Nivel de experiencia con Linux: {nivel}

Genera la guía de migración personalizada en JSON.
"""
    respuesta = model.generate_content(prompt)
    return json.loads(limpiar_json(respuesta.text))


def llamar_groq(hardware: str, apps: str, nivel: str) -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no está configurada en las variables de entorno.")

    client = Groq(api_key=api_key)
    prompt = f"""
Hardware / Modelo de PC: {hardware}
Aplicaciones que utiliza: {apps}
Nivel de experiencia con Linux: {nivel}

Genera la guía de migración personalizada en JSON.
"""
    chat = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    return json.loads(limpiar_json(chat.choices[0].message.content))


# ─── Rutas ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/api/recomendar", methods=["POST"])
def recomendar():
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "No se recibieron datos JSON."}), 400

    hardware = datos.get("hardware", "").strip()
    apps = datos.get("apps", "").strip()
    nivel = datos.get("nivel", "Principiante").strip()

    if not hardware or not apps:
        return jsonify({"error": "Los campos 'hardware' y 'apps' son obligatorios."}), 400

    try:
        if PROVIDER == "gemini":
            resultado = llamar_gemini(hardware, apps, nivel)
        elif PROVIDER == "groq":
            resultado = llamar_groq(hardware, apps, nivel)
        else:
            return jsonify({
                "error": "No se encontró ningún SDK de IA. Instala 'google-generativeai' o 'groq'."
            }), 500

        return jsonify(resultado)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except json.JSONDecodeError:
        return jsonify({"error": "La IA devolvió una respuesta en formato inesperado. Intenta de nuevo."}), 502
    except Exception as e:
        return jsonify({"error": f"Error al conectar con la API de IA: {str(e)}"}), 500


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "provider": PROVIDER or "ninguno",
        "gemini_key": bool(os.environ.get("GEMINI_API_KEY")),
        "groq_key": bool(os.environ.get("GROQ_API_KEY"))
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
