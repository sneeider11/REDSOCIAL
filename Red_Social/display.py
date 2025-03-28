import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def mostrar_mensaje(titulo, contenido, estilo="red"):
    console.print(Panel(Text(contenido, justify="center"), 
                       title=titulo, 
                       style=estilo,
                       border_style=estilo))

def mostrar_publicacion_con_opciones(pub_id, pub_data, usuario_actual):
    timestamp = pub_data.get('timestamp', 0)
    try:
        fecha = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
    except:
        fecha = "Fecha desconocida"
    
    liked_by = pub_data.get('liked_by', {})
    ha_dado_like = usuario_actual and usuario_actual['id'] in liked_by
    
    likes = pub_data.get('likes', 0)
    comentarios = pub_data.get('comentarios', {})
    num_comentarios = len(comentarios)
    
    texto_likes = f"❤️ {likes}" if likes else "Sin me gusta"
    if ha_dado_like:
        texto_likes += " (Te gusta)"
    
    texto_comentarios = f"💬 {num_comentarios} comentarios" if num_comentarios else "Sin comentarios"
    
    console.print(Panel(
        f"{pub_data.get('contenido', 'Sin contenido')}\n\n"
        f"[dim]👤 {pub_data.get('autor', 'Anónimo')}  •  📅 {fecha}[/dim]\n"
        f"[bold]{texto_likes}[/bold] | [bold cyan]{texto_comentarios}[/bold cyan]",
        border_style="blue"
    ))
    
    return ha_dado_like, num_comentarios