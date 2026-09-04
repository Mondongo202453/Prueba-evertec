import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask import redirect, url_for
from placetopay import crear_sesion, consultar_sesion

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "clave-local-de-prueba")

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
        url_for("resultado", _external=True)
    )
    
    session["request_id"] = resultado["requestId"]
    return redirect(resultado["processUrl"])



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
    
    

if __name__ == "__main__":
    if not os.getenv("PLACETOPAY_LOGIN"):
        raise RuntimeError("Falta PLACETOPAY_LOGIN en el archivo .env")

    if not os.getenv("PLACETOPAY_URL"):
        raise RuntimeError("Falta PLACETOPAY_URL en el archivo .env")

    app.run(host="127.0.0.1", port=5000, debug=True)