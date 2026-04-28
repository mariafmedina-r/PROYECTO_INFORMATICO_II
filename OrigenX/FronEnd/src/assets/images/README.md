# /src/assets/images

Imágenes importadas directamente en componentes React.
Vite las procesa, optimiza y genera hashes en el nombre para cache busting.

## Uso

```jsx
import heroCafe from './hero-cafe.jpg';

<img src={heroCafe} alt="..." />
```

## Subcarpetas sugeridas

- `logos/`      → logo de la marca en distintos formatos
- `regions/`    → fotos de regiones cafeteras
- `producers/`  → fotos de productores o fincas
- `ui/`         → imágenes decorativas de la interfaz

## Notas

- Formatos recomendados: WebP (preferido), SVG (para íconos/logos), JPG, PNG
- Tamaño máximo recomendado: 200 KB por imagen (Vite no comprime automáticamente)
- Archivos SVG pueden importarse como componentes React con el plugin vite-plugin-svgr
