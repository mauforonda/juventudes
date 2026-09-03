# Vista del Observatorio de la Juventud

Sitio estático sin dependencias. El índice se genera a partir de todas las fichas y los datos detallados se cargan bajo demanda desde el repositorio público.

## Construir

Desde `observatorio/vista`:

```bash
source /home/m/.virtualenvs/pruebas/bin/activate
python construir_indice.py
```

Para probar localmente, desde `observatorio`:

```bash
python -m http.server 8000
```

Abrir `http://localhost:8000/vista/`.

## Publicar

El workflow `.github/workflows/pages.yml` regenera el índice y publica el contenido de `vista` en GitHub Pages:

- automáticamente, cuando un commit en `main` cambia un archivo dentro de `vista`;
- manualmente, con **Run workflow** en la pestaña **Actions**.

En **Settings → Pages → Build and deployment**, la fuente debe estar configurada como **GitHub Actions**.
