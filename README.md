# 🎧 Autenticación OAuth con Spotify en Python

Este proyecto implementa el flujo completo de autenticación OAuth 2.0 con **Spotify** usando solo **Python puro**, sin frameworks adicionales como Flask o FastAPI.  
Es ideal para principiantes que desean entender cómo funciona OAuth paso a paso y hacer solicitudes a la API de Spotify de forma segura.

---

## 🚀 Características

- Flujo de autorización OAuth 2.0 (`authorization_code`)
- Obtención y uso del `access_token`
- Renovación automática con `refresh_token`
- Almacenamiento seguro de tokens en `token.json`
- Uso de variables de entorno (`.env`)
- Sin frameworks externos, solo librerías estándar y `requests`

---

## 📦 Requisitos

- Python 3.8 o superior
- Cuenta de desarrollador en [Spotify Developer](https://developer.spotify.com/dashboard/)

---

## 📁 Instalación

1. **Clona el repositorio:**

```bash
git clone https://github.com/tu-usuario/spotify-oauth-python.git
cd spotify-oauth-python

