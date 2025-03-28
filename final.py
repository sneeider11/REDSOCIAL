import firebase_admin
from firebase_admin import credentials, db
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary
from questionary import Style as QStyle
from datetime import datetime

# Configuración Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'
})
ref = db.reference()

# Estilos
console = Console()
custom_style = QStyle([
    ('qmark', 'fg:#00ffff bold'),
    ('question', 'fg:#ffffff bold'),
    ('answer', 'fg:#00ff7f bold'),
    ('selected', 'fg:#ff79c6'),
    ('pointer', 'fg:#ff79c6 bold'),
])

def mostrar_menu_principal():
    """Menú principal interactivo simplificado"""
    while True:
        opcion = questionary.select(
            "🌟 ADMINISTRADOR DE RED SOCIAL",
            choices=[
                "👥 Listar usuarios",
                "👤 Ver perfil",
                "📝 Crear publicación",
                "✏️ Editar perfil",
                "🚪 Salir"
            ],
            style=custom_style
        ).ask()

        if opcion == "👥 Listar usuarios":
            listar_usuarios()
        elif opcion == "👤 Ver perfil":
            ver_perfil_completo()
        elif opcion == "📝 Crear publicación":
            crear_publicacion()
        elif opcion == "✏️ Editar perfil":
            editar_perfil()
        elif opcion == "🚪 Salir":
            console.print(Panel("[bold green]✅ Sesión finalizada[/bold green]"))
            break

def listar_usuarios():
    """Muestra lista simplificada de usuarios"""
    usuarios = ref.child('usuarios').get()
    
    if not usuarios:
        console.print(Panel("No hay usuarios registrados", style="red"))
        return

    tabla = Table(title="👥 LISTA DE USUARIOS")
    tabla.add_column("Nombre", style="magenta")
    tabla.add_column("Email", style="green")

    for user_data in usuarios.values():
        tabla.add_row(
            user_data.get('nombre', 'Sin nombre'),
            user_data.get('email', 'Sin email')
        )

    console.print(tabla)

def ver_perfil_completo():
    """Muestra perfil simplificado"""
    usuarios = ref.child('usuarios').get()
    
    if not usuarios:
        console.print(Panel("No hay usuarios registrados", style="red"))
        return

    # Selección de usuario
    opciones = [f"{u['nombre']} ({u['email']})" for u in usuarios.values()]
    seleccion = questionary.select(
        "Seleccione un usuario:",
        choices=opciones,
        style=custom_style
    ).ask()

    user_id = next(uid for uid, u in usuarios.items() if f"{u['nombre']} ({u['email']})" == seleccion)
    perfil = usuarios[user_id]

    # Obtener publicaciones
    try:
        publicaciones = ref.child('publicaciones').order_by_child('autor').equal_to(user_id).get() or {}
    except Exception as e:
        console.print(Panel(
            f"⚠️ Error al cargar publicaciones: {str(e)}",
            style="yellow"
        ))
        publicaciones = {}

    # Mostrar información básica del perfil
    console.print(Panel.fit(
        f"[bold]👤 {perfil.get('nombre', 'N/A')}[/bold]\n"
        f"[cyan]Email:[/cyan] {perfil.get('email', 'N/A')}\n"
        f"[cyan]Biografía:[/cyan] {perfil.get('bio', 'No especificada')}",
        title="PERFIL DE USUARIO",
        border_style="blue"
    ))

    # Mostrar publicaciones simplificadas
    if publicaciones:
        console.print(Panel("📝 PUBLICACIONES", style="bold"))
        for pub in publicaciones.values():
            console.print(f"• {pub.get('contenido', 'Sin contenido')}")
            console.print(f"  [dim]{pub.get('fecha', 'Sin fecha')}[/dim]\n")
    else:
        console.print(Panel("Este usuario no tiene publicaciones", style="yellow"))

def crear_publicacion():
    """Crea una nueva publicación"""
    usuarios = ref.child('usuarios').get()
    
    if not usuarios:
        console.print(Panel("No hay usuarios registrados", style="red"))
        return

    # Selección de usuario
    opciones = [f"{u['nombre']} ({u['email']})" for u in usuarios.values()]
    seleccion = questionary.select(
        "Para qué usuario es la publicación:",
        choices=opciones,
        style=custom_style
    ).ask()

    user_id = next(uid for uid, u in usuarios.items() if f"{u['nombre']} ({u['email']})" == seleccion)
    
    contenido = questionary.text(
        "Contenido de la publicación:",
        validate=lambda text: True if text else "El contenido no puede estar vacío",
        style=custom_style
    ).ask()

    try:
        nueva_pub = {
            'autor': user_id,
            'contenido': contenido,
            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        ref.child('publicaciones').push(nueva_pub)
        console.print(Panel("✅ Publicación creada!", style="green"))
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))

def editar_perfil():
    """Edición básica de perfil"""
    usuarios = ref.child('usuarios').get()
    
    if not usuarios:
        console.print(Panel("No hay usuarios para editar", style="red"))
        return

    # Selección de usuario
    opciones = [f"{u['nombre']} ({u['email']})" for u in usuarios.values()]
    seleccion = questionary.select(
        "Seleccione usuario a editar:",
        choices=opciones,
        style=custom_style
    ).ask()

    user_id = next(uid for uid, u in usuarios.items() if f"{u['nombre']} ({u['email']})" == seleccion)
    usuario_actual = usuarios[user_id]

    # Formulario simplificado
    nuevos_datos = questionary.form(
        nombre=questionary.text("Nombre:", default=usuario_actual.get('nombre', '')),
        email=questionary.text("Email:", default=usuario_actual.get('email', '')),
        bio=questionary.text("Biografía:", default=usuario_actual.get('bio', ''))
    ).ask(style=custom_style)

    try:
        ref.child('usuarios').child(user_id).update(nuevos_datos)
        console.print(Panel("✅ Perfil actualizado!", style="green"))
    except Exception as e:
        console.print(Panel(f"❌ Error: {e}", style="red"))

if __name__ == "__main__":
    console.print(Panel.fit(
        "🌟 ADMINISTRADOR DE RED SOCIAL",
        style="bold blue"
    ))
    mostrar_menu_principal()
