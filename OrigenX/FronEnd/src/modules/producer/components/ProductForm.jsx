/**
 * components/ProductForm.jsx – Formulario de creación/edición de producto.
 * Descripción: editor Tiptap enriquecido.
 * Imágenes: zona drag & drop (máx. 5, ≤ 5 MB, JPG/PNG).
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
import styles from '../producer.module.css';

const MAX_IMAGES      = 5;
const MAX_FILE_SIZE_MB = 5;
const ALLOWED_TYPES   = ['image/jpeg', 'image/png'];

/* ── Iconos SVG ─────────────────────────────────────────── */
const IcBold    = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M6 4h8a4 4 0 0 1 0 8H6zm0 8h9a4 4 0 0 1 0 8H6z"/></svg>;
const IcItalic  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M11.49 3h7v2h-2.93l-3.12 14H15v2H8v-2h2.93l3.12-14H11.49z"/></svg>;
const IcUnder   = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M12 17a6 6 0 0 0 6-6V3h-2v8a4 4 0 0 1-8 0V3H6v8a6 6 0 0 0 6 6zm-7 2v2h14v-2z"/></svg>;
const IcBullet  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M8 4h13v2H8V4zM4.5 6.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm0 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm0 7a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM8 11h13v2H8v-2zm0 7h13v2H8v-2z"/></svg>;
const IcOrdered = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M8 4h13v2H8V4zM5 3v3h1v1H3V6h1V4H3V3h2zm-2 9.5h2V12H3v-1h3v3H4v.5h2V15H3v-1.5zm2 5.5H3v-1h2v-.5H3v-1h3v4H3v-1h2V18zM8 11h13v2H8v-2zm0 7h13v2H8v-2z"/></svg>;
const IcAlignL  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm0 4h12v2H3V8zm0 4h18v2H3v-2zm0 4h12v2H3v-2z"/></svg>;
const IcAlignC  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm3 4h12v2H6V8zm-3 4h18v2H3v-2zm3 4h12v2H6v-2z"/></svg>;
const IcAlignR  = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><path d="M3 4h18v2H3V4zm6 4h12v2H9V8zm-6 4h18v2H3v-2zm6 4h12v2H9v-2z"/></svg>;
const IcLink    = () => <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>;

/* ── Toolbar ─────────────────────────────────────────────── */
function RichToolbar({ editor }) {
  if (!editor) return null;
  const Btn = ({ onClick, active, title, children }) => (
    <button type="button" onMouseDown={(e) => { e.preventDefault(); onClick(); }}
      className={[styles.richBtn, active && styles.richBtnActive].filter(Boolean).join(' ')}
      aria-label={title} title={title}>{children}</button>
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
      <Btn onClick={() => editor.chain().focus().toggleBold().run()}      active={editor.isActive('bold')}      title="Negrita"><IcBold /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleItalic().run()}    active={editor.isActive('italic')}    title="Cursiva"><IcItalic /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')} title="Subrayado"><IcUnder /></Btn>
      <Sep />
      <label className={styles.richColorBtn} title="Color de texto" aria-label="Color de texto">
        <span className={styles.richColorPreview} style={{ backgroundColor: editor.getAttributes('textStyle').color || '#000000' }} />
        <input type="color" className={styles.richColorInput} defaultValue="#000000"
          onInput={(e) => editor.chain().focus().setColor(e.target.value).run()} aria-label="Seleccionar color" />
      </label>
      <Sep />
      <Btn onClick={() => editor.chain().focus().toggleBulletList().run()}  active={editor.isActive('bulletList')}  title="Lista con viñetas"><IcBullet /></Btn>
      <Btn onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive('orderedList')} title="Lista numerada"><IcOrdered /></Btn>
      <Sep />
      <Btn onClick={() => editor.chain().focus().setTextAlign('left').run()}   active={editor.isActive({ textAlign: 'left' })}   title="Izquierda"><IcAlignL /></Btn>
      <Btn onClick={() => editor.chain().focus().setTextAlign('center').run()} active={editor.isActive({ textAlign: 'center' })} title="Centrar"><IcAlignC /></Btn>
      <Btn onClick={() => editor.chain().focus().setTextAlign('right').run()}  active={editor.isActive({ textAlign: 'right' })}  title="Derecha"><IcAlignR /></Btn>
      <Sep />
      <Btn onClick={handleLink} active={editor.isActive('link')} title="Insertar enlace"><IcLink /></Btn>
    </div>
  );
}

/* ── Componente principal ────────────────────────────────── */
export default function ProductForm({ product, onSubmit, onCancel, uploadImage, deleteImage, saving }) {
  const isEditing = !!product;

  /* Imágenes */
  const [images,         setImages]         = useState(product?.images ?? []);
  const [newFiles,       setNewFiles]       = useState([]);
  const [deletedIds,     setDeletedIds]     = useState([]);   // IDs a eliminar al guardar
  const [imageError,     setImageError]     = useState(null);
  const [descError,      setDescError]      = useState(null);
  const [isDragging,     setIsDragging]     = useState(false);
  const dragCounterRef = useRef(0);
  const dropRef        = useRef(null);
  const fileInputRef   = useRef(null);

  const totalImages = images.length + newFiles.length;
  const canAddMore  = totalImages < MAX_IMAGES;

  /* Editor */
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
      attributes: { class: styles.richEditorContent, 'aria-label': 'Descripción del producto', role: 'textbox', 'aria-multiline': 'true' },
    },
    onCreate: ({ editor: e }) => {
      if (product?.description) {
        e.commands.setContent(product.description);
      }
    },
    onUpdate: () => {
      setDescError(null);
    },
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    defaultValues: {
      name:  product?.name  ?? '',
      price: product?.price ?? '',
      stock: product?.stock != null ? product.stock : 0,
    },
  });

  useEffect(() => {
    if (product && editor) {
      reset({
        name:  product.name  ?? '',
        price: product.price ?? '',
        stock: product.stock != null ? product.stock : 0,
      });
      editor.commands.setContent(product.description ?? '');
      setImages(product.images ?? []);
      setNewFiles([]);
      setDeletedIds([]);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [product?.id, product?.stock, product?.description, editor]);

  /* Validación de archivos */
  const addFiles = (files) => {
    setImageError(null);
    const valid = files.filter(f => ALLOWED_TYPES.includes(f.type));
    if (!valid.length) { setImageError('Solo se aceptan JPG o PNG.'); return; }
    const total = images.length + newFiles.length + valid.length;
    if (total > MAX_IMAGES) { setImageError(`Máximo ${MAX_IMAGES} imágenes.`); return; }
    const oversized = valid.filter(f => f.size > MAX_FILE_SIZE_MB * 1024 * 1024);
    if (oversized.length) { setImageError(`Superan ${MAX_FILE_SIZE_MB} MB: ${oversized.map(f => f.name).join(', ')}`); return; }
    setNewFiles(prev => [...prev, ...valid]);
  };

  const handleFileChange = (e) => { addFiles(Array.from(e.target.files || [])); e.target.value = ''; };

  /* Drag & drop */
  const handleDragEnter = (e) => { e.preventDefault(); e.stopPropagation(); dragCounterRef.current += 1; if (dragCounterRef.current === 1) setIsDragging(true); };
  const handleDragOver  = (e) => { e.preventDefault(); e.stopPropagation(); };
  const handleDragLeave = (e) => { e.preventDefault(); e.stopPropagation(); dragCounterRef.current -= 1; if (dragCounterRef.current === 0) setIsDragging(false); };
  const handleDrop      = (e) => { e.preventDefault(); e.stopPropagation(); dragCounterRef.current = 0; setIsDragging(false); if (canAddMore) addFiles(Array.from(e.dataTransfer.files || [])); };

  /* Eliminar — solo marca visualmente, se ejecuta al guardar */
  const removeExisting = (imgId) => {
    setImageError(null);
    setImages(prev => prev.filter(i => i.id !== imgId));
    setDeletedIds(prev => [...prev, imgId]);
  };
  const removeNew = (idx) => setNewFiles(prev => prev.filter((_, i) => i !== idx));

  /* Submit */
  const handleFormSubmit = async (data) => {
    const description = editor?.getHTML() ?? '';
    const descEmpty = !description || description === '<p></p>' || description.trim() === '';

    // Validar descripción
    if (descEmpty) {
      setDescError('La descripción es obligatoria.');
      return;
    }
    setDescError(null);

    // Validar mínimo 1 imagen
    if (images.length === 0 && newFiles.length === 0) {
      setImageError('Debes agregar al menos una imagen del producto.');
      return;
    }
    setImageError(null);

    await onSubmit({
      name:        data.name.trim(),
      price:       parseFloat(data.price),
      stock:       parseInt(data.stock, 10) || 0,
      description,
      _newFiles:   newFiles,
      _deletedIds: deletedIds,
    });
  };

  return (
    <div className={styles.formOverlay} role="dialog" aria-modal="true" aria-label={isEditing ? 'Editar producto' : 'Nuevo producto'}>
      <div className={styles.formCard}>
        <div className={styles.formCardHeader}>
          <h2 className={styles.formCardTitle}>{isEditing ? 'Editar producto' : 'Nuevo producto'}</h2>
          <button type="button" className={styles.closeButton} onClick={onCancel} aria-label="Cerrar">✕</button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit(handleFormSubmit)} noValidate>

          {/* Nombre + Precio + Stock en fila */}
          <div className={styles.fieldRow}>
            <div className={styles.fieldGroup}>
              <label htmlFor="productName" className={styles.label}>Nombre <span className={styles.required}>*</span></label>
              <input id="productName" type="text"
                className={`${styles.input} ${errors.name ? styles.inputError : ''}`}
                placeholder="Ej. Café Especial Huila" aria-required="true"
                {...register('name', { required: 'El nombre es obligatorio', maxLength: { value: 120, message: 'Máximo 120 caracteres' } })} />
              {errors.name && <span className={styles.errorMessage} role="alert">{errors.name.message}</span>}
            </div>
            <div className={styles.fieldGroup} style={{ flex: '0 0 140px' }}>
              <label htmlFor="productPrice" className={styles.label}>Precio (COP) <span className={styles.required}>*</span></label>
              <input id="productPrice" type="number" step="0.01" min="0.01"
                className={`${styles.input} ${errors.price ? styles.inputError : ''}`}
                placeholder="45000" aria-required="true"
                {...register('price', { required: 'El precio es obligatorio', min: { value: 0.01, message: 'Debe ser mayor a 0' } })} />
              {errors.price && <span className={styles.errorMessage} role="alert">{errors.price.message}</span>}
            </div>
            <div className={styles.fieldGroup} style={{ flex: '0 0 110px' }}>
              <label htmlFor="productStock" className={styles.label}>Stock <span className={styles.required}>*</span></label>
              <input id="productStock" type="number" min="0" step="1"
                className={`${styles.input} ${errors.stock ? styles.inputError : ''}`}
                placeholder="0" aria-required="true"
                {...register('stock', { required: 'El stock es obligatorio', min: { value: 0, message: 'Mínimo 0' } })} />
              {errors.stock && <span className={styles.errorMessage} role="alert">{errors.stock.message}</span>}
            </div>
          </div>

          {/* Descripción enriquecida */}
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Descripción <span className={styles.required}>*</span></label>
            <div className={`${styles.richEditorWrapper} ${descError ? styles.inputError : ''}`}
              style={descError ? { borderColor: 'var(--color-error)' } : {}}>
              <RichToolbar editor={editor} />
              <EditorContent editor={editor} />
            </div>
            {descError
              ? <span className={styles.errorMessage} role="alert">{descError}</span>
              : <span className={styles.hint}>Describe las características, notas de cata y proceso de tu café.</span>
            }
          </div>

          {/* Imágenes */}
          <div className={styles.fieldGroup}>
            <label className={styles.label}>
              Imágenes <span className={styles.required}>*</span>
              <span className={styles.hint} style={{ fontWeight: 'normal', marginLeft: 6 }}>(máx. {MAX_IMAGES} · JPG/PNG · ≤ {MAX_FILE_SIZE_MB} MB c/u)</span>
            </label>

            <div
              ref={dropRef}
              className={`${styles.dropZone} ${isDragging ? styles.dropZoneActive : ''} ${!canAddMore ? styles.dropZoneFull : ''}`}
              onDragEnter={canAddMore ? handleDragEnter : undefined}
              onDragOver={canAddMore ? handleDragOver : undefined}
              onDragLeave={canAddMore ? handleDragLeave : undefined}
              onDrop={canAddMore ? handleDrop : undefined}
            >
              {/* Miniaturas existentes */}
              {(images.length > 0 || newFiles.length > 0) && (
                <div className={styles.imageGrid}>
                  {images.map((img) => (
                    <div key={img.id} className={styles.imageThumb}>
                      <img src={img.url} alt="Imagen del producto" className={styles.thumbImg} loading="lazy" />
                      <button type="button" className={styles.deleteImageButton} onClick={() => removeExisting(img.id)} aria-label="Eliminar imagen">✕</button>
                    </div>
                  ))}
                  {newFiles.map((file, i) => (
                    <div key={i} className={styles.imageThumb}>
                      <img src={URL.createObjectURL(file)} alt={`Nueva imagen ${i + 1}`} className={styles.thumbImg} />
                      <button type="button" className={styles.deleteImageButton} onClick={() => removeNew(i)} aria-label="Quitar imagen">✕</button>
                    </div>
                  ))}
                </div>
              )}

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
                        <label htmlFor="productImages" className={styles.dropZoneLink}>selecciona archivos</label>
                      </span>
                      <span className={styles.dropZoneCounter}>{totalImages}/{MAX_IMAGES}</span>
                    </>
                  )}
                </div>
              )}
              {!canAddMore && <p className={styles.dropZoneFullMsg}>Límite de {MAX_IMAGES} imágenes alcanzado</p>}
            </div>

            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png" multiple
              className={styles.fileInput} id="productImages"
              onChange={handleFileChange} disabled={!canAddMore} aria-label="Subir imágenes del producto" />

            {imageError && <span className={styles.errorMessage} role="alert">{imageError}</span>}
            {!isEditing && newFiles.length > 0 && (
              <span className={styles.hint}>Las imágenes se subirán al guardar el producto.</span>
            )}
          </div>

          {/* Acciones */}
          <div className={styles.formActions}>
            <button type="button" className={styles.cancelButton} onClick={onCancel}>Cancelar</button>
            <button type="submit" className={styles.submitButton} disabled={saving} aria-busy={saving}>
              {saving ? 'Guardando...' : isEditing ? 'Guardar cambios' : 'Crear producto'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
