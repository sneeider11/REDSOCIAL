import datetime
from rich.console import Console
from rich.panel import Panel
from firebase_admin import db
import questionary

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(contenido, title=titulo, style=estilo, border_style=estilo))

def crear_publicacion(usuario_actual):
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
        "timestamp": datetime.datetime.now().timestamp(),
        "likes": 0,
        "liked_by": {},
        "comentarios": {}
    }
    
    try:
        publicaciones_ref = db.reference('publicaciones')
        publicaciones_ref.push(publicacion_data)
        mostrar_mensaje("Éxito", "¡Publicación creada con éxito!", "green")
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo publicar: {str(e)}")