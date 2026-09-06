# Tienda Evertec

Tienda de prueba en Flask integrada con Placetopay WebCheckout y Lightbox.

## Instalación de dependencias

Crear y activar el entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` como `.env` y completa las credenciales de prueba:

```env
PLACETOPAY_LOGIN=tu_login
PLACETOPAY_SECRET_KEY=tu_secret_key
PLACETOPAY_URL=https://checkout-test.placetopay.com
FLASK_SECRET_KEY=una_clave_local_segura
PLACETOPAY_NOTIFICATION_URL=https://tu-dominio-publico.com/notificacion
```

`PLACETOPAY_NOTIFICATION_URL` debe ser una URL pública con HTTPS. Una
dirección local como `http://127.0.0.1:5000/notificacion` no puede recibir
webhooks desde Placetopay.

## Ejecución

```bash
python app.py
```

Abre `http://127.0.0.1:5000`.

## Flujo implementado

1. Flask crea una sesión de Checkout y obtiene `processUrl`.
2. El frontend carga el script oficial de Lightbox.
3. Lightbox se inicia con `P.init(processUrl)`.
4. `P.on("response", ...)` recibe el final del proceso.
5. La aplicación usa el `requestId` para consultar el estado real en el backend.
6. Si Lightbox no puede abrirse, Placetopay utiliza el acceso de respaldo a
   `processUrl`.
7. El endpoint `POST /notificacion` valida firmas SHA-256 y SHA-1 durante la
   transición indicada por la documentación.

La tienda no captura ni almacena números de tarjeta, CVV o fechas de
vencimiento.

## Rutas

| Método | Ruta | Uso |
|---|---|---|
| GET | `/` | Tienda |
| GET | `/checkout` | Formulario y Lightbox |
| POST | `/crear-pago` | Crear sesión de pago |
| GET | `/resultado` | Consultar resultado |
| POST | `/notificacion` | Recibir y validar webhook |

La notificación debe procesarse en un servidor HTTPS accesible desde
Placetopay. El endpoint responde rápidamente con HTTP 2xx después de validar
la firma.
