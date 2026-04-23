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
                    <h1 className="serif" style={{fontSize: '5rem', lineHeight: 1, marginBottom: '24px'}}>Legado de la<br/>Montaña.</h1>
                    <p style={{fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: '500px'}}>Conexiones directas con los maestros de los Andes Colombianos. Celebramos la herencia detrás de cada grano.</p>
                </div>
            </div>
            
            {producers.length === 0 ? (
                <div style={{textAlign: 'center', padding: '80px', background: 'var(--bg-color)', borderRadius: '16px', border: '1px dashed var(--border-color)'}}>
                    <h3 className="serif" style={{color: 'var(--text-secondary)'}}>Actualmente no hay productores registrados.</h3>
                </div>
            ) : (
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px'}}>
                    {featuredProducer && (
                        <div style={{gridColumn: 'span 2', gridRow: 'span 2', minHeight: '600px', borderRadius: '20px', position: 'relative', overflow: 'hidden', padding: '60px', color: '#fff', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end'}}>
                            <img src="https://images.unsplash.com/photo-1628157588553-5eeea00af15c?w=1200&q=80" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', zIndex: 0}} alt="finca"/>
                            <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, transparent 100%)', zIndex: 1}}></div>
                            <div style={{position: 'relative', zIndex: 2}}>
                                <span className="badge badge-green" style={{background: 'rgba(255,255,255,0.2)', color: '#fff', backdropFilter: 'blur(5px)', border: '1px solid rgba(255,255,255,0.3)', marginBottom: '16px'}}>FINCA DESTACADA</span>
                                <h2 className="serif" style={{fontSize: '3.5rem', marginBottom: '8px'}}>{featuredProducer.full_name || featuredProducer.email}</h2>
                                <p style={{fontWeight: 700, letterSpacing: '1px', marginBottom: '20px'}}>📍 {featuredProducer.region || 'Colombia'}</p>
                                <p style={{color: '#ddd', lineHeight: 1.6, marginBottom: '32px', maxWidth: '80%'}}>{featuredProducer.description || 'Llevando adelante el legado del café colombiano cultivado en altura.'}</p>
                            </div>
                        </div>
                    )}
                    
                    {producers.slice(1).map((prod, idx) => {
                        const images = [
                            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&q=80",
                            "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&q=80",
                            "https://images.unsplash.com/photo-1589363460779-cbdf1b03b12a?w=500&q=80"
                        ];
                        return (
                            <div key={prod.id} style={{background: '#fff', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--border-color)'}}>
                                <div style={{height: '260px', overflow: 'hidden'}}><img src={images[idx % images.length]} style={{width: '100%', height: '100%', objectFit: 'cover'}} alt="prod"/></div>
                                <div style={{padding: '32px'}}>
                                    <h3 className="serif" style={{fontSize: '1.8rem', marginBottom: '4px'}}>{prod.full_name || prod.email}</h3>
                                    <p style={{color: 'var(--accent-green)', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '16px'}}>{prod.region || 'Colombia'}</p>
                                    <p style={{color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6}}>{prod.description ? (prod.description.substring(0, 80) + '...') : 'Productor certificado.'}</p>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    );
};

export default ProducersView;
