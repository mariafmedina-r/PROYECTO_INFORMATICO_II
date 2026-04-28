"""
repositories/user_repository.py – Acceso a la colección 'users' en Firestore.

Colección Firestore: /users/{userId}
"""

from datetime import datetime, timezone
from typing import Optional

from firebase_admin import firestore


class UserRepository:
    """Repositorio de usuarios en Firestore."""

    COLLECTION = "users"

    def __init__(self):
        self._db = firestore.client()

    def create(self, uid: str, name: str, email: str, role: str) -> dict:
        """
        Crea un documento de usuario en Firestore.

        Args:
            uid: Firebase UID del usuario.
            name: Nombre del usuario.
            email: Correo electrónico.
            role: Rol asignado (CONSUMER, PRODUCER, ADMIN).

        Returns:
            Diccionario con los datos del usuario creado.
        """
        now = datetime.now(timezone.utc)
        user_data = {
            "id": uid,
            "name": name,
            "email": email,
            "role": role,
            "createdAt": now,
            "updatedAt": now,
        }
        self._db.collection(self.COLLECTION).document(uid).set(user_data)
        return user_data

    def get_by_id(self, uid: str) -> Optional[dict]:
        """
        Obtiene un usuario por su UID.

        Args:
            uid: Firebase UID del usuario.

        Returns:
            Diccionario con los datos del usuario, o None si no existe.
        """
        doc = self._db.collection(self.COLLECTION).document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_by_email(self, email: str) -> Optional[dict]:
        """
        Busca un usuario por correo electrónico.

        Args:
            email: Correo electrónico a buscar.

        Returns:
            Diccionario con los datos del usuario, o None si no existe.
        """
        docs = (
            self._db.collection(self.COLLECTION)
            .where("email", "==", email)
            .limit(1)
            .stream()
        )
        for doc in docs:
            return doc.to_dict()
        return None
