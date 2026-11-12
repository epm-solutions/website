# EPM Solutions — Sitio web

Sitio institucional de **EPM Solutions** (Engineering & Project Management),
empresa de ingeniería y gestión de proyectos con sede en Córdoba, Argentina.

## Stack

- HTML/CSS/JS estático, sin frameworks ni dependencias
- Alojado en **GitHub Pages** (rama `gh-pages`, directorio raíz)
- DNS gestionados vía **Cloudflare**
- Dominio personalizado registrado en **NIC.ar**
- Tests con **html-proofer** (links, imágenes, anchors)
- Darío Romero es dueño de las cuentas en GitHub y Cloudflare

## Infraestructura DNS / SSL

- Cloudflare en modo DNS-only (nube gris), sin proxy. GitHub Pages maneja SSL
  directamente con certificado Let's Encrypt
- Dominio: https://epmsolutions.com.ar (sin `www`)

## Estructura

```
index.html                        # Versión en español (idioma original)
en/index.html                     # Versión en ingles
pt/index.html                     # Versión en portugues
assets/styles.css                 # Hoja de estilos única
images/
  favicon.ico / favicon-32.png
  logo-EPM.png                    # Logo principal + vista previa redes sociales
  headshots/
    dario-romero.jpeg
    gaston-sanchez-conci.jpg
    giuliana-lenarduzzi.jpg
    leonardo-poldi.jpg
    marcelo-quaranta.jpg
    renzo-lenarduzzi.jpg
```

Todas las rutas a CSS e imágenes son **relativas** (ej. `assets/styles.css`
desde la raíz, `../assets/styles.css` desde subdirectorios) para funcionar
correctamente en GitHub Pages sin depender de un dominio fijo.

## Cómo traducir

El sitio tiene tres versiones sincronizadas. Al editar contenido:

1. Editar la sección correspondiente en **los tres archivos** (`index.html`,
   `en/index.html`, `pt/index.html`).
2. Mantener la misma estructura HTML en los tres (mismo número de tags, clases,
   imágenes y scripts).
3. Traducir todos los textos visibles; no dejar textos idénticos entre idiomas
   salvo nombres propios, siglas, datos de contacto y términos técnicos
   invariables.
4. Verificar la sincronización con el skill `check-i18n-parity` (ver abajo).

## Verificar sincronización entre idiomas

Usar el skill de Claude Code:

```
/check-i18n-parity
```

O ejecutar el script directamente desde la raíz del proyecto:

```bash
python3 .claude/skills/check-i18n-parity/scripts/check_parity.py \
  index.html en/index.html pt/index.html
```

- Exit code `0` = todo sincronizado.
- Exit code `1` = diferencias encontradas (ver salida para detalles).

## Deploy

El sitio se publica automáticamente con cada push a `main` vía GitHub Pages,
con dominio personalizado (NIC.ar). El workflow `.github/workflows/deploy.yml`
copia el contenido de `main` a la rama `gh-pages`, desde donde GitHub Pages lo
sirve.

## Review apps (previews por PR)

Cada Pull Request despliega automáticamente una copia del sitio en una URL
propia, permitiendo revisar los cambios sin clonar la rama.

**URL del preview:** `https://epmsolutions.com.ar/pr-preview/pr-[número]/`

El workflow `.github/workflows/preview.yml` se encarga de:

- Desplegar el preview cuando se abre o actualiza un PR
- Dejar un comentario en el PR con el link directo (incluye QR)
- Eliminar el preview cuando se cierra el PR

No requiere ninguna acción manual: abrir un PR alcanza.

## Desarrollo local

```bash
python3 -m http.server 3000
```

Abrir `http://localhost:3000` para la versión en español,
`http://localhost:3000/en/` para inglés,
`http://localhost:3000/pt/` para portugués.

## Tests

El proyecto usa [html-proofer](https://github.com/gjtorikian/html-proofer) para
validar los archivos HTML. También se ejecuta automáticamente como hook
pre-commit.

### Setup (una sola vez al clonar)

```bash
bundle install
```

Crear el archivo `.git/hooks/pre-commit` con este contenido:

```bash
#!/usr/bin/env bash
set -euo pipefail

if git diff --cached --name-only | grep -qE '\.(html|css)$'; then
  echo "Validando HTML (html-proofer)..."
  bundle exec ruby bin/validate
fi
```

Y hacerlo ejecutable:

```bash
chmod +x .git/hooks/pre-commit
```

### Qué verifica

- Imágenes referenciadas en `src` existen en disco
- Links internos apuntan a archivos reales
- Anchors (`#contacto`, `#about`, etc.) tienen su `id` correspondiente
- Scripts y stylesheets referenciados existen

### Ejecución manual

```bash
bundle exec ruby bin/validate
```
