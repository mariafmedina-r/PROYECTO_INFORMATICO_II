import { ref, getDownloadURL } from 'firebase/storage';
import { storage } from './firebase_config';

export const getProductImage = async (id, customUrl = null) => {
    if (customUrl && customUrl.startsWith('gs://')) {
        try {
            const storageRef = ref(storage, customUrl);
            return await getDownloadURL(storageRef);
        } catch (e) {
            console.error("Storage Error", e);
        }
    }
    const images = [
        "https://images.unsplash.com/photo-1559525839-b184a4d698c7?w=800&q=80",
        "https://images.unsplash.com/photo-1554522904-e5fd41f1737e?w=800&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefed?w=800&q=80",
        "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&q=80"
    ];
    return images[(id || 0) % images.length];
};
