from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, TextArea
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from rich.panel import Panel
from rich.text import Text
import datetime
import firebase_admin
from firebase_admin import credentials, db
import json
import os

class PublicacionWidget(Static):
    def __init__(self, contenido: str, autor: str, fecha: str):
        super().__init__()
        self.contenido = contenido
        self.autor = autor
        self.fecha = fecha

    def render(self) -> Panel:
        return Panel(
            Text.from_markup(
                f"{self.contenido}\n\n"
                f"[dim]👤 {self.autor}  •  📅 {self.fecha}[/dim]"
            ),
            border_style="blue",
            padding=(1, 2)
        )

class RedSocialMinimal(App):
    CSS = """
    Screen {
        background: #1a1a1a;
    }
    Header {
        background: #004080;
        color: white;
    }
    #editor {
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        with Container():
            with Vertical():
                yield TextArea(id="editor")
                with Horizontal():
                    yield Button("Publicar", variant="primary", id="publicar")
                    yield Button("Limpiar", variant="default", id="limpiar")
                yield ScrollableContainer(id="feed")

    def on_mount(self) -> None:
        self.query_one("#editor", TextArea).placeholder = "Escribe tu publicación..."
        
        # Inicializar Firebase con tu configuración
        try:
            # Asegúrate de tener el archivo serviceAccountKey.json en el mismo directorio
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://redsocial-9a347-default-rtdb.firebaseio.com/'
            })
            self.ref = db.reference('/publicaciones')
            self.cargar_publicaciones()
        except FileNotFoundError:
            self.mostrar_error("No se encontró serviceAccountKey.json")
        except Exception as e:
            self.mostrar_error(f"Error al conectar con Firebase: {str(e)}")

    def cargar_publicaciones(self):
        try:
            publicaciones_fb = self.ref.get() or {}
            self.publicaciones = []
            
            # Convertir el diccionario de Firebase a una lista ordenada
            if publicaciones_fb:
                # Ordenar por timestamp si existe, o por clave si no
                items = sorted(
                    publicaciones_fb.items(),
                    key=lambda x: x[1].get('timestamp', float(x[0])),
                    reverse=True
                )
                
                for _, pub in items:
                    self.publicaciones.append((
                        pub.get('contenido', ''),
                        pub.get('autor', 'Anónimo'),
                        pub.get('fecha', 'Desconocida')
                    ))
            
            self.actualizar_feed()
        except Exception as e:
            self.mostrar_error(f"Error al cargar publicaciones: {str(e)}")

    def mostrar_error(self, mensaje):
        self.notify(mensaje, title="Error", severity="error")

    def actualizar_feed(self):
        feed = self.query_one("#feed", ScrollableContainer)
        feed.remove_children()
        for contenido, autor, fecha in self.publicaciones:
            feed.mount(PublicacionWidget(contenido, autor, fecha))

    @on(Button.Pressed, "#publicar")
    def publicar(self):
        editor = self.query_one("#editor", TextArea)
        contenido = editor.text.strip()
        if contenido:
            try:
                nueva_publicacion = {
                    "contenido": contenido,
                    "autor": "Tú",  # Puedes cambiar esto por un sistema de autenticación
                    "fecha": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "timestamp": datetime.datetime.now().timestamp()
                }
                
                # Guardar en Firebase
                self.ref.push(nueva_publicacion)
                
                # Actualizar localmente (opcional, ya que cargaremos de Firebase)
                self.publicaciones.insert(0, (
                    contenido,
                    "Tú",
                    datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                ))
                self.actualizar_feed()
                editor.text = ""
                
            except Exception as e:
                self.mostrar_error(f"Error al publicar: {str(e)}")

    @on(Button.Pressed, "#limpiar")
    def limpiar(self):
        self.query_one("#editor", TextArea).text = ""

if __name__ == "__main__":
    app = RedSocialMinimal()
    app.run()