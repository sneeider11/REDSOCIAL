import firebase_admin
from firebase_admin import credentials, db
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import datetime
import re  # Para validar correo electrónico
import bcrypt  # Para encriptar contraseñas

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

def es_correo_valido(correo):
    """Verifica si el correo electrónico tiene un formato válido"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, correo))

def encriptar_contraseña(contraseña):
    """Encripta una contraseña usando bcrypt"""
    # Convertir a bytes si es una cadena
    if isinstance(contraseña, str):
        contraseña = contraseña.encode('utf-8')
    # Generar sal y hash
    sal = bcrypt.gensalt()
    hashed = bcrypt.hashpw(contraseña, sal)
    return hashed.decode('utf-8')  # Convertir a string para almacenar

def verificar_contraseña(contraseña_plana, contraseña_hash):
    """Verifica si una contraseña coincide con su hash"""
    # Convertir a bytes si son cadenas
    if isinstance(contraseña_plana, str):
        contraseña_plana = contraseña_plana.encode('utf-8')
    if isinstance(contraseña_hash, str):
        contraseña_hash = contraseña_hash.encode('utf-8')
    # Verificar
    return bcrypt.checkpw(contraseña_plana, contraseña_hash)

# Funciones para comentarios
def agregar_comentario(publicacion_id):
    """Agrega un comentario a una publicación"""
    if not usuario_actual:
        mostrar_mensaje("Error", "Debes iniciar sesión para comentar", "red")
        return False
    
    # Obtener el texto del comentario
    texto_comentario = questionary.text("Escribe tu comentario:").ask()
    if not texto_comentario:
        return False
    
    try:
        # Referencia a la publicación
        pub_ref = db.reference(f'publicaciones/{publicacion_id}')
        publicacion = pub_ref.get()
        
        if not publicacion:
            mostrar_mensaje("Error", "Publicación no encontrada", "red")
            return False
        
        # Crear el comentario
        nuevo_comentario = {
            "contenido": texto_comentario,
            "autor": usuario_actual['nombre'],
            "user_id": usuario_actual['id'],
            "timestamp": datetime.datetime.now().timestamp(),
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Verificar si ya existe la estructura de comentarios
        comentarios = publicacion.get('comentarios', {})
        
        # Generar un ID único para el comentario (timestamp + sufijo aleatorio)
        comentario_id = f"{int(datetime.datetime.now().timestamp())}-{len(comentarios) + 1}"
        comentarios[comentario_id] = nuevo_comentario
        
        # Actualizar la publicación con el nuevo comentario
        pub_ref.update({
            'comentarios': comentarios
        })
        
        mostrar_mensaje("Éxito", "Comentario publicado correctamente", "green")
        return True
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo publicar el comentario: {str(e)}", "red")
        return False

def mostrar_comentarios(publicacion_id, pub_data):
    """Muestra los comentarios de una publicación"""
    comentarios = pub_data.get('comentarios', {})
    
    if not comentarios:
        mostrar_mensaje("Info", "Esta publicación no tiene comentarios", "blue")
        return
    
    # Ordenar comentarios por timestamp
    comentarios_ordenados = sorted(
        comentarios.items(), 
        key=lambda x: x[1].get('timestamp', 0)
    )
    
    console.print(Panel(f"Comentarios de la publicación", style="bold cyan"))
    
    for com_id, com_data in comentarios_ordenados:
        # Formatear fecha
        timestamp = com_data.get('timestamp', 0)
        try:
            fecha = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
        except:
            fecha = com_data.get('fecha', 'Fecha desconocida')
            
        console.print(Panel(
            f"{com_data.get('contenido', 'Sin contenido')}",
            title=f"👤 {com_data.get('autor', 'Anónimo')} • {fecha}",
            border_style="cyan"
        ))

# Funciones para "me gusta"
def dar_me_gusta(publicacion_id):
    """Da me gusta a una publicación y actualiza en Firebase"""
    if not usuario_actual:
        mostrar_mensaje("Error", "Debes iniciar sesión para dar me gusta", "red")
        return False
    
    try:
        # Referencia a la publicación
        pub_ref = db.reference(f'publicaciones/{publicacion_id}')
        publicacion = pub_ref.get()
        
        if not publicacion:
            mostrar_mensaje("Error", "Publicación no encontrada", "red")
            return False
        
        # Verificar si el usuario ya dio me gusta
        liked_by = publicacion.get('liked_by', {})
        
        if usuario_actual['id'] in liked_by:
            # Si ya dio me gusta, lo quitamos
            del liked_by[usuario_actual['id']]
            likes = publicacion.get('likes', 0) - 1
            if likes < 0:
                likes = 0
            mostrar_mensaje("Info", "Has quitado tu me gusta", "blue")
        else:
            # Si no ha dado me gusta, lo añadimos
            liked_by[usuario_actual['id']] = True
            likes = publicacion.get('likes', 0) + 1
            mostrar_mensaje("Éxito", "¡Has dado me gusta a esta publicación!", "green")
        
        # Actualizar publicación
        pub_ref.update({
            'likes': likes,
            'liked_by': liked_by
        })
        
        return True
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo procesar tu reacción: {str(e)}", "red")
        return False

def mostrar_publicacion_con_opciones(pub_id, pub_data):
    """Muestra una publicación con opciones para dar me gusta y comentarios"""
    timestamp = pub_data.get('timestamp', 0)
    try:
        fecha = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m %H:%M")
    except:
        fecha = "Fecha desconocida"
    
    # Determinar si el usuario actual ha dado me gusta
    liked_by = pub_data.get('liked_by', {})
    ha_dado_like = usuario_actual and usuario_actual['id'] in liked_by
    
    # Contador de likes
    likes = pub_data.get('likes', 0)
    
    # Contador de comentarios
    comentarios = pub_data.get('comentarios', {})
    num_comentarios = len(comentarios)
    
    # Texto de likes y comentarios
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
    
    # Validar formato de correo electrónico
    if not es_correo_valido(datos["email"]):
        mostrar_mensaje("Error", "El correo electrónico no tiene un formato válido")
        return
    
    # Validar longitud de contraseña
    if len(datos["contraseña"]) < 8:
        mostrar_mensaje("Error", "La contraseña debe tener al menos 8 caracteres")
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
    
    # Encriptar contraseña antes de almacenar
    contraseña_encriptada = encriptar_contraseña(datos["contraseña"])
    
    nuevo_usuario_ref = usuarios_ref.push({
        "email": datos["email"],
        "nombre": datos["nombre"],
        "contraseña": contraseña_encriptada,
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
            # Verificar contraseña hasheada
            if verificar_contraseña(credenciales["contraseña"], user_data.get('contraseña')):
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

# Funciones de publicaciones (actualizadas para manejar comentarios)
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
        "timestamp": datetime.datetime.now().timestamp(),
        "likes": 0,            # Inicializamos el contador de likes
        "liked_by": {},        # Diccionario para registrar quién ha dado like
        "comentarios": {}      # Diccionario para almacenar comentarios
    }
    
    try:
        publicaciones_ref = db.reference('publicaciones')
        nueva_publicacion_ref = publicaciones_ref.push(publicacion_data)
        mostrar_mensaje("Éxito", "¡Publicación creada con éxito!", "green")
    except Exception as e:
        mostrar_mensaje("Error", f"No se pudo publicar: {str(e)}")

def mostrar_publicaciones():
    """Muestra las publicaciones recientes con opción para dar me gusta y comentar"""
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
        
        while True:
            # Mostrar publicaciones numeradas
            for i, (pub_id, pub_data) in enumerate(publicaciones_ordenadas, 1):
                console.print(f"[bold cyan]{i}.[/bold cyan]", end=" ")
                mostrar_publicacion_con_opciones(pub_id, pub_data)
            
            # Opciones para el usuario
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
                        
                        # Dar/quitar me gusta
                        if dar_me_gusta(pub_id):
                            # Actualizar datos locales para reflejar el cambio
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
                        
                        # Agregar comentario
                        if agregar_comentario(pub_id):
                            # Actualizar datos locales para reflejar el cambio
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
                        
                        # Mostrar comentarios
                        mostrar_comentarios(pub_id, pub_data)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
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
            if usuario_actual and uid == usuario_actual['id']:
                continue  # Saltar el usuario actual
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
    """Muestra las publicaciones de un usuario específico con opción para dar me gusta y comentar"""
    try:
        publicaciones_ref = db.reference('publicaciones')
        
        # Obtenemos todas las publicaciones y filtramos localmente
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
        
        while True:
            # Mostrar publicaciones numeradas
            for i, (pub_id, pub_data) in enumerate(publicaciones_ordenadas, 1):
                console.print(f"[bold cyan]{i}.[/bold cyan]", end=" ")
                mostrar_publicacion_con_opciones(pub_id, pub_data)
            
            # Opciones para el usuario
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
                        
                        # Dar/quitar me gusta
                        if dar_me_gusta(pub_id):
                            # Actualizar datos locales para reflejar el cambio
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
                        
                        # Agregar comentario
                        if agregar_comentario(pub_id):
                            # Actualizar datos locales para reflejar el cambio
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
                        
                        # Mostrar comentarios
                        mostrar_comentarios(pub_id, pub_data)
                    else:
                        mostrar_mensaje("Error", "Número de publicación inválido", "red")
                except ValueError:
                    mostrar_mensaje("Error", "Ingresa un número válido", "red")
            
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