import React, { useState, useEffect } from 'react';
import { getProducts, getCart, addToCart, checkoutContext } from './api';

// --- Placeholder Images Loader ---
export const getProductImage = (id) => {
    const images = [
        "https://images.unsplash.com/photo-1559525839-b184a4d698c7?w=800&q=80",
        "https://images.unsplash.com/photo-1554522904-e5fd41f1737e?w=800&q=80",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefed?w=800&q=80",
        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80"
    ];
    return images[(id || 0) % images.length];
};

// --- View Components ---

const LoginView = ({ onLogin }) => (
    <div className="login-page">
        <div className="login-left">
            <img className="login-bg" src="https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=1200&q=80" alt="bg" />
            <div className="login-overlay"></div>
            <div className="login-left-content">
                <h1 className="login-title serif">La Conexión Artesanal</h1>
                <p className="login-subtitle">Cultivando fincas digitales para los mejores productores y conocedores de Colombia.</p>
                <div className="badge-secure"><span style={{textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.7rem'}}>🛡️ Conexión Segura Nacional</span></div>
            </div>
        </div>
        <div className="login-right">
            <div className="login-form">
                <h2 className="serif">Acceso Cafetero</h2>
                <p style={{color: 'var(--text-secondary)', marginBottom: '40px'}}>Ingrese sus credenciales para gestionar su patrimonio digital.</p>
                
                <div className="role-tabs">
                    <button className="role-tab active">COMPRADOR</button>
                    <button className="role-tab">PRODUCTOR</button>
                </div>
                
                <div className="input-group">
                    <label>Correo Electrónico</label>
                    <input type="email" defaultValue="usuario@finca.com" />
                </div>
                
                <div className="input-group">
                    <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                        <label style={{marginBottom: 0}}>Contraseña</label>
                        <a href="#" style={{fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-green)', textDecoration: 'none'}}>¿OLVIDÓ SU CONTRASEÑA?</a>
                    </div>
                    <input type="password" defaultValue="password123" />
                </div>
                
                <button className="btn btn-primary full-width" onClick={onLogin}>ENTRAR A MI FINCA DIGITAL</button>
                
                <div className="social-divider"><span>O acceder con</span></div>
                <div className="social-btns">
                    <button className="btn btn-outline full-width">G GOOGLE</button>
                    <button className="btn btn-outline full-width">🍎 APPLE</button>
                </div>
            </div>
        </div>
    </div>
);

const CatalogView = ({ products, onSelectProduct }) => (
    <div className="page-container">
        <h1 className="catalog-title serif">Haciendas Curadas,<br/><span>Origen Directo.</span></h1>
        
        <div className="search-bar">
            <span>🔍</span>
            <input type="text" placeholder="Buscar por tueste, origen o notas de sabor..." />
        </div>
        
        <div className="catalog-layout">
            <aside className="filters">
                <h3>Filtros <span>▾</span></h3>
                <div className="filter-group">
                    <p className="filter-label">Origen</p>
                    <label className="filter-item"><input type="checkbox" /> Huila, Colombia</label>
                    <label className="filter-item" style={{color: 'var(--accent-green)', fontWeight: 600}}><input type="checkbox" defaultChecked /> Antigua, Guatemala</label>
                    <label className="filter-item"><input type="checkbox" /> Sidamo, Etiopía</label>
                </div>
                <div className="filter-group">
                    <p className="filter-label">Notas Sensoriales</p>
                    <div className="tag-list">
                        <button className="tag-btn active">Floral</button>
                        <button className="tag-btn">Frutal</button>
                        <button className="tag-btn">Nuez</button>
                    </div>
                </div>
                <button className="btn btn-outline full-width">Limpiar Filtros</button>
            </aside>
            
            <main className="catalog-main">
                <div className="main-header">
                    <span>Mostrando {products.length} variedades</span>
                    <div>Ordenar por: <select style={{fontWeight: 700, border: 'none', background: 'transparent', cursor: 'pointer', textDecoration: 'underline'}}><option>Cosecha Reciente</option></select></div>
                </div>
                
                <div className="product-grid">
                    {products.map(p => {
                        const price = p.variants?.length ? p.variants[0].price : 0;
                        return (
                            <div key={p.id} className="product-card" onClick={() => onSelectProduct(p.id)}>
                                <div className="product-image-container">
                                    <img src={getProductImage(p.id)} alt={p.name} />
                                    <div className="product-badge">Región Exclusiva</div>
                                </div>
                                <div className="product-header-row">
                                    <h3 className="serif">{p.name}</h3>
                                    <span className="product-price">${price.toFixed(2)}</span>
                                </div>
                                <p className="product-desc">{p.description ? p.description.substring(0, 50) + '...' : 'Café de especialidad con notas únicas'}</p>
                            </div>
                        );
                    })}
                </div>
            </main>
        </div>
    </div>
);

const ProductDetailView = ({ product, onBack, onAddToCart }) => {
    const [qty, setQty] = useState(1);
    if (!product) return <div className="page-container"><p>Producto no encontrado.</p></div>;
    const variant = product.variants?.length ? product.variants[0] : null;

    return (
        <div className="page-container">
            <button className="back-btn" onClick={onBack}>← Volver al Catálogo</button>
            
            <div className="product-detail-layout">
                <div className="product-hero-images">
                    <img src={getProductImage(product.id)} className="main-img" alt={product.name} />
                    <div className="sub-images">
                        <img src="https://images.unsplash.com/photo-1541167760496-1628856ab772?w=400&q=80" className="sub-img" alt="sub1"/>
                        <img src="https://images.unsplash.com/photo-1498603536246-15572faa67a6?w=400&q=80" className="sub-img" alt="sub2"/>
                    </div>
                </div>
                
                <div>
                    <div style={{display: 'flex', gap: '12px', marginBottom: '24px'}}>
                        <span className="badge badge-green">Granja Miel</span>
                        <span className="badge" style={{border: '1px solid var(--border-color)', color: 'var(--text-secondary)'}}>Huila, Colombia</span>
                    </div>
                    
                    <h1 className="product-title serif">{product.name}</h1>
                    
                    <div className="price-row">
                        <span className="price-large">${variant ? variant.price.toFixed(2) : '0.00'}</span>
                        <span style={{color: 'var(--text-secondary)', marginBottom: '6px', fontSize: '0.9rem'}}>/ bolsa de 250g</span>
                    </div>
                    
                    <div style={{marginBottom: '40px'}}>
                        <p style={{fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '16px'}}>Perfil Sensorial</p>
                        <div className="sensory-tags">
                            <span className="sensory-tag">🌸 Jazmín</span>
                            <span className="sensory-tag">🍋 Bergamota</span>
                            <span className="sensory-tag">🍯 Miel</span>
                        </div>
                    </div>
                    
                    <div className="stats-grid">
                        <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                            <span style={{fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)'}}>Altitud</span>
                            <span style={{fontWeight: 700, fontSize: '1.1rem'}}>1,850 msnm</span>
                        </div>
                        <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                            <span style={{fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)'}}>Proceso</span>
                            <span style={{fontWeight: 700, fontSize: '1.1rem'}}>Lavado Honey</span>
                        </div>
                    </div>
                    
                    <div className="action-row">
                        <div className="qty-selector">
                            <button className="qty-btn" onClick={() => setQty(Math.max(1, qty - 1))}>-</button>
                            <input type="number" className="qty-input" value={qty} readOnly />
                            <button className="qty-btn" onClick={() => setQty(qty + 1)}>+</button>
                        </div>
                        <button className="btn btn-primary" style={{flex: 1}} onClick={() => onAddToCart(variant?.id, qty)}>
                            AÑADIR AL CARRITO 🛒
                        </button>
                    </div>
                </div>
            </div>
            
            <div className="essence-section">
                <div>
                    <h2 className="essence-title serif">Esencia del Producto</h2>
                    <div className="quote">Una iteración excepcional de la variedad cultivada en su punto óptimo de madurez en los microclimas de gran altitud.</div>
                    <p style={{color: 'var(--text-secondary)', lineHeight: 1.8}}>{product.description || 'Proceso artesanal cuidado en cada etapa de producción.'}</p>
                </div>
                <div style={{background: 'var(--bg-color)', padding: '40px', borderRadius: '16px'}}>
                    <span style={{color: 'var(--accent-green)', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '1px', marginBottom: '16px', display: 'block'}}>CONOCE AL PRODUCTOR</span>
                    <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '16px'}}>Familia Productora</h3>
                    <p style={{color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '24px'}}>Productores de café de tercera generación cultivando en las montañas del Huila.</p>
                </div>
            </div>
        </div>
    );
}

const ProducersView = () => (
    <div className="page-container">
        <span className="badge badge-green" style={{display: 'inline-block', marginBottom: '16px'}}>NUESTROS CAFICULTORES</span>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '60px'}}>
            <div>
                <h1 className="serif" style={{fontSize: '5rem', lineHeight: 1, marginBottom: '24px'}}>Legado de la<br/>Montaña.</h1>
                <p style={{fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '500px'}}>Conexiones directas con los maestros de los Andes Colombianos. Celebramos la herencia detrás de cada grano.</p>
            </div>
        </div>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px'}}>
            <div style={{gridColumn: 'span 2', gridRow: 'span 2', minHeight: '600px', borderRadius: '20px', position: 'relative', overflow: 'hidden', padding: '60px', color: '#fff', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end'}}>
                <img src="https://images.unsplash.com/photo-1628157588553-5eeea00af15c?w=1200&q=80" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', zIndex: 0}} alt="finca"/>
                <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, transparent 100%)', zIndex: 1}}></div>
                <div style={{position: 'relative', zIndex: 2}}>
                    <span className="badge badge-green" style={{background: 'rgba(255,255,255,0.2)', color: '#fff', backdropFilter: 'blur(5px)', border: '1px solid rgba(255,255,255,0.3)', marginBottom: '16px'}}>FINCA DESTACADA</span>
                    <h2 className="serif" style={{fontSize: '3.5rem', marginBottom: '8px'}}>Mateo Rivera</h2>
                    <p style={{fontWeight: 700, letterSpacing: '1px', marginBottom: '20px'}}>📍 Huila, Colombia</p>
                    <p style={{color: '#ddd', lineHeight: 1.6, marginBottom: '32px', maxWidth: '80%'}}>Carrying forward a four-generation legacy in the heart of Huila, combining ancestral knowledge with modern regenerative techniques.</p>
                </div>
            </div>
            <div style={{background: '#fff', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border-color)'}}>
                <div style={{height: '260px', overflow: 'hidden'}}><img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&q=80" style={{width: '100%', height: '100%', objectFit: 'cover'}} alt="prod"/></div>
                <div style={{padding: '32px'}}>
                    <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '4px'}}>Beatriz Mendez</h3>
                    <p style={{color: 'var(--accent-green)', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px'}}>Nariño, Colombia</p>
                    <p style={{color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6}}>Specializing in washed process lots from the steep slopes of Nariño.</p>
                </div>
            </div>
            <div style={{background: '#fff', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border-color)'}}>
                <div style={{height: '260px', overflow: 'hidden'}}><img src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&q=80" style={{width: '100%', height: '100%', objectFit: 'cover'}} alt="prod2"/></div>
                <div style={{padding: '32px'}}>
                    <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '4px'}}>Carlos Ruiz</h3>
                    <p style={{color: 'var(--accent-green)', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px'}}>Quindío, Colombia</p>
                    <p style={{color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6}}>A pioneer in the Eje Cafetero focusing on anaerobic fermentation.</p>
                </div>
            </div>
        </div>
    </div>
);

const OriginView = () => (
    <div>
        <div style={{height: '70vh', position: 'relative', display: 'flex', alignItems: 'center', padding: '0 80px'}}>
            <img src="https://images.unsplash.com/photo-1524414139215-35c99f80112d?w=1600&q=80" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', zIndex: 0}} alt="origin" />
            <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, rgba(250,248,245,1) 0%, rgba(250,248,245,0.7) 50%, transparent 100%)', zIndex: 1}}></div>
            <div style={{position: 'relative', zIndex: 2, maxWidth: '600px', background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(12px)', padding: '60px', borderRadius: '24px'}}>
                <span className="badge badge-green" style={{display: 'inline-block', marginBottom: '24px'}}>EL TERROIR DE LOS ANDES</span>
                <h1 className="serif" style={{fontSize: '5rem', lineHeight: 1, marginBottom: '24px', color: 'var(--text-primary)'}}>Colombia: Tierra de Gracia</h1>
                <p style={{fontSize: '1.2rem', color: 'var(--text-primary)', lineHeight: 1.6}}>Descubre la diversidad inigualable del café colombiano. Desde las cumbres nevadas del norte hasta las laderas volcánicas del Eje Cafetero.</p>
            </div>
        </div>
    </div>
);

// --- Main App Component ---

export default function App() {
    const [view, setView] = useState('login');
    const [products, setProducts] = useState([]);
    const [currentProductId, setCurrentProductId] = useState(null);
    const [cartData, setCartData] = useState({ items: [], total: 0, subtotal: 0, total_iva: 0 });
    const [cartOpen, setCartOpen] = useState(false);
    const [toasts, setToasts] = useState([]);

    const showToast = (message, type = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type, show: false }]);
        setTimeout(() => {
            setToasts(prev => prev.map(t => t.id === id ? { ...t, show: true } : t));
        }, 10);
        setTimeout(() => {
            setToasts(prev => prev.map(t => t.id === id ? { ...t, show: false } : t));
            setTimeout(() => {
                setToasts(prev => prev.filter(t => t.id !== id));
            }, 400);
        }, 4000);
    };

    const handleLogin = async () => {
        showToast("Conexión segura establecida", "success");
        try {
            const data = await getProducts();
            setProducts(data);
            setView('catalog');
            await refreshCart();
        } catch (err) {
            showToast("Error conectando con el servidor", "error");
            console.error(err);
        }
    };

    const refreshCart = async () => {
        try {
            const data = await getCart(1);
            setCartData(data);
        } catch (error) {
            console.error(error);
        }
    };

    const handleAddToCart = async (variantId, quantity) => {
        if (!variantId) {
            showToast("Variante inválida", "error");
            return;
        }
        try {
            await addToCart(variantId, quantity, 1);
            showToast("Añadido a tu patrimonio digital", "success");
            await refreshCart();
            setCartOpen(true);
        } catch (err) {
            showToast(err.message, "error");
        }
    };

    const handleCheckout = async () => {
        if (!cartData.items.length) {
            showToast("El carrito está vacío", "error");
            return;
        }
        try {
            await checkoutContext(1);
            showToast("¡Pedido confirmado con éxito!", "success");
            setCartOpen(false);
            await refreshCart();
        } catch (err) {
            showToast(err.message, "error");
        }
    };

    const navigateTo = (newView, payload = null) => {
        setView(newView);
        if(payload !== null) setCurrentProductId(payload);
        window.scrollTo(0, 0);
    };

    const renderView = () => {
        if (view === 'login') return <LoginView onLogin={handleLogin} />;
        if (view === 'catalog') return <CatalogView products={products} onSelectProduct={(id) => navigateTo('product', id)} />;
        if (view === 'product') return <ProductDetailView product={products.find(p => p.id === currentProductId)} onBack={() => navigateTo('catalog')} onAddToCart={handleAddToCart} />;
        if (view === 'producers') return <ProducersView />;
        if (view === 'origin') return <OriginView />;
        return <div className="page-container"><h2 className="serif">Vista en Construcción</h2><button className="btn btn-outline" onClick={() => navigateTo('catalog')}>Volver</button></div>;
    };

    return (
        <>
            <div className="toast-container">
                {toasts.map(t => (
                    <div key={t.id} className={`toast toast-${t.type} ${t.show ? 'show' : ''}`}>
                        <span className="toast-icon">{t.type === 'success' ? '✓' : '⚠'}</span>
                        <span>{t.message}</span>
                    </div>
                ))}
            </div>

            {view !== 'login' && (
                <header className="navbar">
                    <button className="logo-btn" onClick={() => navigateTo('catalog')}>The Artisanal Connection</button>
                    <nav className="nav-links">
                        <button className={`nav-item ${view === 'catalog' ? 'active' : ''}`} onClick={() => navigateTo('catalog')}>Catálogo</button>
                        <button className={`nav-item ${view === 'producers' ? 'active' : ''}`} onClick={() => navigateTo('producers')}>Productores</button>
                        <button className={`nav-item ${view === 'origin' ? 'active' : ''}`} onClick={() => navigateTo('origin')}>Origen</button>
                    </nav>
                    <div style={{display: 'flex', alignItems: 'center', gap: '24px'}}>
                        <button className="cart-icon-btn" onClick={() => setCartOpen(true)}>🛒
                            <span className="cart-badge" style={{display: cartData.items.reduce((acc, i)=> acc + i.quantity, 0) > 0 ? 'inline-block' : 'none'}}>
                                {cartData.items.reduce((acc, i)=> acc + i.quantity, 0)}
                            </span>
                        </button>
                        <div style={{width: '36px', height: '36px', borderRadius: '50%', background: '#ccc', overflow: 'hidden'}}>
                            <img src="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&q=80" style={{width: '100%', height: '100%', objectFit: 'cover'}} alt="user"/>
                        </div>
                    </div>
                </header>
            )}

            {renderView()}

            {view !== 'login' && (
                <footer className="footer">
                    <div className="footer-container">
                        <div>
                            <h3 className="footer-brand">The Artisanal Connection</h3>
                            <p className="footer-desc">Acortando la distancia entre los micro-lotes de gran altitud y su ritual matutino. Priorizamos la trazabilidad, la compensación justa y una calidad inigualable.</p>
                            <p style={{fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase'}}>© 2026 The Artisanal Connection.</p>
                        </div>
                        <div className="footer-links">
                            <div className="footer-col">
                                <h4>Explorar</h4>
                                <ul><li><a href="#">Sostenibilidad</a></li><li><a href="#">Comercio Directo</a></li></ul>
                            </div>
                            <div className="footer-col">
                                <h4>Boletín</h4>
                                <div className="newsletter-form">
                                    <input type="email" placeholder="Correo electrónico" />
                                    <button>→</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </footer>
            )}

            <div className={`cart-drawer ${cartOpen ? 'open' : ''}`}>
                <div className="cart-overlay" onClick={() => setCartOpen(false)}></div>
                <div className="cart-panel">
                    <div className="cart-header">
                        <h2>Tu Carrito</h2>
                        <button className="close-action" onClick={() => setCartOpen(false)}>×</button>
                    </div>
                    <div className="cart-items">
                        {cartData.items.length === 0 ? (
                            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)'}}>
                                <span style={{fontSize: '3rem', opacity: 0.5}}>🛒</span><p>Tu carrito está reposando...</p>
                            </div>
                        ) : (
                            cartData.items.map(item => (
                                <div key={item.id} className="cart-item">
                                    <img src={getProductImage(item.variant.product_id)} className="cart-item-img" alt={item.variant.name}/>
                                    <div className="cart-item-info">
                                        <h4>{item.variant.name}</h4>
                                        <p>Cantidad: <span style={{fontWeight: 700, color: 'var(--text-primary)'}}>{item.quantity}</span></p>
                                        <p style={{fontWeight: 700, color: 'var(--text-primary)'}}>${(item.variant.price * item.quantity).toFixed(2)}</p>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                    <div className="cart-footer">
                        <div className="summary-row"><span>Subtotal</span><span>${cartData.subtotal.toFixed(2)}</span></div>
                        <div className="summary-row"><span>IVA</span><span>${cartData.total_iva.toFixed(2)}</span></div>
                        <div className="summary-total"><span>Total</span><span>${cartData.total.toFixed(2)}</span></div>
                        <button className="btn btn-primary full-width" onClick={handleCheckout}>Checkout Seguro</button>
                    </div>
                </div>
            </div>
        </>
    );
}
