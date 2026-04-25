import React, { useState } from 'react';

const CatalogView = ({ products, onSelectProduct, getProductImage }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedOrigin, setSelectedOrigin] = useState('Todos');

    // Filtrar solo productos activos
    const activeProducts = products.filter(p => p.is_active !== false);

    const origins = ['Todos', ...new Set(activeProducts.map(p => p.origin).filter(Boolean))];

    const filteredProducts = activeProducts.filter(p => {
        const matchesSearch = (p.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                               p.description?.toLowerCase().includes(searchTerm.toLowerCase()));
        const matchesOrigin = selectedOrigin === 'Todos' || p.origin === selectedOrigin;
        return matchesSearch && matchesOrigin;
    });

    return (
        <div className="page-container">
            <h1 className="catalog-title serif">Haciendas Curadas,<br/><span>Origen Directo.</span></h1>
            
            <div className="search-bar">
                <span>🔍</span>
                <input 
                    type="text" 
                    placeholder="Buscar por tueste, origen o notas de sabor..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>
            
            <div className="catalog-layout">
                <aside className="filters">
                    <h3>Filtros <span>▾</span></h3>
                    <div className="filter-group">
                        <p className="filter-label">Origen / Región</p>
                        {origins.map(origin => (
                            <label key={origin} className="filter-item" style={{cursor: 'pointer', fontWeight: selectedOrigin === origin ? 700 : 400, color: selectedOrigin === origin ? 'var(--accent-green)' : 'inherit'}}>
                                <input 
                                    type="radio" 
                                    name="origin"
                                    checked={selectedOrigin === origin}
                                    onChange={() => setSelectedOrigin(origin)}
                                    style={{marginRight: '8px'}}
                                /> 
                                {origin}
                            </label>
                        ))}
                    </div>
                    
                    <div className="filter-group" style={{marginTop: '20px'}}>
                        <p className="filter-label">Notas Sensoriales</p>
                        <div className="tag-list">
                            <button className="tag-btn active">Floral</button>
                            <button className="tag-btn">Frutal</button>
                            <button className="tag-btn">Nuez</button>
                        </div>
                    </div>
                    <button className="btn btn-outline full-width" style={{marginTop: '20px'}} onClick={() => {setSearchTerm(''); setSelectedOrigin('Todos');}}>Limpiar Filtros</button>
                </aside>
                
                <main className="catalog-main">
                    <div className="main-header">
                        <span>Mostrando {filteredProducts.length} variedades</span>
                        <div>Ordenar por: <select style={{fontWeight: 700, border: 'none', background: 'transparent', cursor: 'pointer', textDecoration: 'underline'}}><option>Cosecha Reciente</option></select></div>
                    </div>
                    
                    {filteredProducts.length === 0 ? (
                        <div style={{textAlign: 'center', padding: '80px', background: 'rgba(0,0,0,0.02)', borderRadius: '16px', border: '1px dashed #ccc', marginTop: '40px'}}>
                            <h2 className="serif" style={{color: '#999'}}>No se encontraron coincidencias</h2>
                            <p style={{color: '#666'}}>Intenta ajustar tus criterios de búsqueda o filtros.</p>
                            <button className="btn btn-text" style={{marginTop: '20px', textDecoration: 'underline'}} onClick={() => {setSearchTerm(''); setSelectedOrigin('Todos');}}>Ver todo el catálogo</button>
                        </div>
                    ) : (
                        <div className="product-grid">
                            {filteredProducts.map(p => {
                                const price = p.price !== undefined ? parseFloat(p.price) : (p.variants?.length ? p.variants[0].price : 0);
                                return (
                                    <div key={p.id} className="product-card" onClick={() => onSelectProduct(p.id)}>
                                        <div className="product-image-container">
                                            <img src={getProductImage(p.id, p)} alt={p.name} />
                                            {p.is_exclusive && <div className="product-badge">Región Exclusiva</div>}
                                        </div>
                                        <div className="product-header-row">
                                            <h3 className="serif">{p.name}</h3>
                                            <span className="product-price">${price.toFixed(2)}</span>
                                        </div>
                                        <p className="product-desc">{p.description ? p.description.substring(0, 80) + '...' : 'Café de especialidad con notas únicas'}</p>
                                        <div style={{marginTop: '12px', fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-green)', textTransform: 'uppercase'}}>{p.origin}</div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default CatalogView;
