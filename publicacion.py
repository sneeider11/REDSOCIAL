import firebase_admin
from firebase_admin import credentials, db
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import datetime

# Configuración de Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'
})

# Variables globales
usuario_actual = None
console = Console()

# Funciones de utilidad
def mostrar_mensaje(titulo, contenido, estilo="red"):
    """Muestra un mensaje formateado con Rich"""
    console.print(Panel(Text(contenido, justify="center"), 
                       title=titulo, 
                       style=estilo,
                       border_style=estilo))

# Funciones de autenticación
def registrar_usuario():
    """Registra un nuevo usuario en Realtime Database"""
    console.print(Panel("Registro de nuevo usuario", style="blue"))
    
    datos = questionary.form(
        email=questionary.text("Correo electrónico:"),
        nombre=questionary.text("Nombre completo:"),
        contraseña=questionary.password("Contraseña:"),
        confirmar=questionary.password("Confirmar contraseña:")
    ).ask()
    
    if not datos:
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
    
    nuevo_usuario_ref = usuarios_ref.push({
        "email": datos["email"],
        "nombre": datos["nombre"],
        "contraseña": datos["contraseña"],
        "activo": True,
        "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    
    if not credenciales:
        return
    
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
    return True

# Funciones de publicaciones (con solución para el error)
def crear_publicacion():
    """Crea una nueva publicación vinculada al usuario"""
    if not usuario_actual:
        mostrar_mensaje("Error", "Debes iniciar sesión para publicar")
        return
    
    console.print(Panel("Nueva publicación", style="blue"))
    
    contenido = questionary.text("¿Qué quieres compartir hoy?").ask()
    if not contenido:
        return
    
    publicacion_data = {
        "contenido": contenido,
        "autor": usuario_actual['nombre'],
        "user_id": usuario_actual['id'],
        "email": usuario_actual['email'],
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": datetime.datetime.now().timestamp()
    }
    
    try:
        publicaciones_ref = db.reference('publicaciones')
        nueva_publicacion_ref = publicaciones_ref.push(publicacion_data)
        mostrar_mensaje("Éxito", "¡Publicación creada con éxito!", "green")
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo publicar: {str(e)}")

def mostrar_publicaciones():
    """Muestra las publicaciones recientes con manejo de error de índice"""
    try:
        publicaciones_ref = db.reference('publicaciones')
        
        # Intento 1: Obtener ordenado por timestamp (puede fallar sin reglas)
        try:
            publicaciones = publicaciones_ref.order_by_child('timestamp').limit_to_last(10).get()
            publicaciones_ordenadas = sorted(publicaciones.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        except Exception as e:
            # Intento 2: Obtener sin ordenar y ordenar localmente
            mostrar_mensaje("Advertencia", "Optimizando visualización...", "yellow")
            publicaciones = publicaciones_ref.limit_to_last(10).get() or {}
            publicaciones_ordenadas = sorted(publicaciones.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
        if not publicaciones_ordenadas:
            mostrar_mensaje("Info", "No hay publicaciones recientes", "blue")
            return
        
        console.print(Panel("Publicaciones recientes", style="bold blue"))
        
        for pub_id, pub_data in publicaciones_ordenadas:
            timestamp = pub_data.get('timestamp', 0)
            try:
                fecha = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
            except:
                fecha = "Fecha desconocida"
                
            console.print(Panel(
                f"{pub_data.get('contenido', 'Sin contenido')}\n\n"
                f"[dim]👤 {pub_data.get('autor', 'Anónimo')}  •  📅 {fecha}[/dim]",
                border_style="blue"
            ))
            
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudieron cargar las publicaciones: {str(e)}")

# Menús del sistema
def menu_principal():
    """Menú principal de la aplicación"""
    while True:
        console.print(Panel("Red Social con Firebase", style="bold blue"))
        
        opciones = [
            "Iniciar sesión",
            "Registrarse",
            "Salir"
        ]
        
        if usuario_actual:
            opciones.insert(0, "Menú de usuario")
        
        opcion = questionary.select(
            "Seleccione una opción:",
            choices=opciones
        ).ask()
        
        if opcion == "Iniciar sesión":
            if iniciar_sesion():
                menu_usuario()
        elif opcion == "Registrarse":
            registrar_usuario()
        elif opcion == "Menú de usuario":
            menu_usuario()
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
                "Crear publicación",
                "Ver publicaciones",
                "Ver perfil",
                "Cerrar sesión"
            ]
        ).ask()
        
        if opcion == "Crear publicación":
            crear_publicacion()
        elif opcion == "Ver publicaciones":
            mostrar_publicaciones()
        elif opcion == "Ver perfil":
            mostrar_perfil()
        elif opcion == "Cerrar sesión":
            usuario_actual = None
            mostrar_mensaje("Info", "Sesión cerrada correctamente", "blue")
            break

def mostrar_perfil():
    """Muestra los datos del usuario actual"""
    if not usuario_actual:
        return
    
    try:
        usuario_ref = db.reference(f'usuarios/{usuario_actual["id"]}')
        datos_usuario = usuario_ref.get()
        
        console.print(Panel(
            f"Nombre: {datos_usuario.get('nombre', 'Desconocido')}\n"
            f"Email: {datos_usuario.get('email', 'Desconocido')}\n"
            f"Registrado el: {datos_usuario.get('fecha_registro', 'Desconocido')}",
            title="Tu perfil",
            border_style="green"
        ))
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo cargar el perfil: {str(e)}")

if __name__ == "__main__":
    menu_principal()
