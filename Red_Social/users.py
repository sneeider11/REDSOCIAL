import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from firebase_admin import db
import questionary

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(Text(contenido, justify="center"), 
                       title=titulo, 
                       style=estilo,
                       border_style=estilo))

def listar_usuarios(usuario_actual):
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
            if usuario_actual and uid == usuario_actual['id']:
                continue
            opcion = f"{user_data.get('nombre', 'Anónimo')} ({user_data.get('email', 'sin email')})"
            opciones.append(opcion)
            usuarios_lista.append({
                'id': uid,
                'nombre': user_data.get('nombre', 'Anónimo'),
                'email': user_data.get('email', 'sin email'),
                'datos': user_data
            })
        
        if not opciones:
            mostrar_mensaje("Info", "No hay otros usuarios registrados", "blue")
            return None
            
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
        mostrar_mensaje("Error", f"No se pudieron listar los usuarios: {str(e)}", "red")
        return None

def buscar_usuarios_por_nombre():
    console.print(Panel("Buscar usuarios", style="blue"))
    
    termino_busqueda = questionary.text("Ingresa el nombre o parte del nombre a buscar:").ask()
    if not termino_busqueda:
        return None
    
    try:
        usuarios_ref = db.reference('usuarios')
        todos_usuarios = usuarios_ref.get() or {}
        
        resultados = []
        for uid, user_data in todos_usuarios.items():
            nombre = user_data.get('nombre', '').lower()
            if termino_busqueda.lower() in nombre:
                resultados.append({
                    'id': uid,
                    'nombre': user_data.get('nombre', 'Anónimo'),
                    'email': user_data.get('email', 'sin email'),
                    'datos': user_data
                })
        
        if not resultados:
            mostrar_mensaje("Info", "No se encontraron usuarios con ese nombre", "blue")
            return None
        
        console.print(Panel(f"Resultados de búsqueda para '{termino_busqueda}'", style="bold blue"))
        
        opciones = [f"{user['nombre']} ({user['email']})" for user in resultados]
        opciones.append("Volver")
        
        seleccion = questionary.select(
            "Seleccione un usuario para ver su perfil:",
            choices=opciones
        ).ask()
        
        if seleccion == "Volver" or not seleccion:
            return None
            
        indice = opciones.index(seleccion)
        return resultados[indice]
        
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo completar la búsqueda: {str(e)}", "red")
        return None

def ver_perfil_usuario(usuario_id):
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

def mostrar_perfil(usuario_actual):
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