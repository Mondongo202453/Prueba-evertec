import os
import uuid
import hashlib
import hmac
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, session
from flask import url_for
from placetopay import crear_sesion, consultar_sesion

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave-local-de-prueba")

@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://checkout.placetopay.com https://*.placetopay.com; "
        "connect-src 'self' https://checkout-test.placetopay.com https://*.placetopay.com; "
        "img-src 'self' data: https://*.placetopay.com; "
        "frame-src https://*.placetopay.com;"
    )
    return response

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/checkout")
def checkout():
    return render_template("checkout.html")

@app.post("/crear-pago")
def crear_pago():
    name = request.form.get("name")
    surname = request.form.get("surname")
    email = request.form.get("email")
    document = request.form.get("document")
    mobile = request.form.get("mobile")
    
    if not all([name, surname, email, document, mobile]):
        return "todos los campos son obligatorios", 400
    
    payment = {
    "reference": f"ORDEN-{uuid.uuid4().hex[:8].upper()}",
    "description": "Producto de prueba",
    "amount": {
        "currency": "COP",
        "total": 50000
    }
}
    buyer = {
    "name": name,
    "surname": surname,
    "email": email,
    "document": document,
    "documentType": "CC",
    "mobile": mobile
}
    resultado = crear_sesion(
        os.getenv("PLACETOPAY_LOGIN"),
        os.getenv("PLACETOPAY_SECRET_KEY"),
        os.getenv("PLACETOPAY_URL"),
        payment,
        buyer,
        url_for("resultado", _external=True),
        os.getenv("PLACETOPAY_NOTIFICATION_URL")
    )
    
    session["request_id"] = resultado["requestId"]
    
    return render_template(
        "checkout.html",
        process_url=resultado["processUrl"],
        request_id=resultado["requestId"]
    )



@app.get("/resultado")
def resultado():
    request_id = request.args.get("requestId") or session.get("request_id")

    if not request_id:
        return "No se recibió el requestId del pago", 400

    resultado_pago = consultar_sesion(
        os.getenv("PLACETOPAY_LOGIN"),
        os.getenv("PLACETOPAY_SECRET_KEY"),
        os.getenv("PLACETOPAY_URL"),
        request_id
    )

    estado = resultado_pago.get("status", {})

    return render_template(
        "resultado.html",
        request_id=request_id,
        estado=estado
    )


@app.post("/notificacion")
def notificacion():
    notification = request.get_json(silent=True)
    if not isinstance(notification, dict):
        return jsonify({"error": "El cuerpo debe ser un objeto JSON"}), 400

    request_id = notification.get("requestId")
    signature = notification.get("signature")
    status = notification.get("status")

    if not request_id or not isinstance(signature, str) or not isinstance(status, dict):
        return jsonify({"error": "La notificación no tiene la estructura requerida"}), 400

    status_name = status.get("status")
    status_date = status.get("date")
    secret_key = os.getenv("PLACETOPAY_SECRET_KEY")

    if not status_name or not status_date or not secret_key:
        return jsonify({"error": "No se puede validar la notificación"}), 500

    algorithm = "sha256" if signature.startswith("sha256:") else "sha1"
    received_signature = signature.removeprefix("sha256:")
    signature_data = f"{request_id}{status_name}{status_date}{secret_key}".encode("utf-8")

    if algorithm == "sha256":
        generated_signature = hashlib.sha256(signature_data).hexdigest()
    else:
        generated_signature = hashlib.sha1(signature_data).hexdigest()

    if not hmac.compare_digest(received_signature, generated_signature):
        return jsonify({"error": "Firma inválida"}), 401

    return jsonify({"status": "received"}), 200
    
    

if __name__ == "__main__":
    if not os.getenv("PLACETOPAY_LOGIN"):
        raise RuntimeError("Falta PLACETOPAY_LOGIN en el archivo .env")

    if not os.getenv("PLACETOPAY_URL"):
        raise RuntimeError("Falta PLACETOPAY_URL en el archivo .env")

    app.run(host="127.0.0.1", port=5000, debug=True)