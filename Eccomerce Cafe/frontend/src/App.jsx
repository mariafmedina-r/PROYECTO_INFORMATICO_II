import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import { getProductsFS, createProductFS, deleteProductFS, getCart, addToCart, checkoutContext, getPendingProducersFS, approveProducerFS, saveUserProfile, getAllUsersFS } from './api';
import LoginView from './components/LoginView';
import CatalogView from './components/CatalogView';
import ProductDetailView from './components/ProductDetailView';
import ProducersView from './components/ProducersView';
import OriginView from './components/OriginView';
import { getProductImage } from './utils';
import { auth } from './firebase_config';
import { createUserWithEmailAndPassword } from 'firebase/auth';

class ErrorBoundary extends React.Component {
    constructor(props) { super(props); this.state = { hasError: false, error: null }; }
    static getDerivedStateFromError(error) { return { hasError: true, error }; }
    render() {
        if (this.state.hasError) {
            return (
                <div style={{padding: '50px', background: '#fee', color: '#900', fontFamily: 'monospace'}}>
                    <h2>El sistema encontró un error fatal</h2>
                    <p>{this.state.error?.toString()}</p>
                    <button onClick={() => window.location.href='/'} style={{padding: '10px', marginTop: '20px'}}>Volver al inicio</button>
                </div>
            );
        }
        return this.props.children;
    }
}

// --- Improved Components ---

const AdminDashboard = ({ token, showToast }) => {
    const [view, setView] = useState('overview');
    const [pending, setPending] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [inviteLink, setInviteLink] = useState('');

    const loadData = async () => {
        try {
            const p = await getPendingProducersFS();
            setPending(p);
            const u = await getAllUsersFS();
            setAllUsers(u);
        } catch (e) { console.error(e); }
    };

    useEffect(() => { loadData(); }, [token]);

    const handleApprove = async (id) => {
        try {
            await approveProducerFS(id);
            showToast("Productor aprobado exitosamente", "success");
            loadData();
        } catch (e) { showToast("Error al aprobar", "error"); }
    };

    const generateInvite = () => {
        const t = Math.random().toString(36).substring(7);
        setInviteLink(`${window.location.origin}/registro-productor/${t}`);
    };

    return (
        <div className="admin-layout">
            <aside className="admin-sidebar">
                <h2>Admin Portal</h2>
                <nav className="admin-nav">
                    <div className={`admin-nav-item ${view === 'overview' ? 'active' : ''}`} onClick={() => setView('overview')}>📊 Resumen General</div>
                    <div className={`admin-nav-item ${view === 'pending' ? 'active' : ''}`} onClick={() => setView('pending')}>⏳ Productores Pendientes ({pending.length})</div>
                    <div className={`admin-nav-item ${view === 'users' ? 'active' : ''}`} onClick={() => setView('users')}>👥 Directorio Usuarios</div>
                </nav>
            </aside>
            <main className="admin-content">
                {view === 'overview' && (
                    <>
                        <h1 className="serif" style={{marginBottom: '32px'}}>Dashboard Admin</h1>
                        <div className="stats-grid-admin">
                            <div className="stat-card"><h4>Usuarios Totales</h4><div className="stat-val">{allUsers.length}</div></div>
                            <div className="stat-card"><h4>Pendientes</h4><div className="stat-val">{pending.length}</div></div>
                            <div className="stat-card"><h4>Estatus</h4><div className="stat-val">Online</div></div>
                        </div>
                        <div className="card">
                            <h3>Gestión de Invitaciones</h3>
                            <button className="btn btn-primary" onClick={generateInvite}>Generar Link Productor</button>
                            {inviteLink && (
                                <div style={{marginTop: '20px', padding: '15px', background: '#fff', border: '1px dashed #296C42', borderRadius: '8px'}}>
                                    <code style={{fontSize: '0.8rem'}}>{inviteLink}</code>
                                    <button className="btn-text" style={{display:'block',marginTop:'5px'}} onClick={() => {navigator.clipboard.writeText(inviteLink); showToast("Link copiado")}}>COPIAR</button>
                                </div>
                            )}
                        </div>
                    </>
                )}
                {view === 'pending' && (
                    <div className="admin-table-container">
                        <table className="admin-table">
                            <thead><tr><th>Productor</th><th>Finca</th><th>WhatsApp</th><th>Acción</th></tr></thead>
                            <tbody>
                                {pending.map(p => (
                                    <tr key={p.id}>
                                        <td>{p.full_name}</td><td>{p.farm_name}</td><td>{p.whatsapp}</td>
                                        <td><button className="btn btn-primary" style={{padding:'5px 10px', fontSize:'0.7rem'}} onClick={() => handleApprove(p.id)}>APROBAR</button></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
                {view === 'users' && (
                    <div className="admin-table-container">
                        <table className="admin-table">
                            <thead><tr><th>Email</th><th>Rol</th><th>Estatus</th></tr></thead>
                            <tbody>
                                {allUsers.map(u => (
                                    <tr key={u.id}>
                                        <td>{u.email}</td><td style={{fontWeight:700}}>{u.role}</td>
                                        <td><span className={`status-tag ${u.is_active ? 'status-active' : 'status-pending'}`}>{u.is_active ? 'Activo' : 'Pendiente'}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </main>
        </div>
    );
};

const ProducerDashboard = ({ user, showToast }) => {
    const [myProducts, setMyProducts] = useState([]);
    const [formData, setFormData] = useState({ name: '', price: '', origin: '', description: '', stock: 100, image_path: '' });
    
    const loadMyProducts = async () => {
        try {
            const allProducts = await getProductsFS();
            setMyProducts(allProducts.filter(p => p.producer_id === user?.uid));
        } catch (e) { console.error(e); }
    };
    
    useEffect(() => { if (user) loadMyProducts(); }, [user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await createProductFS({
                name: formData.name,
                price: parseFloat(formData.price),
                origin: formData.origin,
                description: formData.description,
                stock: parseInt(formData.stock),
                is_active: true,
                image_path: formData.image_path || null
            }, user.uid);
            showToast("Producto subido exitosamente a la tienda", "success");
            setFormData({ name: '', price: '', origin: '', description: '', stock: 100, image_path: '' });
            loadMyProducts();
        } catch (e) {
            showToast("Error al subir el producto", "error");
        }
    };
    
    const handleDelete = async (id) => {
        try {
            await deleteProductFS(id);
            showToast("Producto eliminado", "success");
            loadMyProducts();
        } catch (e) { showToast("Error", "error"); }
    };

    return (
        <div className="admin-layout">
            <aside className="admin-sidebar" style={{background: '#3E2723'}}>
                <h2>Mi Finca</h2>
                <nav className="admin-nav">
                    <div className="admin-nav-item active">☕ Mis Productos</div>
                    <div className="admin-nav-item">📦 Pedidos Entrantes</div>
                </nav>
            </aside>
            <main className="admin-content">
                <h1 className="serif" style={{marginBottom: '32px'}}>Gestión de Cosecha</h1>
                
                <div style={{display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '40px', alignItems: 'start'}}>
                    {/* Add Product Form */}
                    <div className="card" style={{background: '#fff', padding: '24px', borderRadius: '12px', boxShadow: 'var(--shadow-soft)'}}>
                        <h3 style={{marginBottom: '20px'}}>Publicar Nuevo Lote</h3>
                        <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                            <div><label style={{fontSize: '0.8rem', fontWeight: 600}}>Nombre del Café</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #ccc', borderRadius:'4px'}} required value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})} /></div>
                            <div><label style={{fontSize: '0.8rem', fontWeight: 600}}>Precio (USD)</label><input type="number" step="0.01" className="full-width" style={{padding: '10px', border: '1px solid #ccc', borderRadius:'4px'}} required value={formData.price} onChange={e=>setFormData({...formData, price: e.target.value})} /></div>
                            <div><label style={{fontSize: '0.8rem', fontWeight: 600}}>Origen Específico</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #ccc', borderRadius:'4px'}} required value={formData.origin} onChange={e=>setFormData({...formData, origin: e.target.value})} /></div>
                            <div><label style={{fontSize: '0.8rem', fontWeight: 600}}>Descripción</label><textarea className="full-width" style={{padding: '10px', border: '1px solid #ccc', borderRadius:'4px'}} required value={formData.description} onChange={e=>setFormData({...formData, description: e.target.value})}></textarea></div>
                            <div><label style={{fontSize: '0.8rem', fontWeight: 600}}>URL de Imagen (Opcional)</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #ccc', borderRadius:'4px'}} value={formData.image_path} onChange={e=>setFormData({...formData, image_path: e.target.value})} placeholder="https://..." /></div>
                            <button type="submit" className="btn btn-primary">SUBIR PRODUCTO</button>
                        </form>
                    </div>

                    {/* Products List */}
                    <div>
                        <h3 style={{marginBottom: '20px'}}>Lotes Activos ({myProducts.length})</h3>
                        <div className="admin-table-container">
                            <table className="admin-table">
                                <thead><tr><th>Nombre</th><th>Origen</th><th>Precio</th><th>Stock</th><th>Acción</th></tr></thead>
                                <tbody>
                                    {myProducts.length === 0 ? <tr><td colSpan="5" style={{textAlign: 'center'}}>No has publicado productos</td></tr> :
                                    myProducts.map(p => (
                                        <tr key={p.id}>
                                            <td><strong style={{fontFamily: 'var(--font-serif)'}}>{p.name}</strong></td>
                                            <td>{p.origin}</td><td>${p.price}</td><td>{p.stock} lbs</td>
                                            <td><button className="btn btn-outline" style={{padding:'4px 8px', fontSize:'0.7rem', color: '#D32F2F', borderColor: '#D32F2F'}} onClick={() => handleDelete(p.id)}>BORRAR</button></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

const ProducerRegistrationView = ({ showToast }) => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        email: '', password: '', full_name: '', farm_name: '', region: 'Antioquia', whatsapp: '', description: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
            await saveUserProfile(userCredential.user.uid, { ...formData, role: 'PRODUCTOR', password: null });
            showToast("Perfil enviado satisfactoriamente.", "success");
            navigate('/login');
        } catch (e) { showToast(e.message, "error"); }
    };

    return (
        <div className="onboarding-container" style={{marginTop: '100px'}}>
            <h1 className="serif">Registro de Productor</h1>
            <p>Sus datos serán procesados por la administración central.</p>
            <form onSubmit={handleSubmit}>
                <div className="form-grid">
                    <div className="input-group"><label>Email</label><input type="email" required onChange={e => setFormData({...formData, email: e.target.value})} /></div>
                    <div className="input-group"><label>Password</label><input type="password" required onChange={e => setFormData({...formData, password: e.target.value})} /></div>
                    <div className="input-group"><label>Productor</label><input type="text" required onChange={e => setFormData({...formData, full_name: e.target.value})} /></div>
                    <div className="input-group"><label>Finca</label><input type="text" required onChange={e => setFormData({...formData, farm_name: e.target.value})} /></div>
                    <div className="input-group"><label>WhatsApp</label><input type="text" required onChange={e => setFormData({...formData, whatsapp: e.target.value})} /></div>
                    <div className="input-group form-span-2 textarea-group"><label>Bio</label><textarea required onChange={e => setFormData({...formData, description: e.target.value})}></textarea></div>
                </div>
                <button type="submit" className="btn btn-primary full-width" style={{marginTop:'20px'}}>ENVIAR SOLICITUD</button>
            </form>
        </div>
    );
};

const NavHeader = ({ role, user, cartCount, onLogout }) => (
    <header className="navbar">
        <Link to="/" className="logo-btn">The Artisanal Connection</Link>
        <nav className="nav-links">
            <Link to="/" className="nav-item">Catálogo</Link>
            <Link to="/productores" className="nav-item">Productores</Link>
            <Link to="/origen" className="nav-item">Origen</Link>
            {role === 'ADMIN' && <Link to="/admin" className="nav-item" style={{color: 'var(--accent-green)', fontWeight: 700}}>⚙️ PANEL ADMIN</Link>}
            {role === 'PRODUCTOR' && <Link to="/productor" className="nav-item" style={{color: 'var(--accent-green)', fontWeight: 700}}>☕ PANEL PRODUCTOR</Link>}
        </nav>
        <div style={{display: 'flex', alignItems: 'center', gap: '24px'}}>
            {role !== 'ADMIN' && (
                <button className="cart-icon-btn">🛒<span className="cart-badge" style={{display: cartCount > 0 ? 'inline-block' : 'none'}}>{cartCount}</span></button>
            )}
            <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                {user ? (
                    <>
                        <div style={{width: '36px', height: '36px', borderRadius: '50%', background: '#ccc', overflow: 'hidden'}}><img src={user.photoURL || "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&q=80"} style={{width: '100%', height: '100%', objectFit: 'cover'}} alt="user"/></div>
                        <button className="btn-text" onClick={onLogout} style={{fontSize: '0.8rem', fontWeight: 600}}>SALIR</button>
                    </>
                ) : <Link to="/login" className="btn btn-primary" style={{padding: '8px 16px', fontSize: '0.8rem', textDecoration: 'none'}}>INICIAR SESIÓN</Link>}
            </div>
        </div>
    </header>
);

function AppContent() {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [currentProductId, setCurrentProductId] = useState(null);
    const [cartData, setCartData] = useState({ items: [], total: 0 });
    const [cartOpen, setCartOpen] = useState(false);
    const [toasts, setToasts] = useState([]);
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
            try {
                if (firebaseUser) {
                    console.log("DEBUG Auth: Reconnecting user", firebaseUser.email);
                    const profile = await getUserProfile(firebaseUser.uid);
                    const token = await firebaseUser.getIdToken();
                    setUser({...firebaseUser, ...profile});
                    setToken(token);
                    setRole(profile?.role || 'COMPRADOR');
                } else {
                    setUser(null);
                    setRole(null);
                }
            } catch (err) {
                console.error("DEBUG Auth Persistence Error:", err);
            } finally {
                setLoading(false);
            }
        });
        // Fallback: If after 5 seconds we are still loading, force it to false
        const timer = setTimeout(() => setLoading(false), 5000);
        return () => { unsubscribe(); clearTimeout(timer); };
    }, []);

    useEffect(() => {
        const init = async () => {
            try { const data = await getProductsFS(); setProducts(data); } catch (e) { console.error(e); }
        };
        init();
    }, []);

    const showToast = (message, type = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type, show: false }]);
        setTimeout(() => setToasts(prev => prev.map(t => t.id === id ? { ...t, show: true } : t)), 10);
        setTimeout(() => {
            setToasts(prev => prev.map(t => t.id === id ? { ...t, show: false } : t));
            setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 400);
        }, 4000);
    };

    const handleLogin = async (loggedUser, authToken, userRole) => {
        if (loggedUser.is_active === false && userRole === 'PRODUCTOR') {
            showToast("Su cuenta está pendiente de aprobación.", "error"); 
            return;
        }

        console.log("DEBUG handleLogin: Setting user and role:", userRole);
        setUser(loggedUser); 
        setToken(authToken); 
        setRole(userRole);
        
        // Fast navigation
        if (userRole === 'ADMIN') navigate('/admin');
        else if (userRole === 'PRODUCTOR') navigate('/productor');
        else navigate('/');
        
        showToast("Sesión iniciada correctamente");
    };

    useEffect(() => {
        if (user && role) {
            console.log("DEBUG App Navigation: User is logged in as", role);
            // If the user lands on login but is already logged in, move them to their dashboard
            if (window.location.pathname === '/login') {
                if (role === 'ADMIN') navigate('/admin');
                else if (role === 'PRODUCTOR') navigate('/productor');
                else navigate('/');
            }
        }
    }, [user, role, navigate]);

    const handleLogout = () => { setUser(null); setToken(null); setRole(null); navigate('/'); showToast("Adiós!"); };

    const handleAddToCart = async (variantId, quantity) => {
        if (!user) { navigate('/login'); return; }
        try {
            await addToCart(variantId, quantity, user.uid || 1, token);
            showToast("Añadido!");
            const data = await getCart(user.uid || 1, token);
            setCartData(data);
            setCartOpen(true);
        } catch (err) { showToast("Error", "error"); }
    };

    if (loading) return <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'var(--font-serif)', color: 'var(--accent-green)'}}><h2>Cargando Patrimonio Cafetero...</h2></div>;

    return (
        <>
            <div className="toast-container">{toasts.map(t => (<div key={t.id} className={`toast toast-${t.type} ${t.show ? 'show' : ''}`}><span>{t.message}</span></div>))}</div>
            <Routes>
                <Route path="/login" element={<LoginView onLogin={handleLogin} showToast={showToast} />} />
                <Route path="/admin" element={role === 'ADMIN' ? <AdminDashboard token={token} showToast={showToast} /> : (user ? null : <Navigate to="/login" />)} />
                <Route path="/productor" element={role === 'PRODUCTOR' ? <ProducerDashboard user={user} showToast={showToast} /> : (user ? null : <Navigate to="/login" />)} />
                <Route path="/registro-productor/:token" element={<ProducerRegistrationView showToast={showToast} />} />
                <Route path="*" element={
                    <>
                        <NavHeader role={role} user={user} cartCount={cartData.items?.length || 0} onLogout={handleLogout} />
                        <main>
                            <Routes>
                                <Route path="/" element={<CatalogView products={products} onSelectProduct={(id) => {setCurrentProductId(id); navigate(`/product/${id}`)}} getProductImage={getProductImage} />} />
                                <Route path="/product/:id" element={<ProductDetailView product={products.find(p => p.id === currentProductId)} onBack={() => navigate('/')} onAddToCart={handleAddToCart} getProductImage={getProductImage} />} />
                                <Route path="/productores" element={<ProducersView />} />
                                <Route path="/origen" element={<OriginView />} />
                                <Route path="*" element={<Navigate to="/" />} />
                            </Routes>
                        </main>
                    </>
                } />
            </Routes>
            <div className={`cart-drawer ${cartOpen ? 'open' : ''}`}>
                <div className="cart-overlay" onClick={() => setCartOpen(false)}></div>
                <div className="cart-panel"><div className="cart-header"><h2>Carrito</h2><button onClick={() => setCartOpen(false)}>×</button></div><div className="cart-footer"><button className="btn btn-primary full-width" onClick={() => showToast("Checkout...")}>Pagar</button></div></div>
            </div>
        </>
    );
}

export default function App() { 
    return (
        <ErrorBoundary>
            <Router><AppContent /></Router>
        </ErrorBoundary>
    ); 
}

