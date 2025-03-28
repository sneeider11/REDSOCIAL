from rich.console import Console
from rich.panel import Panel
from firebase_admin import db

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(contenido, title=titulo, style=estilo, border_style=estilo))

def dar_me_gusta(publicacion_id, usuario_actual):
    if not usuario_actual:
        mostrar_mensaje("Error", "Debes iniciar sesión para dar me gusta", "red")
        return False
    
    try:
        pub_ref = db.reference(f'publicaciones/{publicacion_id}')
        publicacion = pub_ref.get()
        
        if not publicacion:
            mostrar_mensaje("Error", "Publicación no encontrada", "red")
            return False
        
        liked_by = publicacion.get('liked_by', {})
        
        if usuario_actual['id'] in liked_by:
            del liked_by[usuario_actual['id']]
            likes = publicacion.get('likes', 0) - 1
            if likes < 0:
                likes = 0
            mostrar_mensaje("Info", "Has quitado tu me gusta", "blue")
        else:
            liked_by[usuario_actual['id']] = True
            likes = publicacion.get('likes', 0) + 1
            mostrar_mensaje("Éxito", "¡Has dado me gusta a esta publicación!", "green")
        
        pub_ref.update({
            'likes': likes,
            'liked_by': liked_by
        })
        
        return True
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo procesar tu reacción: {str(e)}", "red")
        return False