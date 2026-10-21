

from getpass import getpass

USUARIOS = {
    "ana":   {"password": "1234", "rol": "admin",    "intentos": 0},
    "luis":  {"password": "abcd", "rol": "usuario",  "intentos": 0},
    "maria": {"password": "pass", "rol": "invitado", "intentos": 0},
}

MAX_INTENTOS = 3


class CredencialesInvalidas(Exception):
    """Excepcion personalizada del sistema de login."""



def leer_texto(mensaje, oculto=False):
    try:
        valor = getpass(mensaje) if oculto else input(mensaje)
        return valor.strip()
    except Exception:
        
        return ""


def obtener_usuario(nombre):
    try:
        return USUARIOS[nombre]
    except KeyError:
        raise CredencialesInvalidas("El usuario no existe")



def validar_longitud(texto, minimo=3):
    try:
        if len(texto) < minimo:
            raise ValueError(f"debe tener al menos {minimo} caracteres")
        return True
    except ValueError as e:
        print(f"  [validacion] El dato {e}")
        return False



def pedir_opcion():
    try:
        return int(input("Opcion: "))
    except ValueError:
        print("  Debes escribir un numero.")
    except EOFError:
        print("  Entrada cerrada.")
    except Exception:
        print("  Error inesperado al leer la opcion.")
    return -1



def intentos_restantes(nombre):
    try:
        return MAX_INTENTOS - USUARIOS[nombre]["intentos"]
    except (KeyError, TypeError):
        return MAX_INTENTOS



def verificar_password(usuario, password):
    try:
        coincide = usuario["password"] == password
    except (TypeError, KeyError):
        return False
    else:
        return coincide



def guardar_log(mensaje):
    archivo = None
    try:
        archivo = open("login.log", "a", encoding="utf-8")
        archivo.write(mensaje + "\n")
    except OSError:
        print("  No se pudo escribir el log.")
    finally:
        if archivo:
            archivo.close()




def autenticar(nombre, password):
    try:
        usuario = obtener_usuario(nombre)          

        try:                                       
            if usuario["intentos"] >= MAX_INTENTOS:
                raise PermissionError("Cuenta bloqueada por intentos fallidos")
        except PermissionError as e:
            print(f"  {e}")
            return None

        if not verificar_password(usuario, password):
            raise CredencialesInvalidas("Contrasena incorrecta")   

    except CredencialesInvalidas as e:
        registro = USUARIOS.get(nombre)
        if registro:
            registro["intentos"] += 1
        print(f"  {e}. Intentos restantes: {intentos_restantes(nombre)}")
        return None
    else:
        usuario["intentos"] = 0
        return usuario
    finally:
        guardar_log(f"intento de login -> {nombre}")


def menu(nombre, usuario):
    rol = usuario["rol"]

    while True:
        print(f"\n=== Sesion de {nombre} ({rol}) ===")
        print("1) Ver mi perfil")
        print("2) Listar usuarios (solo admin)")
        print("3) Cambiar contrasena")
        print("0) Cerrar sesion")

        opcion = pedir_opcion()

        match opcion:                                   
            case 1:
                match rol:                              
                    case "admin":
                        print("  Perfil con permisos totales.")
                    case "usuario":
                        print("  Perfil estandar.")
                    case "invitado":
                        print("  Perfil de solo lectura.")
                    case _:
                        print("  Rol desconocido.")

            case 2 if rol == "admin":
                for u, datos in USUARIOS.items():
                    print(f"  - {u} ({datos['rol']})")

            case 2:
                print("  No tienes permisos para esta opcion.")

            case 3:
                nueva = leer_texto("Nueva contrasena: ", oculto=True)
                if validar_longitud(nueva, 4):
                    usuario["password"] = nueva
                    print("  Contrasena actualizada.")

            case 0:
                print("  Sesion cerrada.")
                break

            case _:
                print("  Opcion no valida.")


def main():
    print("=== LOGIN ===")
    try:                                   
        while True:
            nombre = leer_texto("Usuario (o 'salir'): ").lower()

            if nombre == "salir":
                print("Hasta luego.")
                break
            if not validar_longitud(nombre):
                continue

            password = leer_texto("Contrasena: ", oculto=True)
            usuario = autenticar(nombre, password)

            if usuario:
                print(f"\nBienvenido/a, {nombre}!")
                menu(nombre, usuario)
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido por el usuario.")


if __name__ == "__main__":
    main()