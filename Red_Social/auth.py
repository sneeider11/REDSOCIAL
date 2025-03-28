import firebase_admin
from firebase_admin import credentials, db
import questionary
import re
import bcrypt
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import datetime

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(Text(contenido, justify="center"), 
                       title=titulo, 
                       style=estilo,
                       border_style=estilo))

def es_correo_valido(correo):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, correo))

def encriptar_contraseña(contraseña):
    if isinstance(contraseña, str):
        contraseña = contraseña.encode('utf-8')
    sal = bcrypt.gensalt()
    hashed = bcrypt.hashpw(contraseña, sal)
    return hashed.decode('utf-8')

def verificar_contraseña(contraseña_plana, contraseña_hash):
    if isinstance(contraseña_plana, str):
        contraseña_plana = contraseña_plana.encode('utf-8')
    if isinstance(contraseña_hash, str):
        contraseña_hash = contraseña_hash.encode('utf-8')
    return bcrypt.checkpw(contraseña_plana, contraseña_hash)

def registrar_usuario():
    console.print(Panel("Registro de nuevo usuario", style="blue"))
    
    datos = questionary.form(
        email=questionary.text("Correo electrónico:"),
        nombre=questionary.text("Nombre completo:"),
        contraseña=questionary.password("Contraseña:"),
        confirmar=questionary.password("Confirmar contraseña:")
    ).ask()
    
    if not datos:
        return
    
    if not es_correo_valido(datos["email"]):
        mostrar_mensaje("Error", "El correo electrónico no tiene un formato válido")
        return
    
    if len(datos["contraseña"]) < 8:
        mostrar_mensaje("Error", "La contraseña debe tener al menos 8 caracteres")
        return
    
    if datos["contraseña"] != datos["confirmar"]:
        mostrar_mensaje("Error", "Las contraseñas no coinciden")
        return
    
    usuarios_ref = db.reference('usuarios')
    usuarios = usuarios_ref.get() or {}
    
    for uid, user_data in usuarios.items():
        if user_data.get('email') == datos["email"]:
            mostrar_mensaje("Error", "El correo electrónico ya está registrado")
            return
    
    contraseña_encriptada = encriptar_contraseña(datos["contraseña"])
    
    nuevo_usuario_ref = usuarios_ref.push({
        "email": datos["email"],
        "nombre": datos["nombre"],
        "contraseña": contraseña_encriptada,
        "activo": True,
        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    mostrar_mensaje("Éxito", f"Usuario registrado con ID: {nuevo_usuario_ref.key}", "green")

def iniciar_sesion(usuario_actual):
    console.print(Panel("Inicio de sesión", style="blue"))
    
    credenciales = questionary.form(
        email=questionary.text("Correo electrónico:"),
        contraseña=questionary.password("Contraseña:")
    ).ask()
    
    if not credenciales:
        return None
    
    usuarios_ref = db.reference('usuarios')
    usuarios = usuarios_ref.get() or {}
    
    usuario_encontrado = None
    for uid, user_data in usuarios.items():
        if user_data.get('email') == credenciales["email"]:
            if verificar_contraseña(credenciales["contraseña"], user_data.get('contraseña')):
                usuario_encontrado = user_data
                usuario_encontrado['id'] = uid
                break
    
    if not usuario_encontrado:
        mostrar_mensaje("Error", "Credenciales incorrectas")
        return None
    
    usuario_actual = {
        "id": usuario_encontrado['id'],
        "email": usuario_encontrado['email'],
        "nombre": usuario_encontrado['nombre']
    }
    
    mostrar_mensaje("Éxito", f"Bienvenido, {usuario_actual['nombre']}!", "green")
    return usuario_actual