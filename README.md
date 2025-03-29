#Guarohub
📥 Instalación
Clona el repositorio:
https://github.com/sneeider11/REDSOCIAL.git


pip install -r requirements.txt
🔥 Configuración Firebase
Crea un proyecto en Firebase Console.

Ve a Configuración del proyecto > Cuentas de servicio y descarga serviceAccountKey.json.

Coloca el archivo en la carpeta src/.

¡Listo! La base de datos estará conectada.

⚠️ Importante: Añade serviceAccountKey.json al .gitignore para no exponer credenciales.

🕹️ Cómo Usar
Ejecuta la aplicación:

python src/main.py
Menú Principal:


1. Registrarse  
2. Iniciar Sesión  
3. Ver Publicaciones  
4. Buscar Usuarios  
5. Salir  
Flujo Básico:
Regístrate con nombre y contraseña.

Publica tus logros:

python

"¡Acabo de completar el Dark Souls sin morir! 🏆"  
Interactúa con "Me gusta" y comentarios.

🚀 Funcionalidades Clave
Registro seguro con encriptación bcrypt.

Publicaciones en tiempo real almacenadas en Firebase.

Sistema de likes y comentarios.

Búsqueda de usuarios por nombre.

Perfiles personalizados con historial de publicaciones.

📂 Estructura del Proyecto
GameHub/  
├── src/  
│   ├── auth.py           # Autenticación y registro  
│   ├── posts.py          # Lógica de publicaciones  
│   ├── comments.py       # Gestión de comentarios  
│   ├── likes.py          # Sistema de "Me gusta"  
│   ├── users.py          # Perfiles y búsqueda  
│   ├── main.py           # Punto de entrada  
│   └── serviceAccountKey.json  # Credenciales Firebase  
├── docs/                 # Documentación del proceso Scrum  
├── screenshots/          # Capturas de la interfaz  
└── README.md  
🤝 Contribución
¡Tu ayuda es bienvenida! Sigue estos pasos:

Haz un fork del repositorio.

Crea una rama:



git checkout -b nueva-funcionalidad
Haz tus cambios y haz commit:



git commit -m "feat: añadí X funcionalidad"
Envía un Pull Request.

📜 Licencia
Este proyecto usa la licencia MIT.

¡A jugar se dijo! 🎮✨

Usa la extensión Firebase Explorer en VSCode para monitorear datos en tiempo real.

Ejecuta python -m pytest tests/ para correr pruebas (si las añades).

¡Listo para dominar la red social gamer! 🚀



DOCUMENTACION EN WORD

https://docs.google.com/document/d/1P-PS6mPgpzjpT8vcJN4MM6PIuD6oHmP4DMG7v_3QLdU/edit?usp=sharing

PRESENTACION
https://gamma.app/docs/CENTRO-ENTRENAMIENTO-INTENSIVO-BOOTCAMP-CampusLands-c8kgatflnm0pdsm

https://1drv.ms/p/c/74f634baa07751f9/EVaVx38iEBJBozHhOT-P36gBjX07zLzJeRDpTkKQlKQ1pA?e=Wukx2X


