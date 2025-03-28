# Gestor de Datos Firebase
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import List, Dict, Optional

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class FirebaseDataManager:
    def __init__(self):
        self._initialize_firebase()
        self.db = firestore.client()
    
    def _initialize_firebase(self):
        """Configura la conexión con Firebase"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate("service-account.json")
                firebase_admin.initialize_app(cred)
        except Exception as e:
            raise ConnectionError(f"Firebase connection failed: {str(e)}")

    def get_users(self, theme_filter: str = None) -> List[Dict]:
        """Obtiene usuarios con filtro opcional por tema"""
        try:
            users_ref = self.db.collection("usuarios")
            
            if theme_filter:
                users_ref = users_ref.where("tema_interes", "==", theme_filter.lower())
            
            return [self._format_user(doc) for doc in users_ref.stream()]
        except Exception as e:
            raise RuntimeError(f"Error fetching users: {str(e)}")

    def _format_user(self, user_doc) -> Dict:
        """Formatea los datos del usuario"""
        user_data = user_doc.to_dict()
        return {
            'id': user_doc.id,
            'name': user_data.get('nombre', 'Anonymous'),
            'email': user_data.get('email', ''),
            'theme': user_data.get('tema_interes', 'general').capitalize(),
            'register_date': self._parse_date(user_data.get('fecha_registro'))
        }

    def _parse_date(self, date) -> str:
        """Convierte timestamp a string legible"""
        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d %H:%M")
        return str(date) if date else "Unknown"

    def add_user(self, user_data: Dict) -> str:
        """Añade un nuevo usuario a Firestore"""
        required_fields = ['nombre', 'email', 'tema_interes']
        if not all(field in user_data for field in required_fields):
            raise ValueError("Missing required user fields")
        
        try:
            doc_ref = self.db.collection("usuarios").add({
                'nombre': user_data['nombre'],
                'email': user_data['email'],
                'tema_interes': user_data['tema_interes'].lower(),
                'fecha_registro': firestore.SERVER_TIMESTAMP
            })
            return doc_ref[1].id
        except Exception as e:
            raise RuntimeError(f"Error adding user: {str(e)}")

# Ejemplo de uso autónomo
if __name__ == "__main__":
    try:
        manager = FirebaseDataManager()
        
        # Test: Obtener usuarios
        print("=== Testing get_users() ===")
        users = manager.get_users()
        print(f"Found {len(users)} users")
        
        # Test: Filtrar por tema
        gamers = manager.get_users("gamers")
        print(f"Found {len(gamers)} gamers")
        
        # Test: Añadir usuario (descomentar para probar)
        # new_id = manager.add_user({
        #     "nombre": "Test User",
        #     "email": "test@example.com",
        #     "tema_interes": "testing"
        # })
        # print(f"Added user with ID: {new_id}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")

    # codigo de usuarios.py finalizado 