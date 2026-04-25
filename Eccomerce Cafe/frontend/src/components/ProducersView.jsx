import React, { useState, useEffect } from 'react';
import { getAllUsersFS } from '../api';

const ProducersView = () => {
    const [producers, setProducers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProducers = async () => {
            try {
                const users = await getAllUsersFS();
                const activeProducers = users.filter(u => u.role === 'PRODUCTOR' && u.is_active);
                setProducers(activeProducers);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchProducers();
    }, []);

    if (loading) {
        return <div className="page-container" style={{textAlign: 'center', padding: '100px 0'}}><h2>Cargando cultivadores...</h2></div>;
    }

    const featuredProducer = producers.length > 0 ? producers[0] : null;

    return (
        <div className="page-container">
            <span className="badge badge-green" style={{display: 'inline-block', marginBottom: '16px'}}>NUESTROS CAFICULTORES</span>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '60px'}}>
                <div>
                    <h1 className="serif" style={{fontSize: '5rem', lineHeight: 1, marginBottom: '24px'}}>Maestros del<br/>Grano.</h1>
                    <p style={{fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '500px'}}>Conoce a las personas detrás de tu taza diaria. Transparencia total desde la finca hasta tu hogar.</p>
                </div>
            </div>
            
            {producers.length === 0 ? (
                <div style={{textAlign: 'center', padding: '80px', background: 'var(--bg-color)', borderRadius: '16px', border: '1px dashed var(--border-color)'}}>
                    <h3 className="serif" style={{color: 'var(--text-secondary)'}}>Actualmente no hay productores registrados con productos activos.</h3>
                </div>
            ) : (
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '32px'}}>
                    {producers.map((prod) => (
                        <div key={prod.id} style={{background: '#fff', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column'}}>
                            <div style={{height: '240px', overflow: 'hidden', background: '#f0f0f0'}}>
                                <img 
                                    src={prod.farm_image || prod.photoURL || "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=500&q=80"} 
                                    style={{width: '100%', height: '100%', objectFit: 'cover'}} 
                                    alt="finca"
                                />
                            </div>
                            <div style={{padding: '32px', flex: 1, display: 'flex', flexDirection: 'column'}}>
                                <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '4px'}}>{prod.farm_name || 'Finca Sin Nombre'}</h3>
                                <p style={{color: 'var(--accent-green)', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px'}}>
                                    {prod.full_name || 'Productor'} • {prod.region || 'Colombia'}
                                </p>
                                <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, flex: 1}}>
                                    {prod.description || 'Productor certificado de café de especialidad comprometido con la calidad y la sostenibilidad.'}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ProducersView;
