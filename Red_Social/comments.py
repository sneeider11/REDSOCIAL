import datetime
from rich.console import Console
from rich.panel import Panel
from firebase_admin import db
import questionary

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(contenido, title=titulo, style=estilo, border_style=estilo))

def agregar_comentario(publicacion_id, usuario_actual):
    if not usuario_actual:
        mostrar_mensaje("Error", "Debes iniciar sesión para comentar", "red")
        return False
    
    texto_comentario = questionary.text("Escribe tu comentario:").ask()
    if not texto_comentario:
        return False
    
    try:
        pub_ref = db.reference(f'publicaciones/{publicacion_id}')
        publicacion = pub_ref.get()
        
        if not publicacion:
            mostrar_mensaje("Error", "Publicación no encontrada", "red")
            return False
        
        nuevo_comentario = {
            "contenido": texto_comentario,
            "autor": usuario_actual['nombre'],
            "user_id": usuario_actual['id'],
            "timestamp": datetime.datetime.now().timestamp(),
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        comentarios = publicacion.get('comentarios', {})
        comentario_id = f"{int(datetime.datetime.now().timestamp())}-{len(comentarios) + 1}"
        comentarios[comentario_id] = nuevo_comentario
        
        pub_ref.update({
            'comentarios': comentarios
        })
        
        mostrar_mensaje("Éxito", "Comentario publicado correctamente", "green")
        return True
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo publicar el comentario: {str(e)}", "red")
        return False

def mostrar_comentarios(publicacion_id, pub_data):
    comentarios = pub_data.get('comentarios', {})
    
    if not comentarios:
        mostrar_mensaje("Info", "Esta publicación no tiene comentarios", "blue")
        return
    
    comentarios_ordenados = sorted(
        comentarios.items(), 
        key=lambda x: x[1].get('timestamp', 0)
    )
    
    console.print(Panel(f"Comentarios de la publicación", style="bold cyan"))
    
    for com_id, com_data in comentarios_ordenados:
        try:
            fecha = datetime.datetime.fromtimestamp(com_data.get('timestamp', 0)).strftime("%d/%m %H:%M")
        except:
            fecha = com_data.get('fecha', 'Fecha desconocida')
            
        console.print(Panel(
            f"{com_data.get('contenido', 'Sin contenido')}",
            title=f"👤 {com_data.get('autor', 'Anónimo')} • {fecha}",
            border_style="cyan"
        ))