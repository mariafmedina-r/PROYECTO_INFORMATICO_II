import { db_fs } from './firebase_config';
import { doc, getDoc, setDoc, updateDoc, collection, query, where, getDocs, addDoc, deleteDoc } from "firebase/firestore";

const API_URL = 'http://localhost:8000';

// --- Firestore Base APIs (User Profiles & Roles) ---

export async function saveUserProfile(uid, userData) {
    const res = await fetch(`${API_URL}/users/profile?uid=${uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    return res.json();
}

export async function getUserProfile(uid) {
    try {
        const res = await fetch(`${API_URL}/users/profile/${uid}`);
        if (res.ok) {
            return await res.json();
        }
    } catch(e) { console.error("Error al obtener perfil desde backend:", e); }
    return null;
}

export async function approveProducerFS(uid) {
    const docRef = doc(db_fs, "users", uid);
    await updateDoc(docRef, { is_active: true });
}

export async function upgradeToProducerFS(uid, producerData) {
    const res = await fetch(`${API_URL}/users/upgrade-to-producer?uid=${uid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(producerData)
    });
    return res.json();
}

export async function toggleUserStatusFS(uid, currentStatus) {
    const docRef = doc(db_fs, "users", uid);
    await updateDoc(docRef, { is_active: !currentStatus });
}

export async function getPendingProducersFS() {
    const q = query(collection(db_fs, "users"), where("role", "==", "PRODUCTOR"), where("is_active", "==", false));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(d => ({ id: d.id, ...d.data() }));
}

export async function getAllUsersFS() {
    const res = await fetch(`${API_URL}/users/admin/firebase-users`);
    return res.json();
}

// --- Firestore Products APIs ---

export async function getProductsFS() {
    const querySnapshot = await getDocs(collection(db_fs, "products"));
    return querySnapshot.docs.map(d => ({ id: d.id, ...d.data() }));
}

export async function createProductFS(productData, userId) {
    const docRef = await addDoc(collection(db_fs, "products"), {
        ...productData,
        producer_id: userId,
        createdAt: new Date().toISOString()
    });
    return { id: docRef.id, ...productData };
}

export async function deleteProductFS(productId) {
    await deleteDoc(doc(db_fs, "products", productId));
}

// --- Backend SQL APIs (Orders & Cart Placeholder) ---

export async function getCart(userId, token) {
    const res = await fetch(`${API_URL}/cart`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
}

export async function addToCart(variantId, quantity, userId, token) {
    const res = await fetch(`${API_URL}/cart/items`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ variant_id: variantId, quantity })
    });
    if (!res.ok) throw new Error("Stock insuficiente u error en carrito");
    return res.json();
}

export async function checkoutContext(userId, token) {
    const res = await fetch(`${API_URL}/orders/checkout/${userId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
}
