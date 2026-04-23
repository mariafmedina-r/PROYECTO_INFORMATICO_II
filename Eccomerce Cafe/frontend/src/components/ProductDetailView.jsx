import React, { useState } from 'react';

const ProductDetailView = ({ product, onBack, onAddToCart, getProductImage }) => {
    const [qty, setQty] = useState(1);
    if (!product) return <div className="page-container"><p>Producto no encontrado.</p></div>;
    const variant = product.variants?.length ? product.variants[0] : null;
    const price = product.price !== undefined ? parseFloat(product.price) : (variant ? variant.price : 0);

    return (
        <div className="page-container">
            <button className="back-btn" onClick={onBack}>← Volver al Catálogo</button>
            
            <div className="product-detail-layout">
                <div className="product-hero-images">
                    <img src={getProductImage(product.id, product)} className="main-img" alt={product.name} />
                    <div className="sub-images">
                        <img src="https://images.unsplash.com/photo-1541167760496-1628856ab772?w=400&q=80" className="sub-img" alt="sub1"/>
                        <img src="https://images.unsplash.com/photo-1498603536246-15572faa67a6?w=400&q=80" className="sub-img" alt="sub2"/>
                    </div>
                </div>
                
                <div>
                    <div style={{display: 'flex', gap: '12px', marginBottom: '24px'}}>
                        <span className="badge badge-green">Granja Miel</span>
                        <span className="badge" style={{border: '1px solid var(--border-color)', color: 'var(--text-secondary)'}}>{product.origin || 'Colombia'}</span>
                    </div>
                    
                    <h1 className="product-title serif">{product.name}</h1>
                    
                    <div className="price-row">
                        <span className="price-large">${price.toFixed(2)}</span>
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

export default ProductDetailView;
