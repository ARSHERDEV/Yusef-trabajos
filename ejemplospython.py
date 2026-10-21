# 1. Determinar si un número es par o impar
numero = 7
resultado_paridad = "Par" if numero % 2 == 0 else "Impar"
print(f"El número {numero} es {resultado_paridad}.")

# 2. Verificar si una persona es mayor de edad
edad = 20
estado_edad = "Mayor de edad" if edad >= 18 else "Menor de edad"
print(f"Estado: {estado_edad}.")

# 3. Asignar un descuento según el monto de compra
monto_compra = 120
descuento = 0.15 if monto_compra > 100 else 0.05
print(f"Descuento aplicado: {descuento * 100}%")

# 4. Validar el estado de inicio de sesión
usuario_activo = True
mensaje_acceso = "Bienvenido al sistema" if usuario_activo else "Por favor inicie sesión"
print(mensaje_acceso)

# 5. Obtener el valor máximo entre dos números
a, b = 15, 25
mayor = a if a > b else b
print(f"El número mayor entre {a} y {b} es {mayor}.")