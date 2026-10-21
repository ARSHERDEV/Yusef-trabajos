from flask import Flask, request, jsonify
from flask_cors import CORS
from usuarios import validar_credenciales, AutenticacionError

app = Flask(__name__)
CORS(app)

INVENTARIO_FRUTAS = [
    {"id": 1, "nombre": "Manzana", "calorias": 52, "emoji": "🍎"},
    {"id": 2, "nombre": "Banano", "calorias": 89, "emoji": "🍌"},
    {"id": 3, "nombre": "Fresa", "calorias": 32, "emoji": "🍓"},
    {"id": 4, "nombre": "Naranja", "calorias": 47, "emoji": "🍊"},
    {"id": 5, "nombre": "Uva", "calorias": 69, "emoji": "🍇"}
]

frutas_seleccionadas = []

@app.route('/api/ejercicios', methods=['GET'])
def obtener_ejercicios():
    ejercicios_txt = {
        "javascript": [
            {
                "id": 1,
                "titulo": "Ejercicio 1 (JS): Mayoría de edad",
                "codigo": "const edad = 20;\nconst estado = (edad >= 18) ? 'Mayor de edad' : 'Menor de edad';\nconsole.log(estado);"
            },
            {
                "id": 2,
                "titulo": "Ejercicio 2 (JS): Par e impar",
                "codigo": "const numero = 7;\nconst resultado = (numero % 2 === 0) ? 'Par' : 'Impar';\nconsole.log(resultado);"
            },
            {
                "id": 3,
                "titulo": "Ejercicio 3 (JS): Descuento de miembro",
                "codigo": "const esMiembro = true;\nconst descuento = esMiembro ? 0.20 : 0.0;\nconsole.log(`Descuento: ${descuento * 100}%`);"
            }
        ],
        "python": [
            {
                "id": 4,
                "titulo": "Ejercicio 4 (Python): Positivo o Negativo",
                "codigo": "num = -5\nresultado = 'Positivo' if num >= 0 else 'Negativo'\nprint(resultado)"
            },
            {
                "id": 5,
                "titulo": "Ejercicio 5 (Python): Validar Acceso",
                "codigo": "autenticado = True\nmensaje = 'Acceso concedido' if autenticado else 'Acceso denegado'\nprint(mensaje)"
            },
            {
                "id": 6,
                "titulo": "Ejercicio 6 (Python): Estado Académico",
                "codigo": "nota = 3.5\nestado = 'Aprobado' if nota >= 3.0 else 'Reprobado'\nprint(estado)"
            },
            {
                "id": 7,
                "titulo": "Ejercicio 7 (Python): Número Máximo",
                "codigo": "a, b = 15, 22\nmaximo = a if a > b else b\nprint(f'El mayor es: {maximo}')"
            },
            {
                "id": 8,
                "titulo": "Ejercicio 8 (Python): Control de Stock",
                "codigo": "stock = 2\nalerta = 'Stock ok' if stock >= 3 else 'Reabastecer stock'\nprint(alerta)"
            }
        ]
    }
    return jsonify(ejercicios_txt), 200

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        validar_credenciales(username, password)
        return jsonify({"mensaje": f"Bienvenido/a {username}", "status": "ok"}), 200

    except AutenticacionError as e:
        return jsonify({"error": str(e)}), 401

@app.route('/api/inventario', methods=['GET'])
def obtener_inventario():
    return jsonify(INVENTARIO_FRUTAS), 200

@app.route('/api/frutas', methods=['GET'])
def obtener_seleccion():
    return jsonify(frutas_seleccionadas), 200

@app.route('/api/frutas', methods=['POST'])
def agregar_fruta():
    data = request.get_json() or {}
    fruta_id = data.get('id')
    fruta = next((f for f in INVENTARIO_FRUTAS if f['id'] == fruta_id), None)
    
    if not fruta:
        return jsonify({"error": "Fruta no encontrada."}), 400

    frutas_seleccionadas.append(fruta.copy())
    return jsonify({"mensaje": f"{fruta['nombre']} agregada."}), 201

@app.route('/api/frutas/<int:index>', methods=['PUT'])
def actualizar_fruta(index):
    if index < 0 or index >= len(frutas_seleccionadas):
        return jsonify({"error": "Índice fuera de rango."}), 400

    data = request.get_json() or {}
    nuevo_id = data.get('id')
    nueva_fruta = next((f for f in INVENTARIO_FRUTAS if f['id'] == nuevo_id), None)

    if not nueva_fruta:
        return jsonify({"error": "El ID ingresado no existe."}), 400

    frutas_seleccionadas[index] = nueva_fruta.copy()
    return jsonify({"mensaje": "Fruta actualizada."}), 200

@app.route('/api/frutas/<int:index>', methods=['DELETE'])
def eliminar_fruta(index):
    if index < 0 or index >= len(frutas_seleccionadas):
        return jsonify({"error": "Índice fuera de rango."}), 400

    eliminada = frutas_seleccionadas.pop(index)
    return jsonify({"mensaje": f"'{eliminada['nombre']}' eliminada."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)