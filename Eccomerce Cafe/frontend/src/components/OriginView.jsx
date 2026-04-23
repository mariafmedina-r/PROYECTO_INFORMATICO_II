import React from 'react';

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
        <div className="page-container" style={{padding: '80px 0'}}>
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '40px'}}>
                <div style={{background: '#fff', padding: '40px', borderRadius: '16px', boxShadow: 'var(--shadow-soft)', border: '1px solid var(--border-color)'}}>
                    <h3 className="serif" style={{fontSize: '2rem', marginBottom: '16px', color: 'var(--accent-green)'}}>Huila</h3>
                    <p style={{color: 'var(--text-secondary)', lineHeight: '1.6'}}>Suelos volcánicos ricos en minerales y vientos del valle del río Magdalena. Produce tazas balanceadas con notas a caramelo y frutas tropicales dulce.</p>
                </div>
                <div style={{background: '#fff', padding: '40px', borderRadius: '16px', boxShadow: 'var(--shadow-soft)', border: '1px solid var(--border-color)'}}>
                    <h3 className="serif" style={{fontSize: '2rem', marginBottom: '16px', color: 'var(--accent-green)'}}>Antioquia</h3>
                    <p style={{color: 'var(--text-secondary)', lineHeight: '1.6'}}>Montañas escarpadas y microclimas ideales. Da como resultado cafés suaves, taza limpia, con una acidez cítrica brillante y cuerpo medio.</p>
                </div>
                <div style={{background: '#fff', padding: '40px', borderRadius: '16px', boxShadow: 'var(--shadow-soft)', border: '1px solid var(--border-color)'}}>
                    <h3 className="serif" style={{fontSize: '2rem', marginBottom: '16px', color: 'var(--accent-green)'}}>Nariño</h3>
                    <p style={{color: 'var(--text-secondary)', lineHeight: '1.6'}}>Cultivado a gran altitud bajo la influencia extrema del Pacífico. Desarrolla perfiles únicos, alta acidez cítrica y dulzor herbal marcado.</p>
                </div>
            </div>
        </div>
    </div>
);

export default OriginView;
