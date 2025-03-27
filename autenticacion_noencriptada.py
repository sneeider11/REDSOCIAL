import firebase_admin
from firebase_admin import credentials, db
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Configuración exclusiva para Realtime Database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'  # Reemplaza con tu URL real
})

# Variable global para el usuario actual
usuario_actual = None
console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    """Muestra un mensaje formateado con Rich"""
    console.print(Panel(Text(contenido, justify="center"), 
                       title=titulo, 
                       style=estilo,
                       border_style=estilo))

def registrar_usuario():
    """Registra un nuevo usuario directamente en Realtime Database"""
    console.print(Panel("Registro de nuevo usuario", style="blue"))
    
    datos = questionary.form(
        email=questionary.text("Correo electrónico:"),
        nombre=questionary.text("Nombre completo:"),
        contraseña=questionary.password("Contraseña:"),
        confirmar=questionary.password("Confirmar contraseña:")
    ).ask()
    
    if datos["contraseña"] != datos["confirmar"]:
        mostrar_mensaje("Error", "Las contraseñas no coinciden")
        return
    
    # Referencia a la colección de usuarios
    usuarios_ref = db.reference('usuarios')
    
    # Verificar si el email ya existe
    usuarios = usuarios_ref.get() or {}
    for uid, user_data in usuarios.items():
        if user_data.get('email') == datos["email"]:
            mostrar_mensaje("Error", "El correo electrónico ya está registrado")
            return
    
    # Crear nuevo usuario con ID automático
    nuevo_usuario_ref = usuarios_ref.push({
        "email": datos["email"],
        "nombre": datos["nombre"],
        "contraseña": datos["contraseña"],  # ¡Precaución: Almacenamiento inseguro!
        "activo": True
    })
    
    mostrar_mensaje("Éxito", f"Usuario registrado con ID: {nuevo_usuario_ref.key}", "green")

def iniciar_sesion():
    """Inicia sesión buscando en Realtime Database"""
    global usuario_actual
    
    console.print(Panel("Inicio de sesión", style="blue"))
    
    credenciales = questionary.form(
        email=questionary.text("Correo electrónico:"),
        contraseña=questionary.password("Contraseña:")
    ).ask()
    
    # Buscar en todos los usuarios
    usuarios_ref = db.reference('usuarios')
    usuarios = usuarios_ref.get() or {}
    
    usuario_encontrado = None
    for uid, user_data in usuarios.items():
        if user_data.get('email') == credenciales["email"]:
            if user_data.get('contraseña') == credenciales["contraseña"]:
                usuario_encontrado = user_data
                usuario_encontrado['id'] = uid
                break
    
    if not usuario_encontrado:
        mostrar_mensaje("Error", "Credenciales incorrectas")
        return
    
    usuario_actual = {
        "id": usuario_encontrado['id'],
        "email": usuario_encontrado['email'],
        "nombre": usuario_encontrado['nombre']
    }
    
    mostrar_mensaje("Éxito", f"Bienvenido, {usuario_actual['nombre']}!", "green")

def menu_principal():
    """Menú principal solo con opciones de Realtime Database"""
    while True:
        console.print(Panel("Sistema de Autenticación (Realtime DB)", style="bold blue"))
        
        opcion = questionary.select(
            "Seleccione una opción:",
            choices=[
                "Iniciar sesión",
                "Registrarse",
                "Salir"
            ]
        ).ask()
        
        if opcion == "Iniciar sesión":
            iniciar_sesion()
            if usuario_actual:
                menu_usuario()
        elif opcion == "Registrarse":
            registrar_usuario()
        elif opcion == "Salir":
            break

def menu_usuario():
    """Menú para usuarios autenticados"""
    global usuario_actual
    
    while usuario_actual:
        console.print(Panel(f"Usuario: {usuario_actual['nombre']}", style="bold green"))
        
        opcion = questionary.select(
            "Seleccione una opción:",
            choices=[
                "Ver perfil",
                "Cerrar sesión"
            ]
        ).ask()
        
        if opcion == "Ver perfil":
            mostrar_perfil()
        elif opcion == "Cerrar sesión":
            usuario_actual = None
            mostrar_mensaje("Info", "Sesión cerrada correctamente", "blue")

def mostrar_perfil():
    """Muestra datos del usuario desde Realtime Database"""
    if not usuario_actual:
        return
    
    # Obtener datos actualizados
    usuario_ref = db.reference(f'usuarios/{usuario_actual["id"]}')
    datos_usuario = usuario_ref.get()
    
    console.print(Panel.fit(
        f"Nombre: {datos_usuario['nombre']}\n"
        f"Email: {datos_usuario['email']}\n"
        f"ID: {usuario_actual['id']}",
        title="Perfil de usuario",
        border_style="green"
    ))

if __name__ == "__main__":
    menu_principal()
