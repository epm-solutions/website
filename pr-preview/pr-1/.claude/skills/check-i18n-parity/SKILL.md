---
name: check-i18n-parity
description: Verifica paridad estructural y de contenido entre las versiones multiidioma del sitio EPM (index.html español, en/index.html inglés, pt/index.html portugués). Detecta markup faltante o extra, imágenes distintas, scripts divergentes, textos sin traducir, y nav links rotos. Usar cuando se pide "verificar traducciones", "check i18n", "sync check", "¿están sincronizados los idiomas?", o después de editar cualquier archivo index.
---

# Check i18n Parity

Ejecutar `scripts/check_parity.py` para verificar que todas las versiones del sitio estén sincronizadas.

## Uso rápido

```bash
cd /home/user/website
python3 .claude/skills/check-i18n-parity/scripts/check_parity.py \
  index.html en/index.html pt/index.html
```

Exit code 0 = todo sincronizado. Exit code 1 = diferencias encontradas.

## Qué verifica el script

1. **Estructura HTML**: diff normalizado de la estructura DOM (tags + clases CSS). Detecta nodos extra, faltantes, o en orden distinto.
2. **Textos**: misma cantidad de nodos de texto, ninguno vacío, y textos que deberían estar traducidos no son idénticos entre idiomas.
3. **Scripts**: bloques `<script>` deben ser idénticos en todos los archivos.
4. **Imágenes**: mismas referencias `<img src>` en el mismo orden.
5. **Stylesheets**: mismas hojas de estilo referenciadas.
6. **Consistencia interna**: nav anchors apuntan a section IDs existentes, `<html lang>` correcto.

## Diferencias esperadas (filtradas automáticamente)

- `<html lang>` (`es` vs `en` vs `pt`)
- Clase `active` en el lang-switcher
- Section IDs (`#nosotros` vs `#about`)
- `data-tab` attributes (`ingenieria` vs `engineering`)
- Nombres propios, siglas universitarias, datos de contacto
- "Project Management", "Engineering & Project Management", "Córdoba, Argentina"

## Flujo de trabajo

1. Ejecutar el script
2. Si hay problemas, corregir en el archivo que corresponda
3. Re-ejecutar hasta obtener exit code 0

## Agregar un nuevo idioma

1. Crear `XX/index.html` copiando la estructura de `index.html`
2. Traducir textos visibles
3. Mapear section IDs al nuevo idioma
4. Actualizar la función `_lang_of()` del script para detectar el nuevo subdirectorio
5. Actualizar el lang-switcher en todos los archivos para incluir el nuevo idioma
6. Ejecutar el script con todos los archivos
