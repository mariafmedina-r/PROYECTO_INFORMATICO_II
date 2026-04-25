import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate, useParams } from 'react-router-dom';
import { getProductsFS, createProductFS, deleteProductFS, updateProductFS, getCart, addToCart, checkoutContext, getPendingProducersFS, approveProducerFS, saveUserProfile, getUserProfile, getAllUsersFS, upgradeToProducerFS, toggleUserStatusFS } from './api';
import LoginView from './components/LoginView';
import CatalogView from './components/CatalogView';
import ProductDetailView from './components/ProductDetailView';
import ProducersView from './components/ProducersView';
import OriginView from './components/OriginView';
import { getProductImage } from './utils';
import { auth } from './firebase_config';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import PaymentModal from './components/PaymentModal';

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
    const [allUsers, setAllUsers] = useState([]);
    const [allProducts, setAllProducts] = useState([]);

    const loadData = async () => {
        try {
            const u = await getAllUsersFS(); setAllUsers(u);
            const p = await getProductsFS(); setAllProducts(p);
        } catch (e) { console.error(e); }
    };

    useEffect(() => { loadData(); }, [token]);

    const handleToggleUser = async (uid, status) => {
        try {
            await toggleUserStatusFS(uid, status);
            showToast(status ? "Usuario suspendido" : "Usuario activado", "success");
            loadData();
        } catch (e) { showToast("Error", "error"); }
    };

    const handleDeleteProduct = async (id) => {
        try {
            await deleteProductFS(id);
            showToast("Producto eliminado por administración", "success");
            loadData();
        } catch (e) { showToast("Error", "error"); }
    };

    return (
        <div className="admin-layout">
            <aside className="admin-sidebar" style={{background: '#263238'}}>
                <div style={{padding: '30px 20px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px'}}>
                    <h2 style={{fontSize: '1.2rem', color: '#fff', letterSpacing: '1px'}}>CONTROL CENTRAL</h2>
                </div>
                <nav className="admin-nav">
                    <div className={`admin-nav-item ${view === 'overview' ? 'active' : ''}`} onClick={() => setView('overview')}>📊 Dashboard</div>
                    <div className={`admin-nav-item ${view === 'users' ? 'active' : ''}`} onClick={() => setView('users')}>👥 Usuarios</div>
                    <div className={`admin-nav-item ${view === 'products' ? 'active' : ''}`} onClick={() => setView('products')}>🛒 Inventario Global</div>
                </nav>
            </aside>
            <main className="admin-content" style={{background: '#F5F7F8'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px'}}>
                    <h1 className="serif">{view === 'overview' ? 'Resumen Ejecutivo' : view === 'users' ? 'Gestión de Usuarios' : 'Inventario Maestro'}</h1>
                    <button className="btn btn-outline" onClick={loadData} style={{fontSize: '0.8rem'}}>🔄 ACTUALIZAR DATOS</button>
                </div>
                
                {view === 'overview' && (
                    <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px'}}>
                        <div className="stat-card" style={{borderLeft: '5px solid #607D8B', background: '#fff'}}>
                            <span style={{fontSize: '0.7rem', color: '#666', fontWeight: 700}}>USUARIOS TOTALES</span>
                            <div className="stat-val" style={{color: '#263238'}}>{allUsers.length}</div>
                        </div>
                        <div className="stat-card" style={{borderLeft: '5px solid #4CAF50', background: '#fff'}}>
                            <span style={{fontSize: '0.7rem', color: '#666', fontWeight: 700}}>LOTES DE CAFÉ</span>
                            <div className="stat-val" style={{color: '#263238'}}>{allProducts.length}</div>
                        </div>
                        <div className="stat-card" style={{borderLeft: '5px solid #FF9800', background: '#fff'}}>
                            <span style={{fontSize: '0.7rem', color: '#666', fontWeight: 700}}>INFRAESTRUCTURA</span>
                            <div className="stat-val" style={{fontSize: '1.2rem', color: '#4CAF50', paddingTop: '10px'}}>ESTABLE</div>
                        </div>
                    </div>
                )}

                {view === 'users' && (
                    <div className="card shadow-soft" style={{background: '#fff', borderRadius: '16px', overflow: 'hidden'}}>
                        <table className="admin-table">
                            <thead style={{background: '#f8f9fa'}}>
                                <tr><th>USUARIO / EMAIL</th><th>ROL</th><th>WHATSAPP</th><th>ESTADO</th><th>ACCIONES</th></tr>
                            </thead>
                            <tbody>
                                {allUsers.map(u => (
                                    <tr key={u.id}>
                                        <td><strong>{u.email}</strong><br/><small style={{color: '#999'}}>{u.id}</small></td>
                                        <td><span className={`role-tag role-${u.role?.toLowerCase()}`}>{u.role}</span></td>
                                        <td>{u.whatsapp ? <a href={`https://wa.me/${u.whatsapp}`} target="_blank" rel="noreferrer" style={{color: '#25D366', fontWeight: 600}}>💬 {u.whatsapp}</a> : '—'}</td>
                                        <td><span className={`status-tag ${u.is_active ? 'status-active' : 'status-pending'}`}>{u.is_active ? 'Activo' : 'Suspendido'}</span></td>
                                        <td>
                                            <button className={`btn ${u.is_active ? 'btn-outline-danger' : 'btn-primary'}`} style={{padding: '6px 12px', fontSize: '0.75rem'}} onClick={() => handleToggleUser(u.id, u.is_active)}>
                                                {u.is_active ? 'DESACTIVAR' : 'ACTIVAR'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
                
                {view === 'products' && (
                    <div className="card shadow-soft" style={{background: '#fff', borderRadius: '16px', overflow: 'hidden'}}>
                        <table className="admin-table">
                            <thead style={{background: '#f8f9fa'}}>
                                <tr><th>LOTE</th><th>PRODUCTOR</th><th>PRECIO</th><th>STOCK</th><th>ACCIONES</th></tr>
                            </thead>
                            <tbody>
                                {allProducts.map(p => (
                                    <tr key={p.id}>
                                        <td><strong>{p.name}</strong></td>
                                        <td><small>{p.farm_name || p.producer_id}</small></td>
                                        <td>${p.price}</td>
                                        <td>{p.stock}</td>
                                        <td><button className="btn-text" style={{color: 'red', fontWeight: 700}} onClick={() => handleDeleteProduct(p.id)}>ELIMINAR</button></td>
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

const ProducerDashboard = ({ user, showToast, refreshGlobalProducts, refreshProfile, role }) => {
    const [view, setView] = useState('products');
    const [productTab, setProductTab] = useState('active'); // active | inactive
    const [myProducts, setMyProducts] = useState([]);
    const [formData, setFormData] = useState({ 
        name: '', price: '', origin: '', description: '', stock: 100, image_path: '',
        sensory_notes: '', altitude: '', process: 'Lavado', is_exclusive: false
    });
    const [editingProduct, setEditingProduct] = useState(null);
    const [fileError, setFileError] = useState('');
    
    const [profileForm, setProfileForm] = useState({
        full_name: '', farm_name: '', region: '', whatsapp: '', description: ''
    });

    useEffect(() => {
        if (user) {
            setProfileForm({
                full_name: user.full_name || '',
                farm_name: user.farm_name || '',
                region: user.region || '',
                whatsapp: user.whatsapp || '',
                description: user.description || ''
            });
        }
    }, [user]);

    const loadMyProducts = async () => {
        try {
            const allProducts = await getProductsFS();
            setMyProducts(allProducts.filter(p => p.producer_id === user?.uid));
        } catch (e) { console.error(e); }
    };
    
    useEffect(() => { if (user) loadMyProducts(); }, [user]);

    const handleFileChange = (e) => {
        const url = e.target.value;
        setFormData({ ...formData, image_path: url });
        if (url && !url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
            setFileError('Tipo de archivo no permitido. Use imágenes (jpg, png, webp).');
        } else {
            setFileError('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...formData,
                price: parseFloat(formData.price),
                stock: parseInt(formData.stock),
                is_active: editingProduct ? editingProduct.is_active : true,
                farm_name: user.farm_name
            };

            if (editingProduct) {
                await updateProductFS(editingProduct.id, payload);
                showToast("Producto actualizado", "success");
            } else {
                await createProductFS(payload, user.uid);
                showToast("Lote publicado exitosamente", "success");
            }

            setFormData({ 
                name: '', price: '', origin: '', description: '', stock: 100, image_path: '',
                sensory_notes: '', altitude: '', process: 'Lavado', is_exclusive: false
            });
            setEditingProduct(null);
            loadMyProducts();
            if (refreshGlobalProducts) refreshGlobalProducts();
        } catch (e) { showToast("Error al procesar el producto", "error"); }
    };

    const handleEdit = (p) => {
        setEditingProduct(p);
        setFormData({
            name: p.name || '', price: p.price || '', origin: p.origin || '', description: p.description || '', stock: p.stock || 100, image_path: p.image_path || '', sensory_notes: p.sensory_notes || '', altitude: p.altitude || '', process: p.process || 'Lavado', is_exclusive: p.is_exclusive || false
        });
        showToast("Editando: " + p.name, "info");
    };

    const handleToggleStatus = async (product) => {
        try {
            const newStatus = !product.is_active;
            await updateProductFS(product.id, { is_active: newStatus });
            showToast(newStatus ? "Lote Activado" : "Lote Pausado", "success");
            loadMyProducts();
            if (refreshGlobalProducts) refreshGlobalProducts();
        } catch (e) { showToast("Error", "error"); }
    };

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        try {
            await saveUserProfile(user.uid, profileForm);
            showToast("Perfil actualizado", "success");
            if (refreshProfile) await refreshProfile();
        } catch (e) { showToast("Error", "error"); }
    };

    const filteredProducts = myProducts.filter(p => productTab === 'active' ? p.is_active !== false : p.is_active === false);

    return (
        <div className="admin-layout">
            <aside className="admin-sidebar" style={{background: '#3d2b1f'}}>
                <div style={{padding: '30px 20px', textAlign: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px'}}>
                    <div style={{width: '60px', height: '60px', borderRadius: '50%', background: 'rgba(255,255,255,0.1)', margin: '0 auto 15px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem'}}>🏞️</div>
                    <h3 style={{color: '#fff', fontSize: '0.9rem', textTransform: 'uppercase'}}>{user?.farm_name || 'Mi Finca'}</h3>
                </div>
                <nav className="admin-nav">
                    <div className={`admin-nav-item ${view === 'products' ? 'active' : ''}`} onClick={() => setView('products')}>☕ Mis Cosechas</div>
                    <div className={`admin-nav-item ${view === 'orders' ? 'active' : ''}`} onClick={() => setView('orders')}>📦 Pedidos Entrantes</div>
                    <div className={`admin-nav-item ${view === 'profile' ? 'active' : ''}`} onClick={() => setView('profile')}>👤 Mi Perfil Comercial</div>
                </nav>
            </aside>
            <main className="admin-content" style={{background: '#FAF9F6'}}>
                <h1 className="serif" style={{marginBottom: '32px'}}>
                    {view === 'products' ? 'Gestión de Cosecha' : view === 'orders' ? 'Pedidos Recibidos' : 'Perfil Comercial'}
                </h1>
                
                {view === 'products' && (
                    <div style={{display: 'grid', gridTemplateColumns: 'minmax(350px, 1.2fr) 2fr', gap: '30px', alignItems: 'start'}}>
                        <div className="card shadow-soft" style={{background: '#fff', padding: '24px', borderRadius: '12px'}}>
                            <h3 style={{marginBottom: '20px'}}>{editingProduct ? '✏️ Editar Lote' : '➕ Publicar Nuevo Lote'}</h3>
                            <form onSubmit={handleSubmit} style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
                                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px'}}>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Nombre del Café</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} required value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})} /></div>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Precio (USD)</label><input type="number" step="0.01" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} required value={formData.price} onChange={e=>setFormData({...formData, price: e.target.value})} /></div>
                                </div>
                                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px'}}>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Región/Origen</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} required value={formData.origin} onChange={e=>setFormData({...formData, origin: e.target.value})} /></div>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Stock (Unidades)</label><input type="number" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} required value={formData.stock} onChange={e=>setFormData({...formData, stock: e.target.value})} /></div>
                                </div>
                                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'12px'}}>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Altitud (msnm)</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} placeholder="Ej: 1850" value={formData.altitude} onChange={e=>setFormData({...formData, altitude: e.target.value})} /></div>
                                    <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Proceso</label>
                                        <select className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} value={formData.process} onChange={e=>setFormData({...formData, process: e.target.value})}>
                                            <option value="Lavado">Lavado</option>
                                            <option value="Natural">Natural</option>
                                            <option value="Honey">Honey</option>
                                            <option value="Anaeróbico">Anaeróbico</option>
                                        </select>
                                    </div>
                                </div>
                                <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Notas Sensoriales</label><input type="text" className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px'}} placeholder="Ej: Cacao, Cítrico, Dulce" value={formData.sensory_notes} onChange={e=>setFormData({...formData, sensory_notes: e.target.value})} /></div>
                                <div><label style={{fontSize: '0.75rem', fontWeight: 600}}>Descripción</label><textarea className="full-width" style={{padding: '10px', border: '1px solid #eee', borderRadius:'4px', minHeight: '80px'}} required value={formData.description} onChange={e=>setFormData({...formData, description: e.target.value})}></textarea></div>
                                <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
                                    <input type="checkbox" id="exclusive" checked={formData.is_exclusive} onChange={e=>setFormData({...formData, is_exclusive: e.target.checked})} />
                                    <label htmlFor="exclusive" style={{fontSize: '0.75rem', cursor: 'pointer'}}>Región Exclusiva 🌟</label>
                                </div>
                                <div style={{display: 'flex', gap: '10px'}}>
                                    <button type="submit" className="btn btn-primary" style={{flex: 1}}>{editingProduct ? 'GUARDAR CAMBIOS' : 'PUBLICAR LOTE'}</button>
                                    {editingProduct && <button type="button" className="btn btn-outline" onClick={()=>setEditingProduct(null)}>CANCELAR</button>}
                                </div>
                            </form>
                        </div>
                        <div>
                            <div style={{display: 'flex', gap: '20px', marginBottom: '20px', borderBottom: '1px solid #eee'}}>
                                <button className={`btn-text ${productTab === 'active' ? 'active-tab' : ''}`} style={{paddingBottom: '15px', fontWeight: 700, color: productTab === 'active' ? '#3d2b1f' : '#999'}} onClick={()=>setProductTab('active')}>EN VENTA</button>
                                <button className={`btn-text ${productTab === 'inactive' ? 'active-tab' : ''}`} style={{paddingBottom: '15px', fontWeight: 700, color: productTab === 'inactive' ? '#3d2b1f' : '#999'}} onClick={()=>setProductTab('inactive')}>PAUSADOS</button>
                            </div>
                            <div className="admin-table-container shadow-soft" style={{background: '#fff', borderRadius: '12px', overflow: 'hidden'}}>
                                <table className="admin-table">
                                    <thead><tr><th>Lote</th><th>Características</th><th>Stock</th><th>Acciones</th></tr></thead>
                                    <tbody>
                                        {filteredProducts.map(p => (
                                            <tr key={p.id}>
                                                <td><strong className="serif">{p.name}</strong><br/><small style={{color:'var(--accent-green)', fontWeight:700}}>${p.price}</small></td>
                                                <td>
                                                    <div style={{fontSize:'0.7rem', color:'#666'}}>
                                                        <div>{p.origin} • {p.process}</div>
                                                        <div>{p.altitude} msnm</div>
                                                    </div>
                                                </td>
                                                <td><span style={{fontWeight:700, color: p.stock < 10 ? 'red' : 'inherit'}}>{p.stock <= 0 ? 'AGOTADO' : `${p.stock} un.`}</span></td>
                                                <td style={{display:'flex', gap:'8px'}}>
                                                    <button className="btn-icon" onClick={()=>handleEdit(p)}>✏️</button>
                                                    <button className="btn-icon" onClick={()=>handleToggleStatus(p)}>{p.is_active ? '⏸️' : '▶️'}</button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                {view === 'orders' && (
                    <div className="card shadow-soft" style={{background: '#fff', padding: '40px', borderRadius: '12px', textAlign: 'center'}}>
                        <h3>No hay pedidos entrantes</h3>
                        <p style={{color: '#666'}}>Aquí aparecerán las ventas realizadas.</p>
                    </div>
                )}

                {view === 'profile' && (
                    <div style={{maxWidth: '800px'}}>
                        <div className="card shadow-soft" style={{background: '#fff', padding: '32px', borderRadius: '12px'}}>
                            <h3 style={{marginBottom: '24px'}}>Mi Perfil Comercial</h3>
                            <form onSubmit={handleSaveProfile} style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
                                <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'20px'}}>
                                    <div><label style={{fontSize:'0.85rem', fontWeight:600}}>Productor</label><input type="text" className="full-width" style={{padding:'10px', border:'1px solid #ddd', borderRadius:'6px', marginTop:'5px'}} value={profileForm.full_name} onChange={e=>setProfileForm({...profileForm, full_name: e.target.value})} /></div>
                                    <div><label style={{fontSize:'0.85rem', fontWeight:600}}>WhatsApp</label><input type="text" className="full-width" style={{padding:'10px', border:'1px solid #ddd', borderRadius:'6px', marginTop:'5px'}} value={profileForm.whatsapp} onChange={e=>setProfileForm({...profileForm, whatsapp: e.target.value})} /></div>
                                </div>
                                <div style={{display:'flex', justifyContent:'flex-end'}}><button type="submit" className="btn btn-primary">GUARDAR PERFIL</button></div>
                            </form>
                        </div>
                    </div>
                )}
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

const UpgradeToProducerView = ({ user, setRole, showToast }) => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        full_name: '', farm_name: '', region: 'Antioquia', whatsapp: '', description: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await upgradeToProducerFS(user.uid, formData);
            showToast("¡Felicidades! Su perfil de productor ha sido habilitado inmediatamente.", "success");
            setRole('PRODUCTOR');
            navigate('/productor');
        } catch (e) { showToast(e.message, "error"); }
    };

    return (
        <div className="onboarding-container" style={{marginTop: '100px'}}>
            <h1 className="serif">Convertirse en Productor</h1>
            <p>Aplique para vender sus mejores productos en nuestra plataforma.</p>
            <form onSubmit={handleSubmit}>
                <div className="form-grid">
                    <div className="input-group"><label>Nombre Completo</label><input type="text" required onChange={e => setFormData({...formData, full_name: e.target.value})} /></div>
                    <div className="input-group"><label>Nombre de la Finca</label><input type="text" required onChange={e => setFormData({...formData, farm_name: e.target.value})} /></div>
                    <div className="input-group"><label>Región</label><input type="text" required onChange={e => setFormData({...formData, region: e.target.value})} /></div>
                    <div className="input-group"><label>WhatsApp</label><input type="text" required onChange={e => setFormData({...formData, whatsapp: e.target.value})} /></div>
                    <div className="input-group form-span-2 textarea-group"><label>Historia de su café</label><textarea required onChange={e => setFormData({...formData, description: e.target.value})}></textarea></div>
                </div>
                <button type="submit" className="btn btn-primary full-width" style={{marginTop:'20px'}}>ENVIAR SOLICITUD DE PRODUCTOR</button>
            </form>
        </div>
    );
};

const NavHeader = ({ role, user, cartCount, onLogout, onOpenCart }) => (
    <header className="navbar">
        <Link to="/" className="logo-btn">The Artisanal Connection</Link>
        <nav className="nav-links">
            <Link to="/" className="nav-item">Catálogo</Link>
            <Link to="/productores" className="nav-item">Productores</Link>
            <Link to="/origen" className="nav-item">Origen</Link>
            {role === 'ADMIN' && <Link to="/admin" className="nav-item" style={{color: 'var(--accent-green)', fontWeight: 700}}>⚙️ PANEL ADMIN</Link>}
            {role === 'PRODUCTOR' && <Link to="/productor" className="nav-item" style={{color: 'var(--accent-green)', fontWeight: 700}}>☕ PANEL PRODUCTOR</Link>}
            {role === 'COMPRADOR' && <Link to="/aplicar-productor" className="nav-item" style={{color: '#8D6E63', fontWeight: 600}}>🌱 Quiero vender</Link>}
        </nav>
        <div style={{display: 'flex', alignItems: 'center', gap: '24px'}}>
            {(role === 'COMPRADOR' || !user) && (
                <button className="cart-icon-btn" onClick={onOpenCart}>
                    🛒<span className="cart-badge" style={{display: cartCount > 0 ? 'inline-block' : 'none'}}>{cartCount}</span>
                </button>
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

const ProductDetailWrapper = ({ products, onBack, onAddToCart, getProductImage, role }) => {
    const { id } = useParams();
    const product = products.find(p => p.id === id || p.id === parseInt(id));
    return <ProductDetailView product={product} onBack={onBack} onAddToCart={onAddToCart} getProductImage={getProductImage} role={role} />;
};

function AppContent() {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [currentProductId, setCurrentProductId] = useState(null);
    const [cartData, setCartData] = useState({ items: [], total: 0 });
    const [cartOpen, setCartOpen] = useState(false);
    const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
    const [toasts, setToasts] = useState([]);
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [role, setRole] = useState(null);
    const [loading, setLoading] = useState(true);

    // [SISTEMA DE LOGIN] Hooks de Persistencia y Detección de Identidad
    // onAuthStateChanged verifica continuamente el LocalStorage de Firebase 
    // para reconectar sesiones sin pedir credenciales cada que se recarga la página.
    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
            try {
                if (firebaseUser) {
                    console.log("DEBUG Auth: Reconnecting user", firebaseUser.email);
                    // Petición a base de datos de Firestore
                    const profile = await getUserProfile(firebaseUser.uid);
                    const token = await firebaseUser.getIdToken();
                    
                    // Inyección forzada de seguridad para QA/Desarrollo ('ADMIN' pre-configurado)
                    const adminEmails = ['admin@patrimoniocafetero.com', 'test@example.com'];
                    const finalRole = profile?.role || (adminEmails.includes(firebaseUser.email?.toLowerCase()) ? 'ADMIN' : 'COMPRADOR');
                    
                    console.log("DEBUG Auth: Role identified as", finalRole);
                    // Seteamos el estado local global (`user`, `token`, `role`)
                    setUser({...firebaseUser, ...profile});
                    setToken(token);
                    setRole(finalRole);
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

    const refreshGlobalProducts = async () => {
        try { const data = await getProductsFS(); setProducts(data); } catch (e) { console.error(e); }
    };

    const refreshProfile = async () => {
        if (auth.currentUser) {
            try {
                const profile = await getUserProfile(auth.currentUser.uid);
                setUser(prev => ({...prev, ...profile}));
            } catch (e) { console.error("Error refreshing profile:", e); }
        }
    };

    useEffect(() => {
        refreshGlobalProducts();
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

    const handleLogout = () => { auth.signOut(); setUser(null); setToken(null); setRole(null); navigate('/'); showToast("Adiós!"); };

    // [INACTIVITY TIMEOUT]
    useEffect(() => {
        let inactivityTimer;
        const resetTimer = () => {
            clearTimeout(inactivityTimer);
            if (user) {
                inactivityTimer = setTimeout(() => {
                    handleLogout();
                    showToast("Sesión cerrada por inactividad (5 min)", "warning");
                }, 5 * 60 * 1000);
            }
        };

        window.addEventListener('mousemove', resetTimer);
        window.addEventListener('keydown', resetTimer);
        window.addEventListener('click', resetTimer);
        window.addEventListener('scroll', resetTimer);

        resetTimer();

        return () => {
            clearTimeout(inactivityTimer);
            window.removeEventListener('mousemove', resetTimer);
            window.removeEventListener('keydown', resetTimer);
            window.removeEventListener('click', resetTimer);
            window.removeEventListener('scroll', resetTimer);
        };
    }, [user]);

    const handleAddToCart = async (product, quantity) => {
        if (!user) { navigate('/login'); showToast("Inicia sesión para poder comprar", "warning"); return; }
        try {
            showToast("¡Añadido al carrito!", "success");
            setCartData(prev => {
                const existing = prev.items.find(i => i.product.id === product.id);
                let newItems;
                if (existing) {
                    newItems = prev.items.map(i => i.product.id === product.id ? {...i, quantity: i.quantity + quantity} : i);
                } else {
                    const price = parseFloat(product.price) || (product.variants?.length ? product.variants[0].price : 0);
                    newItems = [...prev.items, { product, quantity, price }];
                }
                const newTotal = newItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
                return { items: newItems, total: newTotal };
            });
            setCartOpen(true);
        } catch (err) { showToast("Error", "error"); }
    };

    const handlePaymentSuccess = (paymentResponse) => {
        setIsPaymentModalOpen(false);
        showToast("✅ ¡Pago Exitoso! Tu pedido #" + paymentResponse.id + " está en camino.", "success");
        setCartData({ items: [], total: 0 });
        setCartOpen(false);
    };

    const handlePaymentError = (error) => {
        console.error("Payment Error:", error);
        showToast("❌ Hubo un problema con el pago: " + (error.message || "Rechazado"), "error");
    };

    const updateCartItemQuantity = (productId, delta) => {
        setCartData(prev => {
            const newItems = prev.items.map(item => {
                if (item.product.id === productId) {
                    return { ...item, quantity: Math.max(1, item.quantity + delta) };
                }
                return item;
            });
            const newTotal = newItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
            return { items: newItems, total: newTotal };
        });
    };

    const removeFromCart = (productId) => {
        setCartData(prev => {
            const newItems = prev.items.filter(item => item.product.id !== productId);
            const newTotal = newItems.reduce((acc, item) => acc + (item.price * item.quantity), 0);
            return { items: newItems, total: newTotal };
        });
    };

    if (loading) return <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'var(--font-serif)', color: 'var(--accent-green)'}}><h2>Cargando Patrimonio Cafetero...</h2></div>;

    return (
        <>
            <div className="toast-container">{toasts.map(t => (<div key={t.id} className={`toast toast-${t.type} ${t.show ? 'show' : ''}`}><span>{t.message}</span></div>))}</div>
            
            <PaymentModal 
                isOpen={isPaymentModalOpen} 
                amount={cartData.total} 
                payerEmail={user?.email}
                onClose={() => setIsPaymentModalOpen(false)}
                onPaymentSuccess={handlePaymentSuccess}
                onPaymentError={handlePaymentError}
            />
            
            <Routes>
                <Route path="/login" element={<LoginView onLogin={handleLogin} showToast={showToast} />} />
                
                {/* Rutas exclusivas Administración */}
                <Route path="/admin" element={role === 'ADMIN' ? <AdminDashboard token={token} showToast={showToast} /> : <Navigate to={user ? "/" : "/login"} />} />
                
                {/* Rutas exclusivas Productor */}
                <Route path="/productor" element={role === 'PRODUCTOR' ? <ProducerDashboard user={user} showToast={showToast} refreshGlobalProducts={refreshGlobalProducts} refreshProfile={refreshProfile} /> : <Navigate to={user ? "/" : "/login"} />} />
                
                <Route path="/registro-productor/:token" element={<ProducerRegistrationView showToast={showToast} />} />
                <Route path="/aplicar-productor" element={role === 'COMPRADOR' ? <UpgradeToProducerView user={user} setRole={setRole} showToast={showToast} /> : <Navigate to="/login" />} />
                
                <Route path="*" element={
                    <>
                        <NavHeader role={role} user={user} cartCount={cartData.items?.length || 0} onLogout={handleLogout} onOpenCart={() => setCartOpen(true)} />
                        <main>
                            <Routes>
                                <Route path="/" element={<CatalogView products={products} onSelectProduct={(id) => {setCurrentProductId(id); navigate(`/product/${id}`)}} getProductImage={getProductImage} />} />
                                <Route path="/product/:id" element={<ProductDetailWrapper products={products} onBack={() => navigate('/')} onAddToCart={handleAddToCart} getProductImage={getProductImage} role={role} />} />
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
                <div className="cart-panel" style={{display: 'flex', flexDirection: 'column'}}>
                    <div className="cart-header"><h2>Tu Carrito</h2><button onClick={() => setCartOpen(false)}>×</button></div>
                    <div style={{flex: 1, overflowY: 'auto', padding: '20px'}}>
                        {cartData.items.length === 0 ? <p style={{textAlign: 'center', color: '#666', marginTop: '40px'}}>El carrito está vacío.</p> :
                        cartData.items.map((item, idx) => (
                            <div key={idx} style={{display: 'flex', gap: '16px', marginBottom: '20px', alignItems: 'center', borderBottom: '1px solid #eee', paddingBottom: '16px'}}>
                                <img src={getProductImage(item.product.id, item.product)} style={{width: '60px', height: '60px', borderRadius: '8px', objectFit: 'cover'}} alt="item" />
                                <div style={{flex: 1}}>
                                    <h4 className="serif" style={{margin: '0 0 4px 0', fontSize: '0.95rem'}}>{item.product.name}</h4>
                                    <div style={{display: 'flex', alignItems: 'center', gap: '10px', marginTop: '8px'}}>
                                        <div className="cart-qty-mini">
                                            <button onClick={() => updateCartItemQuantity(item.product.id, -1)}>-</button>
                                            <span>{item.quantity}</span>
                                            <button onClick={() => updateCartItemQuantity(item.product.id, 1)}>+</button>
                                        </div>
                                        <button className="btn-text" style={{color: '#999', fontSize: '0.7rem', fontWeight: 600}} onClick={() => removeFromCart(item.product.id)}>ELIMINAR</button>
                                    </div>
                                </div>
                                <div style={{fontWeight: 'bold', fontSize: '0.9rem'}}>${(item.price * item.quantity).toFixed(2)}</div>
                            </div>
                        ))}
                    </div>
                    <div className="cart-footer" style={{borderTop: '1px solid #eee', padding: '20px'}}>
                        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '20px', fontSize: '1.2rem', fontWeight: 'bold'}}>
                            <span>Total:</span>
                            <span>${cartData.total.toFixed(2)}</span>
                        </div>
                        <button className="btn btn-primary full-width" disabled={cartData.items.length === 0} onClick={() => {
                            setIsPaymentModalOpen(true);
                        }}>Confirmar y Comprar Seguro</button>
                        <p style={{fontSize: '0.7rem', textAlign: 'center', color: '#999', marginTop: '12px'}}>IVA incluido. Pago procesado por Mercado Pago.</p>
                    </div>
                </div>
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

