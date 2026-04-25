import React, { useState } from 'react';

const CatalogView = ({ products, onSelectProduct, getProductImage, loading }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedOrigin, setSelectedOrigin] = useState('Todos');

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
                        {loading ? (
                            [1,2,3].map(i => <div key={i} className="skeleton" style={{height: '24px', marginBottom: '12px', width: '80%'}}></div>)
                        ) : (
                            origins.map(origin => (
                                <label key={origin} className="filter-item">
                                    <input type="radio" name="origin" checked={selectedOrigin === origin} onChange={() => setSelectedOrigin(origin)} style={{marginRight: '8px'}}/> 
                                    {origin}
                                </label>
                            ))
                        )}
                    </div>
                </aside>
                
                <main className="catalog-main">
                    <div className="main-header">
                        <span>{loading ? 'Cargando variedades...' : `Mostrando ${filteredProducts.length} variedades`}</span>
                    </div>
                    
                    <div className="product-grid">
                        {loading ? (
                            [1,2,3,4,5,6].map(i => (
                                <div key={i} className="product-card">
                                    <div className="product-image-container skeleton"></div>
                                    <div className="skeleton" style={{height: '24px', width: '70%', marginBottom: '8px'}}></div>
                                    <div className="skeleton" style={{height: '16px', width: '90%'}}></div>
                                </div>
                            ))
                        ) : filteredProducts.length === 0 ? (
                            <div style={{gridColumn: '1/-1', textAlign: 'center', padding: '80px', background: 'rgba(0,0,0,0.02)', borderRadius: '16px', border: '1px dashed #ccc'}}>
                                <h2 className="serif" style={{color: '#999'}}>No se encontraron coincidencias</h2>
                                <button className="btn btn-text" style={{marginTop: '20px', textDecoration: 'underline'}} onClick={() => {setSearchTerm(''); setSelectedOrigin('Todos');}}>Ver todo</button>
                            </div>
                        ) : (
                            filteredProducts.map(p => {
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
                                        <p className="product-desc">{p.description ? p.description.substring(0, 80) + '...' : 'Café de especialidad'}</p>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default CatalogView;
