# 🐧 LinuxPath — Guía de Migración con IA

Aplicación web full-stack que usa IA (Google Gemini o Groq) para generar
una guía de migración a Linux personalizada según tu hardware, aplicaciones y experiencia.

---

## 📁 Estructura del proyecto

```
linux-migration/
├── app.py               ← Backend Flask (API + servidor de archivos)
├── requirements.txt     ← Dependencias Python
├── .env.example         ← Plantilla de variables de entorno
├── .env                 ← Tu archivo de claves (créalo tú, NO subir a Git)
└── templates/
    └── index.html       ← Frontend completo (HTML + Tailwind + JS)
```

---

## 🚀 Instrucciones de ejecución local

### Paso 1 — Obtén una API Key gratuita

**Opción A: Google Gemini (recomendado)**
1. Ve a https://aistudio.google.com
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API key" → "Create API key"
4. Copia la clave generada

**Opción B: Groq**
1. Ve a https://console.groq.com
2. Regístrate y ve a "API Keys"
3. Crea una nueva clave y cópiala

---

### Paso 2 — Clona o descarga el proyecto

```bash
# Si usas Git:
git clone <URL_DEL_REPO>
cd linux-migration

# O simplemente crea la carpeta y coloca los archivos manualmente
```

---

### Paso 3 — Crea el entorno virtual de Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activarlo (Linux / macOS)
source venv/bin/activate

# Activarlo (Windows)
venv\Scripts\activate
```

---

### Paso 4 — Instala las dependencias

```bash
pip install -r requirements.txt
```

---

### Paso 5 — Configura tu API Key

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Copia la plantilla
cp .env.example .env
```

Edita el archivo `.env` y pega tu clave:

```env
# Para Gemini:
GEMINI_API_KEY=AIzaSy...TuClaveAqui

# O para Groq (descomenta y usa esta en lugar de la anterior):
# GROQ_API_KEY=gsk_...TuClaveAqui
```

Luego carga las variables en tu terminal:

```bash
# Linux / macOS
export $(cat .env | xargs)

# Windows PowerShell
Get-Content .env | ForEach-Object { $k,$v = $_ -split '=',2; [System.Environment]::SetEnvironmentVariable($k,$v) }
```

---

### Paso 6 — Ejecuta el servidor

```bash
python app.py
```

Deberías ver:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Paso 7 — Abre la aplicación

Abre tu navegador y ve a:
```
http://localhost:5000
```

---

## ✅ Verificar que todo funciona

Puedes verificar el estado del backend en:
```
http://localhost:5000/api/health
```

Deberías ver algo como:
```json
{
  "gemini_key": true,
  "groq_key": false,
  "provider": "gemini",
  "status": "ok"
}
```

---

## 🛠️ Solución de problemas frecuentes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: flask` | Activa el entorno virtual: `source venv/bin/activate` |
| `Error: GEMINI_API_KEY no está configurada` | Exporta la variable: `export GEMINI_API_KEY=tuClave` |
| La IA responde en formato inesperado | Vuelve a intentarlo; los LLMs a veces fallan |
| `ConnectionRefusedError` en el frontend | Asegúrate de que `python app.py` esté corriendo |

---

## 🔒 Seguridad

- **Nunca subas tu `.env` a Git.** Agrega `.env` a tu `.gitignore`.
- Las claves de API son gratuitas pero tienen límites de uso; respétalos.
