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

# Funciones de publicaciones (actualizadas para manejar las reglas)
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
    """Muestra las publicaciones recientes con manejo de reglas de Firebase"""
    try:
        publicaciones_ref = db.reference('publicaciones')
        
        # Usamos el índice timestamp que está definido en las reglas
        publicaciones = publicaciones_ref.order_by_child('timestamp').limit_to_last(10).get()
        
        if not publicaciones:
            mostrar_mensaje("Info", "No hay publicaciones recientes", "blue")
            return
        
        # Convertimos a lista y ordenamos (por si acaso)
        publicaciones_ordenadas = sorted(publicaciones.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
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

# Funciones para ver usuarios y sus publicaciones (actualizadas)
def listar_usuarios():
    """Lista todos los usuarios registrados"""
    try:
        usuarios_ref = db.reference('usuarios')
        usuarios = usuarios_ref.get() or {}
        
        if not usuarios:
            mostrar_mensaje("Info", "No hay usuarios registrados", "blue")
            return None
        
        console.print(Panel("Usuarios registrados", style="bold blue"))
        
        opciones = []
        usuarios_lista = []
        for uid, user_data in usuarios.items():
            if uid == usuario_actual['id']:
                continue  # Saltar el usuario actual
            opcion = f"{user_data.get('nombre', 'Anónimo')} ({user_data.get('email', 'sin email')})"
            opciones.append(opcion)
            usuarios_lista.append({
                'id': uid,
                'nombre': user_data.get('nombre', 'Anónimo'),
                'email': user_data.get('email', 'sin email'),
                'datos': user_data
            })
        
        # Agregar opción para volver
        opciones.append("Volver")
        
        seleccion = questionary.select(
            "Seleccione un usuario para ver su perfil:",
            choices=opciones
        ).ask()
        
        if seleccion == "Volver" or not seleccion:
            return None
            
        indice = opciones.index(seleccion)
        return usuarios_lista[indice]
        
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudieron listar los usuarios: {str(e)}")
        return None

def ver_perfil_usuario(usuario_id):
    """Muestra el perfil de un usuario específico"""
    try:
        usuario_ref = db.reference(f'usuarios/{usuario_id}')
        datos_usuario = usuario_ref.get()
        
        if not datos_usuario:
            mostrar_mensaje("Error", "Usuario no encontrado")
            return
            
        console.print(Panel(
            f"Nombre: {datos_usuario.get('nombre', 'Desconocido')}\n"
            f"Email: {datos_usuario.get('email', 'Desconocido')}\n"
            f"Registrado el: {datos_usuario.get('fecha_registro', 'Desconocido')}",
            title=f"Perfil de {datos_usuario.get('nombre', 'Desconocido')}",
            border_style="green"
        ))
        
        return datos_usuario
        
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo cargar el perfil: {str(e)}")
        return None

def mostrar_publicaciones_usuario(usuario_id):
    """Muestra las publicaciones de un usuario específico (actualizado para manejar reglas)"""
    try:
        publicaciones_ref = db.reference('publicaciones')
        
        # Obtenemos todas las publicaciones y filtramos localmente
        # (porque no tenemos índice en user_id según las reglas)
        mostrar_mensaje("Info", "Cargando publicaciones...", "blue")
        todas_publicaciones = publicaciones_ref.get() or {}
        
        publicaciones_usuario = []
        for pub_id, pub_data in todas_publicaciones.items():
            if pub_data.get('user_id') == usuario_id:
                publicaciones_usuario.append((pub_id, pub_data))
        
        if not publicaciones_usuario:
            mostrar_mensaje("Info", "Este usuario no tiene publicaciones", "blue")
            return
            
        # Ordenamos por timestamp localmente
        publicaciones_ordenadas = sorted(publicaciones_usuario, key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
        console.print(Panel(f"Publicaciones del usuario", style="bold blue"))
        
        for pub_id, pub_data in publicaciones_ordenadas:
            timestamp = pub_data.get('timestamp', 0)
            try:
                fecha = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
            except:
                fecha = "Fecha desconocida"
                
            console.print(Panel(
                f"{pub_data.get('contenido', 'Sin contenido')}\n\n"
                f"[dim]📅 {fecha}[/dim]",
                border_style="blue"
            ))
            
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudieron cargar las publicaciones: {str(e)}")

def menu_ver_usuarios():
    """Menú para explorar otros usuarios"""
    while True:
        usuario_seleccionado = listar_usuarios()
        if not usuario_seleccionado:
            break
            
        datos_usuario = ver_perfil_usuario(usuario_seleccionado['id'])
        if not datos_usuario:
            continue
            
        opcion = questionary.select(
            "¿Qué deseas hacer?",
            choices=[
                "Ver publicaciones de este usuario",
                "Seleccionar otro usuario",
                "Volver al menú principal"
            ]
        ).ask()
        
        if opcion == "Ver publicaciones de este usuario":
            mostrar_publicaciones_usuario(usuario_seleccionado['id'])
        elif opcion == "Volver al menú principal":
            break

# Funciones de perfil
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
                "Ver publicaciones recientes",
                "Ver mi perfil",
                "Explorar otros usuarios",
                "Cerrar sesión"
            ]
        ).ask()
        
        if opcion == "Crear publicación":
            crear_publicacion()
        elif opcion == "Ver publicaciones recientes":
            mostrar_publicaciones()
        elif opcion == "Ver mi perfil":
            mostrar_perfil()
        elif opcion == "Explorar otros usuarios":
            menu_ver_usuarios()
        elif opcion == "Cerrar sesión":
            usuario_actual = None
            mostrar_mensaje("Info", "Sesión cerrada correctamente", "blue")
            break

if __name__ == "__main__":
    menu_principal()
