import firebase_admin
from firebase_admin import credentials, db
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary
from questionary import Style as QStyle

# Configuración de Firebase
def inicializar_firebase():
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'
        })
        return db.reference()
    except Exception as e:
        console.print(Panel(f"[red]Error al conectar con Firebase: {str(e)}[/red]"))
        return None

# Configuración de estilos
console = Console()
estilo_personalizado = QStyle([
    ('qmark', 'fg:#00ffff bold'),
    ('question', 'fg:#ffffff bold'),
    ('answer', 'fg:#00ff7f bold'),
    ('selected', 'fg:#ff79c6'),
    ('pointer', 'fg:#ff79c6 bold'),
])

def mostrar_menu_principal():
    """Muestra el menú principal"""
    while True:
        opcion = questionary.select(
            "🔍 VISOR DE USUARIOS Y PUBLICACIONES",
            choices=[
                "👥 Listar todos los usuarios",
                "👤 Ver perfil con publicaciones",
                "🚪 Salir"
            ],
            style=estilo_personalizado
        ).ask()

        if opcion == "👥 Listar todos los usuarios":
            listar_usuarios()
        elif opcion == "👤 Ver perfil con publicaciones":
            ver_perfil_con_publicaciones()
        elif opcion == "🚪 Salir":
            console.print(Panel("[bold green]¡Hasta pronto![/bold green]", style="green"))
            break

def listar_usuarios():
    """Muestra todos los usuarios registrados"""
    try:
        usuarios = ref.child('usuarios').get()
        
        if not usuarios:
            console.print(Panel("No hay usuarios registrados", style="red"))
            return

        tabla = Table(title="👥 USUARIOS REGISTRADOS")
        tabla.add_column("Nombre", style="magenta")
        tabla.add_column("Email", style="cyan")

        for datos_usuario in usuarios.values():
            tabla.add_row(
                datos_usuario.get('nombre', 'Sin nombre'),
                datos_usuario.get('email', 'Sin email')
            )

        console.print(tabla)
        console.print(f"\n[dim]Total usuarios: {len(usuarios)}[/dim]")
    except Exception as e:
        console.print(Panel(f"[red]Error al cargar usuarios: {str(e)}[/red]"))

def ver_perfil_con_publicaciones():
    """Muestra el perfil completo con sus publicaciones"""
    try:
        usuarios = ref.child('usuarios').get()
        
        if not usuarios:
            console.print(Panel("No hay usuarios registrados", style="red"))
            return

        # Selección de usuario
        opciones_usuario = [f"{u['nombre']} ({u['email']})" for u in usuarios.values()]
        seleccion = questionary.select(
            "Seleccione un usuario:",
            choices=opciones_usuario,
            style=estilo_personalizado
        ).ask()

        id_usuario = next(uid for uid, u in usuarios.items() if f"{u['nombre']} ({u['email']})" == seleccion)
        datos_usuario = usuarios[id_usuario]

        # Mostrar información del perfil
        console.print(Panel(
            f"[bold]👤 {datos_usuario.get('nombre', 'N/A')}[/bold]\n"
            f"📧 [cyan]{datos_usuario.get('email', 'N/A')}[/cyan]\n"
            f"📝 [yellow]{datos_usuario.get('bio', 'Sin biografía')}[/yellow]",
            title="PERFIL DE USUARIO",
            border_style="blue"
        ))

        # Obtener publicaciones con método alternativo
        try:
            # Primero intentamos con el método indexado (más eficiente)
            publicaciones = ref.child('publicaciones').order_by_child('autor').equal_to(id_usuario).get() or {}
        except:
            try:
                # Método alternativo si falla el indexado (menos eficiente pero funciona)
                todas_publicaciones = ref.child('publicaciones').get() or {}
                publicaciones = {k: v for k, v in todas_publicaciones.items() if v.get('autor') == id_usuario}
            except Exception as e:
                console.print(Panel(f"[yellow]Advertencia: {str(e)}[/yellow]"))
                publicaciones = {}

        # Mostrar publicaciones
        if publicaciones:
            console.print(Panel("📝 PUBLICACIONES", style="bold green"))
            for pub_id, pub in publicaciones.items():
                console.print(f"• {pub.get('contenido', 'Sin contenido')}")
                console.print(f"  [dim]{pub.get('fecha', 'Sin fecha')}[/dim]\n")
        else:
            console.print(Panel("Este usuario no tiene publicaciones", style="yellow"))

    except Exception as e:
        console.print(Panel(f"[red]Error: {str(e)}[/red]"))

if __name__ == "__main__":
    ref = inicializar_firebase()
    if ref:
        console.print(Panel.fit(
            "🔍 VISOR DE USUARIOS - FIREBASE",
            subtitle="Conectado a la base de datos en tiempo real",
            style="bold blue"
        ))
        mostrar_menu_principal()
