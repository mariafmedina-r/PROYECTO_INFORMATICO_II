import { db_fs } from './firebase_config';
import { doc, getDoc, setDoc, updateDoc, collection, query, where, getDocs, addDoc, deleteDoc } from "firebase/firestore";

const API_URL = 'http://localhost:8000';

// --- Firestore Base APIs (User Profiles & Roles) ---

export async function saveUserProfile(uid, userData) {
    await setDoc(doc(db_fs, "users", uid), {
        ...userData,
        is_active: userData.role === 'PRODUCTOR' ? false : true,
        createdAt: new Date().toISOString()
    });
}

export async function getUserProfile(uid) {
    const docRef = doc(db_fs, "users", uid);
    const docSnap = await getDoc(docRef);
    if (docSnap.exists()) return docSnap.data();
    return null;
}

export async function approveProducerFS(uid) {
    const docRef = doc(db_fs, "users", uid);
    await updateDoc(docRef, { is_active: true });
}

export async function getPendingProducersFS() {
    const q = query(collection(db_fs, "users"), where("role", "==", "PRODUCTOR"), where("is_active", "==", false));
    const querySnapshot = await getDocs(q);
    return querySnapshot.docs.map(d => ({ id: d.id, ...d.data() }));
}

export async function getAllUsersFS() {
    const querySnapshot = await getDocs(collection(db_fs, "users"));
    return querySnapshot.docs.map(d => ({ id: d.id, ...d.data() }));
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
    const res = await fetch(`${API_URL}/carts/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
}

export async function addToCart(variantId, quantity, userId, token) {
    const res = await fetch(`${API_URL}/carts/${userId}/items`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ variant_id: variantId, quantity })
    });
    if (!res.ok) throw new Error("Stock insuficiente");
    return res.json();
}

export async function checkoutContext(userId, token) {
    const res = await fetch(`${API_URL}/orders/checkout/${userId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
}
