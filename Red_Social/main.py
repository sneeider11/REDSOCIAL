import firebase_admin
from firebase_admin import credentials, db
import questionary
from rich.console import Console
from rich.panel import Panel  # Added missing import
from auth import registrar_usuario, iniciar_sesion
from posts import crear_publicacion
from comments import agregar_comentario, mostrar_comentarios
from likes import dar_me_gusta
from users import listar_usuarios, buscar_usuarios_por_nombre, ver_perfil_usuario, mostrar_perfil
from display import mostrar_mensaje, mostrar_publicacion_con_opciones

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'
})

console = Console()
usuario_actual = None

def mostrar_publicaciones(usuario_actual):
    try:
        publicaciones_ref = db.reference('publicaciones')
        publicaciones = publicaciones_ref.order_by_child('timestamp').limit_to_last(10).get()
        
        if not publicaciones:
            mostrar_mensaje("Info", "No hay publicaciones recientes", "blue")
            return
        
        publicaciones_ordenadas = sorted(publicaciones.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
        console.print(Panel("Publicaciones recientes", style="bold blue"))
        
        while True:
            for i, (pub_id, pub_data) in enumerate(publicaciones_ordenadas, 1):
                console.print(f"[bold cyan]{i}.[/bold cyan]", end=" ")
                mostrar_publicacion_con_opciones(pub_id, pub_data, usuario_actual)
            
            opciones = ["Volver al menú"]
            if usuario_actual:
                opciones.insert(0, "Comentar una publicación")
                opciones.insert(0, "Ver comentarios de una publicación")
                opciones.insert(0, "Dar/quitar me gusta a una publicación")
            
            accion = questionary.select(
                "¿Qué deseas hacer?",
                choices=opciones
            ).ask()
            
            if accion == "Volver al menú":
                break
            elif accion == "Dar/quitar me gusta a una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación a la que quieres dar/quitar me gusta:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        pub_data = publicaciones_ordenadas[indice][1]
                        
                        if dar_me_gusta(pub_id, usuario_actual):
                            pub_data_updated = db.reference(f'publicaciones/{pub_id}').get()
                            if pub_data_updated:
                                publicaciones_ordenadas[indice] = (pub_id, pub_data_updated)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
            elif accion == "Comentar una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación a la que quieres comentar:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        
                        if agregar_comentario(pub_id, usuario_actual):
                            pub_data_updated = db.reference(f'publicaciones/{pub_id}').get()
                            if pub_data_updated:
                                publicaciones_ordenadas[indice] = (pub_id, pub_data_updated)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
            elif accion == "Ver comentarios de una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación cuyos comentarios quieres ver:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        pub_data = publicaciones_ordenadas[indice][1]
                        
                        mostrar_comentarios(pub_id, pub_data)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudieron cargar las publicaciones: {str(e)}")

def mostrar_publicaciones_usuario(usuario_id, usuario_actual):
    try:
        publicaciones_ref = db.reference('publicaciones')
        mostrar_mensaje("Info", "Cargando publicaciones...", "blue")
        todas_publicaciones = publicaciones_ref.get() or {}
        
        publicaciones_usuario = []
        for pub_id, pub_data in todas_publicaciones.items():
            if pub_data.get('user_id') == usuario_id:
                publicaciones_usuario.append((pub_id, pub_data))
        
        if not publicaciones_usuario:
            mostrar_mensaje("Info", "Este usuario no tiene publicaciones", "blue")
            return
            
        publicaciones_ordenadas = sorted(publicaciones_usuario, key=lambda x: x[1].get('timestamp', 0), reverse=True)
        
        console.print(Panel(f"Publicaciones del usuario", style="bold blue"))
        
        while True:
            for i, (pub_id, pub_data) in enumerate(publicaciones_ordenadas, 1):
                console.print(f"[bold cyan]{i}.[/bold cyan]", end=" ")
                mostrar_publicacion_con_opciones(pub_id, pub_data, usuario_actual)
            
            opciones = ["Volver"]
            if usuario_actual:
                opciones.insert(0, "Comentar una publicación")
                opciones.insert(0, "Ver comentarios de una publicación")
                opciones.insert(0, "Dar/quitar me gusta a una publicación")
            
            accion = questionary.select(
                "¿Qué deseas hacer?",
                choices=opciones
            ).ask()
            
            if accion == "Volver":
                break
            elif accion == "Dar/quitar me gusta a una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación a la que quieres dar/quitar me gusta:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        pub_data = publicaciones_ordenadas[indice][1]
                        
                        if dar_me_gusta(pub_id, usuario_actual):
                            pub_data_updated = db.reference(f'publicaciones/{pub_id}').get()
                            if pub_data_updated:
                                publicaciones_ordenadas[indice] = (pub_id, pub_data_updated)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
                    
            elif accion == "Comentar una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación a la que quieres comentar:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        
                        if agregar_comentario(pub_id, usuario_actual):
                            pub_data_updated = db.reference(f'publicaciones/{pub_id}').get()
                            if pub_data_updated:
                                publicaciones_ordenadas[indice] = (pub_id, pub_data_updated)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
            elif accion == "Ver comentarios de una publicación":
                indice = questionary.text(
                    "Ingresa el número de la publicación cuyos comentarios quieres ver:"
                ).ask()
                
                try:
                    indice = int(indice) - 1
                    if 0 <= indice < len(publicaciones_ordenadas):
                        pub_id = publicaciones_ordenadas[indice][0]
                        pub_data = publicaciones_ordenadas[indice][1]
                        
                        mostrar_comentarios(pub_id, pub_data)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudieron cargar las publicaciones: {str(e)}")

def manejar_usuario_seleccionado(usuario_seleccionado, usuario_actual):
    datos_usuario = ver_perfil_usuario(usuario_seleccionado['id'])
    if not datos_usuario:
        return
        
    while True:
        opcion = questionary.select(
            "¿Qué deseas hacer?",
            choices=[
                "Ver publicaciones de este usuario",
                "Seleccionar otro usuario",
                "Volver al menú de usuarios"
            ]
        ).ask()
        
        if opcion == "Ver publicaciones de este usuario":
            mostrar_publicaciones_usuario(usuario_seleccionado['id'], usuario_actual)
        elif opcion == "Seleccionar otro usuario":
            break
        elif opcion == "Volver al menú de usuarios":
            return

def menu_ver_usuarios(usuario_actual):
    while True:
        opcion = questionary.select(
            "Explorar usuarios - Seleccione una opción:",
            choices=[
                "Listar todos los usuarios",
                "Buscar usuario por nombre",
                "Volver al menú principal"
            ]
        ).ask()
        
        if opcion == "Listar todos los usuarios":
            usuario_seleccionado = listar_usuarios(usuario_actual)
            if usuario_seleccionado:
                manejar_usuario_seleccionado(usuario_seleccionado, usuario_actual)
        elif opcion == "Buscar usuario por nombre":
            usuario_seleccionado = buscar_usuarios_por_nombre()
            if usuario_seleccionado:
                manejar_usuario_seleccionado(usuario_seleccionado, usuario_actual)
        elif opcion == "Volver al menú principal":
            break

def menu_usuario(usuario_actual):
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
            crear_publicacion(usuario_actual)
        elif opcion == "Ver publicaciones recientes":
            mostrar_publicaciones(usuario_actual)
        elif opcion == "Ver mi perfil":
            mostrar_perfil(usuario_actual)
        elif opcion == "Explorar otros usuarios":
            menu_ver_usuarios(usuario_actual)
        elif opcion == "Cerrar sesión":
            usuario_actual = None
            mostrar_mensaje("Info", "Sesión cerrada correctamente", "blue")
            return None
    return usuario_actual

def menu_principal():
    global usuario_actual
    
    while True:
        console.print(Panel("GuaroGamers", style="bold blue"))
        
        opciones = [
            "Iniciar sesión",
            "Registrarse",
            "Salir"
        ]
        
        if usuario_actual:
            opciones.insert(0, "Menú de usuario")
            opciones.insert(1, "Buscar usuarios")
        
        opcion = questionary.select(
            "Seleccione una opción:",
            choices=opciones
        ).ask()
        
        if opcion == "Iniciar sesión":
            usuario_actual = iniciar_sesion(usuario_actual)
            if usuario_actual:
                usuario_actual = menu_usuario(usuario_actual)
        elif opcion == "Registrarse":
            registrar_usuario()
        elif opcion == "Menú de usuario":
            usuario_actual = menu_usuario(usuario_actual)
        elif opcion == "Buscar usuarios":
            usuario_seleccionado = buscar_usuarios_por_nombre()
            if usuario_seleccionado:
                manejar_usuario_seleccionado(usuario_seleccionado, usuario_actual)
        elif opcion == "Salir":
            break

if __name__ == "__main__":
    menu_principal()