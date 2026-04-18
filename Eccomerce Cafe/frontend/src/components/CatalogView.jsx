import React from 'react';

const CatalogView = ({ products, onSelectProduct, getProductImage }) => (
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
                        const price = p.price !== undefined ? parseFloat(p.price) : (p.variants?.length ? p.variants[0].price : 0);
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

export default CatalogView;
