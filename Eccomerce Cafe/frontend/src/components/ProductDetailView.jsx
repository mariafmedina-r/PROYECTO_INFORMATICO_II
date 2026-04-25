import React, { useState } from 'react';

const ProductDetailView = ({ product, onBack, onAddToCart, getProductImage, role }) => {
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
                </div>
                
                <div>
                    <div style={{display: 'flex', gap: '12px', marginBottom: '24px'}}>
                        {product.farm_name && <span className="badge badge-green">{product.farm_name}</span>}
                        {product.origin && <span className="badge" style={{border: '1px solid var(--border-color)', color: 'var(--text-secondary)'}}>{product.origin}</span>}
                    </div>
                    
                    <h1 className="product-title serif">{product.name}</h1>
                    
                    <div className="price-row">
                        <span className="price-large">${price.toFixed(2)}</span>
                        <span style={{color: 'var(--text-secondary)', marginBottom: '6px', fontSize: '0.9rem'}}>/ unidad</span>
                    </div>
                    
                    {product.sensory_notes && (
                        <div style={{marginBottom: '40px'}}>
                            <p style={{fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '16px'}}>Perfil Sensorial</p>
                            <div className="sensory-tags">
                                {product.sensory_notes.split(',').map((note, i) => (
                                    <span key={i} className="sensory-tag">{note.trim()}</span>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    <div className="stats-grid">
                        <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                            <span style={{fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)'}}>Altitud</span>
                            <span style={{fontWeight: 700, fontSize: '1.1rem'}}>{product.altitude || 'N/A'} msnm</span>
                        </div>
                        <div style={{display: 'flex', flexDirection: 'column', gap: '8px'}}>
                            <span style={{fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)'}}>Proceso</span>
                            <span style={{fontWeight: 700, fontSize: '1.1rem'}}>{product.process || 'Artesanal'}</span>
                        </div>
                    </div>
                    
                    {role !== 'PRODUCTOR' ? (
                        <div className="action-row">
                            <div className="qty-selector">
                                <button className="qty-btn" onClick={() => setQty(Math.max(1, qty - 1))}>-</button>
                                <input type="number" className="qty-input" value={qty} readOnly />
                                <button className="qty-btn" onClick={() => setQty(qty + 1)}>+</button>
                            </div>
                            <button className="btn btn-primary" style={{flex: 1}} onClick={() => onAddToCart(product, qty)}>
                                AÑADIR AL CARRITO 🛒
                            </button>
                        </div>
                    ) : (
                        <div style={{padding: '20px', background: 'var(--bg-color)', borderRadius: '8px', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'center'}}>
                            Estás visualizando este producto como <strong>Productor</strong>. <br/>
                            Las opciones de compra están deshabilitadas para tu rol.
                        </div>
                    )}
                </div>
            </div>
            
            <div className="essence-section">
                <div>
                    <h2 className="essence-title serif">Esencia del Producto</h2>
                    <div className="quote">Producido con pasión en fincas seleccionadas bajo estándares de alta calidad.</div>
                    <p style={{color: 'var(--text-secondary)', lineHeight: 1.8}}>{product.description || 'Café de especialidad con características únicas de su región.'}</p>
                </div>
                <div style={{background: 'var(--bg-color)', padding: '40px', borderRadius: '16px'}}>
                    <span style={{color: 'var(--accent-green)', fontSize: '0.75rem', fontWeight: 700, letterSpacing: '1px', marginBottom: '16px', display: 'block'}}>INFORMACIÓN ADICIONAL</span>
                    <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '16px'}}>Finca {product.farm_name || 'Productor Asociado'}</h3>
                    <p style={{color: 'var(--text-secondary)', lineHeight: 1.6}}>Región: {product.origin || 'Colombia'}</p>
                </div>
            </div>
        </div>
    );
}

export default ProductDetailView;
