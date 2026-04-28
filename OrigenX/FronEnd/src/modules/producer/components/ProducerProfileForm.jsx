/**
 * ProducerProfileForm.jsx – Perfil del productor con editor enriquecido.
 * Campos obligatorios: farmName, region, description, email, whatsapp, ≥1 imagen.
 */

import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import TextStyle from '@tiptap/extension-text-style';
import Color from '@tiptap/extension-color';
import Link from '@tiptap/extension-link';
import { useAuth } from '../../../context/AuthContext';
import { useProducerProfile } from '../hooks/useProducerProfile';
import styles from '../producer.module.css';


const REGIONS = [
  'Caldas',
  'Quindío',
  'Risaralda',
  'Antioquia',
  'Tolima',
  'Huila',
  'Valle del Cauca',
  'Cauca',
  'Nariño',
];

/* ─── Iconos SVG (igual a la imagen de referencia) ──────── */
const IcBold    = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M6 4h8a4 4 0 0 1 0 8H6zm0 8h9a4 4 0 0 1 0 8H6z"/></svg>;
const IcItalic  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M11.49 3h7v2h-2.93l-3.12 14H15v2H8v-2h2.93l3.12-14H11.49z"/></svg>;
const IcUnder   = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 17a6 6 0 0 0 6-6V3h-2v8a4 4 0 0 1-8 0V3H6v8a6 6 0 0 0 6 6zm-7 2v2h14v-2z"/></svg>;
const IcBullet  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M8 4h13v2H8V4zM4.5 6.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm0 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm0 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM8 11h13v2H8v-2zm0 7h13v2H8v-2z"/></svg>;
const IcOrdered = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M8 4h13v2H8V4zM5 3v3h1v1H3V6h1V4H3V3h2zm-2 9.5h2V12H3v-1h3v3H4v.5h2V15H3v-1.5zm2 5.5H3v-1h2v-.5H3v-1h3v4H3v-1h2V18zM8 11h13v2H8v-2zm0 7h13v2H8v-2z"/></svg>;
const IcAlignL  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm0 4h12v2H3V8zm0 4h18v2H3v-2zm0 4h12v2H3v-2z"/></svg>;
const IcAlignC  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm3 4h12v2H6V8zm-3 4h18v2H3v-2zm3 4h12v2H6v-2z"/></svg>;
const IcAlignR  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm6 4h12v2H9V8zm-6 4h18v2H3v-2zm6 4h12v2H9v-2z"/></svg>;
const IcLink    = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>;

/* ─── Barra de herramientas ──────────────────────────────── */
function RichToolbar({ editor }) {
  if (!editor) return null;

  const Btn = ({ onClick, active, title, children }) => (
    <button
      type="button"
      onMouseDown={(e) => { e.preventDefault(); onClick(); }}
      className={[styles.richBtn, active && styles.richBtnActive].filter(Boolean).join(' ')}
      aria-label={title}
      title={title}
    >
      {children}
    </button>
  );

  const Sep = () => <span className={styles.richSep} aria-hidden="true" />;

  const handleLink = () => {
    const prev = editor.getAttributes('link').href ?? '';
    const url  = window.prompt('URL del enlace:', prev);
    if (url === null) return;
    if (url === '') { editor.chain().focus().unsetLink().run(); return; }
    editor.chain().focus().setLink({ href: url, target: '_blank' }).run();
  };

  return (
    <div className={styles.richToolbar} role="toolbar" aria-label="Opciones de formato">
      {/* Negrita · Cursiva · Subrayado */}
      <Btn onClick={() => editor.chain().focus().toggleBold().run()}      active={editor.isActive('bold')}      title="Negrita"><IcBold /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleItalic().run()}    active={editor.isActive('italic')}    title="Cursiva"><IcItalic /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')} title="Subrayado"><IcUnder /></Btn>

      <Sep />

      {/* Color de texto */}
      <label className={styles.richColorBtn} title="Color de texto" aria-label="Color de texto">
        <span
          className={styles.richColorPreview}
          style={{ backgroundColor: editor.getAttributes('textStyle').color || '#000000' }}
        />
        <input
          type="color"
          className={styles.richColorInput}
          defaultValue="#000000"
          onInput={(e) => editor.chain().focus().setColor(e.target.value).run()}
          aria-label="Seleccionar color de texto"
        />
      </label>

      <Sep />

      {/* Listas */}
      <Btn onClick={() => editor.chain().focus().toggleBulletList().run()}  active={editor.isActive('bulletList')}  title="Lista con viñetas"><IcBullet /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive('orderedList')} title="Lista numerada"><IcOrdered /></Btn>

      <Sep />

      {/* Alineación */}
      <Btn onClick={() => editor.chain().focus().setTextAlign('left').run()}   active={editor.isActive({ textAlign: 'left' })}   title="Alinear izquierda"><IcAlignL /></Btn>
      <Btn onClick={() => editor.chain().focus().setTextAlign('center').run()} active={editor.isActive({ textAlign: 'center' })} title="Centrar"><IcAlignC /></Btn>
      <Btn onClick={() => editor.chain().focus().setTextAlign('right').run()}  active={editor.isActive({ textAlign: 'right' })}  title="Alinear derecha"><IcAlignR /></Btn>

      <Sep />

      {/* Link */}
      <Btn onClick={handleLink} active={editor.isActive('link')} title="Insertar enlace"><IcLink /></Btn>
    </div>
  );
}

/* ─── Componente principal ───────────────────────────────── */
export default function ProducerProfileForm() {
  const { currentUser } = useAuth();
  const {
    profile, loading, error,
    updateProfile, uploadImages, deleteImage, setVisibility,
    MAX_IMAGES, MAX_SIZE_MB,
  } = useProducerProfile();

  const [isEditing,         setIsEditing]         = useState(false);
  const [saveSuccess,       setSaveSuccess]        = useState(false);
  const [saveError,         setSaveError]          = useState(null);
  const [saving,            setSaving]             = useState(false);
  const [togglingActive,    setTogglingActive]     = useState(false);
  const [imageUrls,         setImageUrls]          = useState([]);
  const [newFiles,          setNewFiles]           = useState([]);
  const [imageError,        setImageError]         = useState(null);
  const [isDragging,        setIsDragging]         = useState(false);
  const [showRegisterEmail, setShowRegisterEmail]  = useState(true);
  const [altEmail,          setAltEmail]           = useState('');
  const [showAltEmail,      setShowAltEmail]       = useState(false);
  const fileInputRef = useRef(null);
  const dropRef      = useRef(null);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: { farmName: '', region: '', whatsapp: '' },
  });

  const editor = useEditor({
    extensions: [
      StarterKit,
      Underline,
      TextStyle,
      Color,
      Link.configure({ openOnClick: false }),
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
    ],
    content: '',
    editorProps: {
      attributes: {
        class: styles.richEditorContent,
        'aria-label': 'Descripción del perfil',
        'aria-multiline': 'true',
        role: 'textbox',
      },
    },
  });

  /* Cargar perfil */
  useEffect(() => {
    if (profile) {
      reset({ farmName: profile.farmName ?? '', region: profile.region ?? '', whatsapp: profile.whatsapp ?? '' });
      editor?.commands.setContent(profile.description ?? '');
      setImageUrls(profile.images ?? []);
      setShowRegisterEmail(profile.showRegisterEmail ?? true);
      setAltEmail(profile.altEmail ?? '');
      setShowAltEmail(profile.showAltEmail ?? false);
      setIsEditing(false);
    } else if (!loading) {
      setIsEditing(true);
    }
  }, [profile, loading, reset, editor]);

  /* Imágenes — validación compartida */
  const addFiles = (files) => {
    setImageError(null);
    const imageFiles = files.filter(f => f.type.startsWith('image/'));
    if (!imageFiles.length) { setImageError('Solo se aceptan archivos de imagen.'); return; }
    const total = imageUrls.length + newFiles.length + imageFiles.length;
    if (total > MAX_IMAGES) { setImageError(`Máximo ${MAX_IMAGES} imágenes en total.`); return; }
    const oversized = imageFiles.filter(f => f.size > MAX_SIZE_MB * 1024 * 1024);
    if (oversized.length) { setImageError(`Superan ${MAX_SIZE_MB} MB: ${oversized.map(f => f.name).join(', ')}`); return; }
    setNewFiles(prev => [...prev, ...imageFiles]);
  };

  const handleFileChange = (e) => {
    addFiles(Array.from(e.target.files || []));
    e.target.value = '';
  };

  /* Drag & Drop — contador para evitar parpadeo al pasar sobre hijos */
  const dragCounterRef = useRef(0);

  const handleDragEnter = (e) => {
    e.preventDefault(); e.stopPropagation();
    dragCounterRef.current += 1;
    if (dragCounterRef.current === 1) setIsDragging(true);
  };
  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); };
  const handleDragLeave = (e) => {
    e.preventDefault(); e.stopPropagation();
    dragCounterRef.current -= 1;
    if (dragCounterRef.current === 0) setIsDragging(false);
  };
  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation();
    dragCounterRef.current = 0;
    setIsDragging(false);
    if (!canAddMore) return;
    addFiles(Array.from(e.dataTransfer.files || []));
  };

  const removeExistingImage = async (url) => { await deleteImage(url); setImageUrls(prev => prev.filter(u => u !== url)); };
  const removeNewFile = (idx) => setNewFiles(prev => prev.filter((_, i) => i !== idx));

  /* Submit */
  const onSubmit = async (data) => {
    setImageError(null);
    const description = editor?.getHTML() ?? '';
    if (!description || description === '<p></p>') { setSaveError('La descripción es obligatoria.'); return; }
    const totalImages = imageUrls.length + newFiles.length;
    if (totalImages < 1) { setImageError('Debes subir al menos una imagen.'); return; }

    setSaving(true); setSaveError(null); setSaveSuccess(false);
    try {
      const uploadedUrls = newFiles.length ? await uploadImages(newFiles) : [];
      const allImages = [...imageUrls, ...uploadedUrls];
      await updateProfile({ farmName: data.farmName, region: data.region, description, whatsapp: data.whatsapp, showRegisterEmail, altEmail: altEmail || null, showAltEmail, images: allImages });
      setNewFiles([]); setImageUrls(allImages);
      setSaveSuccess(true); setIsEditing(false);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err.message || err.response?.data?.error?.message || 'No se pudo guardar el perfil.');
    } finally { setSaving(false); }
  };

  const handleEdit   = () => { setSaveSuccess(false); setSaveError(null); setIsEditing(true); };

  const isProfileComplete = !!(profile &&
    profile.farmName?.trim() &&
    profile.region &&
    profile.description?.trim() &&
    profile.whatsapp?.trim() &&
    profile.images?.length > 0);

  const handleToggleActive = async () => {
    if (!profile) return;
    setTogglingActive(true);
    try {
      await setVisibility(!profile.isActive);
    } catch (err) {
      setSaveError(err.response?.data?.error?.message || err.message || 'No se pudo cambiar la visibilidad.');
    } finally {
      setTogglingActive(false);
    }
  };  const handleCancel = () => {
    if (profile) {
      reset({ farmName: profile.farmName ?? '', region: profile.region ?? '', whatsapp: profile.whatsapp ?? '' });
      editor?.commands.setContent(profile.description ?? '');
      setImageUrls(profile.images ?? []); setNewFiles([]);
      setShowRegisterEmail(profile.showRegisterEmail ?? true);
      setAltEmail(profile.altEmail ?? '');
      setShowAltEmail(profile.showAltEmail ?? false);
    }
    setSaveError(null); setImageError(null); setIsEditing(false);
  };

  if (loading) return (
    <div className={styles.loadingState} aria-busy="true">
      <div className={styles.skeletonBlock} /><div className={styles.skeletonBlock} /><div className={styles.skeletonBlock} />
    </div>
  );
  if (error) return (
    <div className={styles.errorState} role="alert">
      <span className={styles.errorStateIcon}>⚠️</span>
      <p className={styles.errorStateText}>{error}</p>
    </div>
  );

  const totalImages = imageUrls.length + newFiles.length;
  const canAddMore  = totalImages < MAX_IMAGES;

  return (
    <section className={styles.formSection}>
      <div className={styles.sectionHeader}>
        <div>
          <h2 className={styles.sectionTitle}>Mi Perfil de Productor</h2>
          <p className={styles.sectionSubtitle}>Esta información es visible para los consumidores en el catálogo.</p>
        </div>
        <div className={styles.sectionHeaderActions}>
          {/* Toggle de visibilidad en el catálogo */}
          <label
            className={`${styles.visibilityToggle} ${!isProfileComplete ? styles.visibilityToggleDisabled : ''}`}
            title={!isProfileComplete ? 'Completa los datos obligatorios para activar tu perfil' : (profile?.isActive ? 'Desactivar perfil del catálogo' : 'Activar perfil en el catálogo')}
          >
            <input
              type="checkbox"
              className={styles.visibilityToggleInput}
              checked={!!profile?.isActive}
              disabled={!isProfileComplete || togglingActive}
              onChange={handleToggleActive}
              aria-label="Activar perfil en el catálogo de productores"
            />
            <span className={styles.visibilityToggleTrack}>
              <span className={styles.visibilityToggleThumb} />
            </span>
            <span className={styles.visibilityToggleLabel}>
              {togglingActive ? 'Guardando...' : profile?.isActive ? 'Activo en catálogo' : 'Inactivo en catálogo'}
            </span>
          </label>

          {profile && !isEditing && (
            <button type="button" className={styles.editButton} onClick={handleEdit} aria-label="Editar perfil">✏️ Editar</button>
          )}
        </div>
      </div>

      {saveSuccess && <div className={styles.successMessage} role="status">✅ Perfil guardado exitosamente.</div>}

      {/* Vista previa */}
      {profile && !isEditing ? (
        <div className={styles.profilePreview}>
          {profile.images?.length > 0 && (
            <div className={styles.profileImages}>
              {profile.images.map((url, i) => (
                <img key={i} src={url} alt={`Imagen ${i + 1} de la finca`} className={styles.profileImg} />
              ))}
            </div>
          )}
          <div className={styles.profilePreviewGrid}>
            <div className={styles.profilePreviewItem}>
              <span className={styles.profilePreviewLabel}>Nombre de la finca</span>
              <span className={styles.profilePreviewValue}>{profile.farmName || <em className={styles.emptyValue}>Sin especificar</em>}</span>
            </div>
            <div className={styles.profilePreviewItem}>
              <span className={styles.profilePreviewLabel}>Departamento</span>
              <span className={styles.profilePreviewValue}>{profile.region || <em className={styles.emptyValue}>Sin especificar</em>}</span>
            </div>
            <div className={styles.profilePreviewItem}>
              <span className={styles.profilePreviewLabel}>Correo de registro</span>
              <span className={styles.profilePreviewValue}>
                {currentUser?.email}
                {profile.showRegisterEmail
                  ? <span className={styles.visibilityBadge}>· visible en perfil</span>
                  : <span className={styles.visibilityBadgeHidden}>· oculto en perfil</span>}
              </span>
            </div>
            {profile.altEmail && (
              <div className={styles.profilePreviewItem}>
                <span className={styles.profilePreviewLabel}>Correo alternativo</span>
                <span className={styles.profilePreviewValue}>
                  {profile.altEmail}
                  {profile.showAltEmail
                    ? <span className={styles.visibilityBadge}>· visible en perfil</span>
                    : <span className={styles.visibilityBadgeHidden}>· oculto en perfil</span>}
                </span>
              </div>
            )}
            <div className={styles.profilePreviewItem}>
              <span className={styles.profilePreviewLabel}>WhatsApp</span>
              <span className={styles.profilePreviewValue}>{profile.whatsapp || <em className={styles.emptyValue}>Sin especificar</em>}</span>
            </div>
            <div className={styles.profilePreviewItem} style={{ gridColumn: '1 / -1' }}>
              <span className={styles.profilePreviewLabel}>Descripción</span>
              <div className={`${styles.profilePreviewValue} ${styles.richPreview}`}
                dangerouslySetInnerHTML={{ __html: profile.description || '<em>Sin especificar</em>' }} />
            </div>
          </div>
        </div>
      ) : (
        <>
          {!profile && <div className={styles.infoMessage} role="note">👋 Completa tu perfil para que los consumidores puedan conocerte.</div>}

          <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Formulario de perfil del productor">

            {/* Nombre de la finca + Región + WhatsApp en la misma fila */}
            <div className={styles.fieldRow}>
              <div className={styles.fieldGroup}>
                <label htmlFor="farmName" className={styles.label}>Nombre de la finca <span className={styles.required} aria-hidden="true">*</span></label>
                <input id="farmName" type="text" className={`${styles.input} ${errors.farmName ? styles.inputError : ''}`}
                  placeholder="Ej. Finca El Paraíso" aria-required="true"
                  {...register('farmName', { required: 'El nombre de la finca es obligatorio', maxLength: { value: 120, message: 'Máximo 120 caracteres' } })} />
                {errors.farmName && <span className={styles.errorMessage} role="alert">{errors.farmName.message}</span>}
              </div>

              <div className={styles.fieldGroup} style={{ flex: '0 0 160px' }}>
                <label htmlFor="region" className={styles.label}>Departamento <span className={styles.required} aria-hidden="true">*</span></label>
                <select id="region" className={`${styles.input} ${errors.region ? styles.inputError : ''}`} aria-required="true"
                  {...register('region', { required: 'Selecciona un departamento' })}>
                  <option value="">— Selecciona —</option>
                  {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
                {errors.region && <span className={styles.errorMessage} role="alert">{errors.region.message}</span>}
              </div>

              <div className={styles.fieldGroup} style={{ flex: '0 0 200px' }}>
                <label htmlFor="whatsapp" className={styles.label}>WhatsApp <span className={styles.required} aria-hidden="true">*</span></label>
                <input id="whatsapp" type="tel" className={`${styles.input} ${errors.whatsapp ? styles.inputError : ''}`}
                  placeholder="+57 300 123 4567" aria-required="true"
                  {...register('whatsapp', { required: 'El WhatsApp es obligatorio', minLength: { value: 7, message: 'Número demasiado corto' } })} />
                {errors.whatsapp && <span className={styles.errorMessage} role="alert">{errors.whatsapp.message}</span>}
              </div>
            </div>

            {/* Correo de registro + Correo alternativo en la misma fila */}
            <div className={styles.fieldRow}>

              {/* Correo de registro — bloqueado */}
              <div className={styles.fieldGroup}>
                <div className={styles.emailRow}>
                  <div className={styles.emailField}>
                    <label htmlFor="registerEmail" className={styles.label}>Correo de registro</label>
                    <input
                      id="registerEmail"
                      type="email"
                      className={`${styles.input} ${styles.inputReadonly}`}
                      value={currentUser?.email ?? ''}
                      readOnly
                      aria-readonly="true"
                    />
                  </div>
                  <label className={styles.toggleSwitch} title="Mostrar este correo en tu perfil público">
                    <input
                      type="checkbox"
                      className={styles.toggleSwitchInput}
                      checked={showRegisterEmail}
                      onChange={(e) => {
                        if (!e.target.checked && !altEmail.trim()) return;
                        setShowRegisterEmail(e.target.checked);
                      }}
                      aria-label="Mostrar correo de registro en perfil público"
                    />
                    <span className={styles.toggleSwitchTrack}>
                      <span className={styles.toggleSwitchThumb} />
                    </span>
                    <span className={styles.toggleSwitchLabel}>Mostrar</span>
                  </label>
                </div>
                {!showRegisterEmail && !altEmail.trim() && (
                  <span className={styles.hint} style={{ color: 'var(--color-error)' }}>
                    Necesitas un correo alternativo para ocultar este correo.
                  </span>
                )}
              </div>

              {/* Correo alternativo — opcional */}
              <div className={styles.fieldGroup}>
                <div className={styles.emailRow}>
                  <div className={styles.emailField}>
                    <label htmlFor="altEmail" className={styles.label}>Correo alternativo</label>
                    <input
                      id="altEmail"
                      type="email"
                      className={styles.input}
                      placeholder="otro@correo.com"
                      value={altEmail}
                      onChange={(e) => {
                        setAltEmail(e.target.value);
                        if (!e.target.value.trim()) setShowAltEmail(false);
                      }}
                      aria-label="Correo alternativo de contacto"
                    />
                  </div>
                  <label className={`${styles.toggleSwitch} ${!altEmail.trim() ? styles.toggleSwitchDisabled : ''}`} title="Mostrar correo alternativo en tu perfil público">
                    <input
                      type="checkbox"
                      className={styles.toggleSwitchInput}
                      checked={showAltEmail}
                      disabled={!altEmail.trim()}
                      onChange={(e) => setShowAltEmail(e.target.checked)}
                      aria-label="Mostrar correo alternativo en perfil público"
                    />
                    <span className={styles.toggleSwitchTrack}>
                      <span className={styles.toggleSwitchThumb} />
                    </span>
                    <span className={styles.toggleSwitchLabel}>Mostrar</span>
                  </label>
                </div>
              </div>

            </div>


            {/* Descripción enriquecida */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Descripción <span className={styles.required} aria-hidden="true">*</span></label>
              <div className={styles.richEditorWrapper}>
                <RichToolbar editor={editor} />
                <EditorContent editor={editor} />
              </div>
              <span className={styles.hint}>Usa el formato para destacar tu historia, proceso y valores.</span>
            </div>

            {/* Imágenes */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>
                Imágenes <span className={styles.required} aria-hidden="true">*</span>
              </label>

              {/* Zona de drag & drop */}
              <div
                ref={dropRef}
                className={`${styles.dropZone} ${isDragging ? styles.dropZoneActive : ''} ${!canAddMore ? styles.dropZoneFull : ''}`}
                onDragEnter={canAddMore ? handleDragEnter : undefined}
                onDragOver={canAddMore ? handleDragOver : undefined}
                onDragLeave={canAddMore ? handleDragLeave : undefined}
                onDrop={canAddMore ? handleDrop : undefined}
                aria-label="Zona para arrastrar imágenes"
              >
                {/* Miniaturas */}
                {(imageUrls.length > 0 || newFiles.length > 0) && (
                  <div className={styles.imageGrid}>
                    {imageUrls.map((url, i) => (
                      <div key={url} className={styles.imageThumb}>
                        <img src={url} alt={`Imagen ${i + 1}`} className={styles.thumbImg} />
                        <button type="button" className={styles.deleteImageButton} onClick={() => removeExistingImage(url)} aria-label={`Eliminar imagen ${i + 1}`}>✕</button>
                      </div>
                    ))}
                    {newFiles.map((file, i) => (
                      <div key={i} className={styles.imageThumb}>
                        <img src={URL.createObjectURL(file)} alt={`Nueva imagen ${i + 1}`} className={styles.thumbImg} />
                        <button type="button" className={styles.deleteImageButton} onClick={() => removeNewFile(i)} aria-label={`Quitar imagen ${i + 1}`}>✕</button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Mensaje de la zona */}
                {canAddMore && (
                  <div className={styles.dropZoneHint}>
                    {isDragging ? (
                      <span className={styles.dropZoneHintText}>📂 Suelta las imágenes aquí</span>
                    ) : (
                      <>
                        <svg className={styles.dropZoneIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                        </svg>
                        <span className={styles.dropZoneHintText}>
                          Arrastra imágenes aquí o{' '}
                          <label htmlFor="profileImages" className={styles.dropZoneLink}>selecciona archivos</label>
                        </span>
                        <span className={styles.dropZoneCounter}>{totalImages}/{MAX_IMAGES} · máx. {MAX_SIZE_MB} MB c/u</span>
                      </>
                    )}
                  </div>
                )}

                {!canAddMore && (
                  <p className={styles.dropZoneFullMsg}>Límite de {MAX_IMAGES} imágenes alcanzado</p>
                )}
              </div>

              {/* Input oculto */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                className={styles.fileInput}
                id="profileImages"
                onChange={handleFileChange}
                aria-label="Subir imágenes de la finca"
                disabled={!canAddMore}
              />

              {imageError && <span className={styles.errorMessage} role="alert">{imageError}</span>}
            </div>

            {saveError && <div className={styles.serverError} role="alert">{saveError}</div>}

            <div className={styles.formActions}>
              <button type="submit" className={styles.submitButton} disabled={saving} aria-busy={saving}>
                {saving ? 'Guardando...' : profile ? 'Guardar cambios' : 'Crear perfil'}
              </button>
              {profile && (
                <button type="button" className={styles.cancelButton} onClick={handleCancel} disabled={saving}>Cancelar</button>
              )}
            </div>
          </form>
        </>
      )}
    </section>
  );
}
