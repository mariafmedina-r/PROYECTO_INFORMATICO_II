import React, { useState } from 'react';
import { auth } from '../firebase_config';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword, sendPasswordResetEmail } from 'firebase/auth';
import { getUserProfile, saveUserProfile } from '../api';

const LoginView = ({ onLogin, showToast, isInvite }) => {
    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [loading, setLoading] = useState(false);

    const handleResetPassword = async () => {
        if (!email) { showToast("Ingrese su correo", "error"); return; }
        try {
            await sendPasswordResetEmail(auth, email);
            showToast("Correo de recuperación enviado", "success");
        } catch (error) { showToast("Error: " + error.message, "error"); }
    };

    // [WORKFLOW DE AUTENTICACIÓN]
    // Esta función centraliza ambas operaciones: Login (signIn...) y Registro (create...):
    // 1. Envía credenciales usando Firebase Auth.
    // 2. Si es registro, delega el guardado de rol ('COMPRADOR' o 'ADMIN') hacia el backend.
    // 3. Extrae el JWT final y lo devuelve al contexto superior (`App.jsx`).
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            console.log("DEBUG: Iniciando proceso de login para:", email);
            let userCredential;
            
            if (isRegister) {
                userCredential = await createUserWithEmailAndPassword(auth, email, password);
                const adminEmails = ['admin@patrimoniocafetero.com', 'test@example.com'];
                const assignedRole = adminEmails.includes(email.toLowerCase()) ? 'ADMIN' : 'COMPRADOR';
                await saveUserProfile(userCredential.user.uid, { email, full_name: fullName, role: assignedRole, is_active: true });
                showToast("Cuenta creada con éxito (" + assignedRole + ")", "success");
            } else {
                userCredential = await signInWithEmailAndPassword(auth, email, password);
            }
            
            console.log("DEBUG: Auth Firebase exitoso. UID:", userCredential.user.uid);
            
            // Intentar obtener perfil de Firestore
            let profile = null;
            try {
                profile = await getUserProfile(userCredential.user.uid);
            } catch (fsError) {
                console.warn("DEBUG: No se pudo leer Firestore (posible tema de reglas):", fsError);
            }
            
            const adminEmails = ['admin@patrimoniocafetero.com', 'test@example.com'];
            const role = profile?.role || (adminEmails.includes(email.toLowerCase()) ? 'ADMIN' : 'COMPRADOR');
            const token = await userCredential.user.getIdToken();
            
            console.log("DEBUG: Login completo. Rol:", role);
            onLogin({...userCredential.user, ...profile}, token, role);
            
        } catch (error) {
            console.error("DEBUG: Error en handleSubmit:", error);
            let msg = "Error de autenticación";
            if (error.code === 'auth/user-not-found') msg = "Usuario no registrado. Verifique su correo.";
            if (error.code === 'auth/wrong-password') msg = "Contraseña incorrecta. Intente de nuevo.";
            if (error.code === 'auth/invalid-credential') msg = "Credenciales inválidas. Correo o contraseña erróneos.";
            if (error.code === 'auth/email-already-in-use') msg = "El correo ya está registrado. Por favor, inicie sesión.";
            if (error.code === 'auth/weak-password') msg = "Su contraseña debe tener al menos 6 caracteres.";
            if (error.code === 'auth/invalid-email') msg = "El formato del correo es inválido.";
            showToast(msg, "error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-left">
                <img className="login-bg" src="https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=1200&q=80" alt="bg" />
                <div className="login-overlay"></div>
                <div className="login-left-content">
                    <h1 className="login-title serif">Patrimonio Cafetero</h1>
                    <p className="login-subtitle">Gestión unificada de fincas y comercio artesanal.</p>
                </div>
            </div>
            <div className="login-right">
                <div className="login-form">
                    <h2 className="serif">{isRegister ? 'Registro' : 'Ingreso'}</h2>
                    {/* Feedback UI para QA / Usuarios: Muestra de qué trata la autenticación híbrida */}
                    <p style={{color: 'var(--text-secondary)', marginBottom: '40px'}}>
                        Sistema de validación con Firebase Authentication y Perfiles Firestore.
                    </p>
                    
                    <form onSubmit={handleSubmit}>
                        {isRegister && (
                            <div className="input-group">
                                <label>Nombre Completo</label>
                                <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Ej. Juan Pérez" required={isRegister} />
                            </div>
                        )}
                        <div className="input-group">
                            <label>Email</label>
                            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="tu@correo.com" required />
                        </div>
                        <div className="input-group">
                            <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                                <label style={{marginBottom: 0}}>Contraseña</label>
                                {!isRegister && <button type="button" onClick={handleResetPassword} className="btn-text" style={{fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-green)', background: 'none', border: 'none', cursor: 'pointer', padding: 0}}>¿OLVIDÓ SU CLAVE?</button>}
                            </div>
                            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
                        </div>
                        <button type="submit" className="btn btn-primary full-width" disabled={loading}>
                            {loading ? 'PROCESANDO...' : (isRegister ? 'REGISTRARME' : 'ENTRAR AL PANEL')}
                        </button>
                    </form>
                    
                    {!isInvite && (
                        <div style={{marginTop: '20px', textAlign: 'center'}}>
                            <button className="btn-text" style={{fontSize: '0.85rem', color: 'var(--accent-green)', fontWeight: 600}} onClick={() => setIsRegister(!isRegister)}>
                                {isRegister ? '¿Ya tienes cuenta? Entra aquí' : '¿Eres nuevo? Crea tu cuenta de comprador'}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LoginView;
