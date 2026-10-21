// 1. Validar la temperatura para alerta de clima
const temperatura = 32;
const alertaClima = temperatura > 30 ? "Alerta de calor" : "Clima normal";
console.log(alertaClima);

// 2. Determinar el costo del envío según suscripción
const esPremium = true;
const costoEnvio = esPremium ? 0 : 5.99;
console.log(`El costo de envío es: $${costoEnvio}`);

// 3. Comprobar si una lista/arreglo tiene elementos
const productos = ["Laptop", "Mouse"];
const estadoCarrito = productos.length > 0 ? "Carrito con productos" : "Carrito vacío";
console.log(estadoCarrito);