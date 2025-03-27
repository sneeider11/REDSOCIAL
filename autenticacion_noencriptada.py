import firebase_admin
from firebase_admin import credentials, firestore
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Configuración de Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    """Registra un nuevo usuario en Firestore (sin encriptación)"""
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
    
    # Verificar si el usuario ya existe
    usuarios_ref = db.collection("usuarios")
    query = usuarios_ref.where("email", "==", datos["email"]).get()
    
    if len(query) > 0:
        mostrar_mensaje("Error", "El correo electrónico ya está registrado")
        return
    
    # Guardar usuario en Firestore (contraseña en texto plano)
    nuevo_usuario = {
        "email": datos["email"],
        "nombre": datos["nombre"],
        "contraseña": datos["contraseña"],  # ← Sin hash
        "activo": True
    }
    
    usuarios_ref.add(nuevo_usuario)
    mostrar_mensaje("Éxito", "Usuario registrado correctamente", "green")

def iniciar_sesion():
    """Inicia sesión con un usuario existente (sin bcrypt)"""
    global usuario_actual
    
    console.print(Panel("Inicio de sesión", style="blue"))
    
    datos = questionary.form(
        email=questionary.text("Correo electrónico:"),
        contraseña=questionary.password("Contraseña:")
    ).ask()
    
    # Buscar usuario en Firestore
    usuarios_ref = db.collection("usuarios")
    query = usuarios_ref.where("email", "==", datos["email"]).get()
    
    if len(query) == 0:
        mostrar_mensaje("Error", "❌ Usuario no encontrado")
        return
    
    # Obtener datos del usuario
    usuario = query[0].to_dict()
    usuario["id"] = query[0].id
    
    # Verificar contraseña (comparación directa)
    if datos["contraseña"] != usuario["contraseña"]:  # ← Sin bcrypt
        mostrar_mensaje("Error", "❌ Contraseña incorrecta")
        return
    
    # Establecer usuario actual
    usuario_actual = {
        "id": usuario["id"],
        "email": usuario["email"],
        "nombre": usuario["nombre"]
    }
    
    mostrar_mensaje("Éxito", f"Bienvenido, {usuario['nombre']}!", "green")

# ... (El resto del código de menús permanece igual)
def menu_principal():
    """Muestra el menú principal"""
    while True:
        console.print(Panel("Sistema de Autenticación", style="bold blue"))
        
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
    """Muestra el menú para usuarios autenticados"""
    global usuario_actual
    
    while usuario_actual:
        console.print(Panel(f"Bienvenido, {usuario_actual['nombre']}", style="bold green"))
        
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
    """Muestra la información del perfil del usuario"""
    if not usuario_actual:
        return
    
    console.print(Panel.fit(
        f"Nombre: {usuario_actual['nombre']}\n"
        f"Email: {usuario_actual['email']}\n"
        f"ID: {usuario_actual['id']}",
        title="Perfil de usuario",
        border_style="green"
    ))

if __name__ == "__main__":
    menu_principal()