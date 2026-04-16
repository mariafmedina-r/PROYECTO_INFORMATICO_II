export const API_URL = 'http://127.0.0.1:8000';

export async function getProducts() {
    const response = await fetch(`${API_URL}/products/`);
    if (!response.ok) throw new Error("Error al obtener catálogo");
    return response.json();
}

export async function getCart(userId = 1) {
    const response = await fetch(`${API_URL}/cart/?user_id=${userId}`);
    if (!response.ok) throw new Error("Error obteniendo el carrito");
    return response.json();
}

export async function addToCart(variantId, quantity = 1, userId = 1) {
    const response = await fetch(`${API_URL}/cart/items?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ variant_id: variantId, quantity: quantity })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al añadir producto");
    }
    return response.json();
}

export async function checkoutContext(userId = 1) {
    const response = await fetch(`${API_URL}/orders/checkout?user_id=${userId}`, { method: 'POST' });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Hubo un problema al procesar el pago");
    }
    return response.json();
}
