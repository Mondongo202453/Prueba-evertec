# Tienda Evertec

Tienda de prueba desarrollada con Python, Flask y Placetopay WebCheckout con
Lightbox.

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` como `.env` y completa tus credenciales:

```env
PLACETOPAY_LOGIN=tu_login
PLACETOPAY_SECRET_KEY=tu_secret_key
PLACETOPAY_URL=https://checkout-test.placetopay.com
FLASK_SECRET_KEY=tu_clave_local
PLACETOPAY_NOTIFICATION_URL=https://tu-dominio.com/notificacion
```

## Ejecutar

```bash
python app.py
```

Abre:

```text
http://127.0.0.1:5000
```
