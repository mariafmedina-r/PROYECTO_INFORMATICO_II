export const getProductImage = (id, product = null) => {
    if (product && product.image_path && typeof product.image_path === 'string' && product.image_path.startsWith('http')) {
        return product.image_path;
    }
    
    // Hash string ID to number if necessary
    let numId = 0;
    if (typeof id === 'string') {
        for (let i = 0; i < id.length; i++) {
            numId += id.charCodeAt(i);
        }
    } else {
        numId = id || 0;
    }
    
    const images = [
        "https://images.unsplash.com/photo-1559525839-b184a4d698c7?w=800&q=80",
        "https://images.unsplash.com/photo-1554522904-e5fd41f1737e?w=800&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefed?w=800&q=80",
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80"
    ];
    return images[numId % images.length];
};
