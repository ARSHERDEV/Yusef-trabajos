class AutenticacionError(Exception):
    """Excepción para errores de autenticación."""
    pass

USUARIOS_DB = [
    {"username": "arce", "password": "123"},
    {"username": "maria", "password": "abc"},
    {"username": "juan", "password": "456"}
]

def validar_credenciales(username, password):
    valido = any(u['username'] == username and u['password'] == password for u in USUARIOS_DB)
    if not valido:
        raise AutenticacionError("Usuario o contraseña incorrectos.")
    return True