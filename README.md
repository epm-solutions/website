# EPM Solutions — Sitio web

Sitio institucional de **EPM Solutions** (Engineering & Project Management),
empresa de ingeniería y gestión de proyectos con sede en Córdoba, Argentina.

## Stack

- HTML/CSS/JS estático, sin frameworks ni dependencias
- Alojado en **GitHub Pages** (rama `main`, directorio raíz)
- Dominio personalizado registrado en **NIC.ar**

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
    dario-romero.jpg
    gaston-sanchez-conci.jpg
    giuliana-lenarduzzi.jpg
    leonardo-poldi.jpg
    marcelo-quaranta.jpg
    renzo-lenarduzzi.jpg
```

Todas las rutas a CSS e imágenes son **absolutas** (ej. `/assets/styles.css`,
`/images/logo-EPM.png`) para funcionar correctamente desde cualquier
subdirectorio (`/en/`, `/pt/`).

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
con dominio personalizado (NIC.ar).

## Desarrollo local

```bash
python3 -m http.server 3000
```

Abrir `http://localhost:3000` para la versión española,
`http://localhost:3000/en/` para inglés,
`http://localhost:3000/pt/` para portugués.
