#!/usr/bin/env python3
"""
Verifica paridad estructural y de contenido entre versiones i18n de HTML.

Uso:
  python3 check_parity.py index.html en/index.html [pt/index.html ...]

Salida: lista de diferencias encontradas, agrupadas por categoría.
Exit code 0 = sin problemas, 1 = diferencias encontradas.
"""

import sys
import re
from html.parser import HTMLParser
from pathlib import Path
from difflib import unified_diff


class StructuralParser(HTMLParser):
    """Extrae estructura, textos, scripts e imágenes del HTML."""

    SKIP_TEXT_IN = {"script", "style"}
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__()
        self.structure = []       # tags normalizados para diff estructural
        self.texts = []           # (context, text)
        self.scripts = []         # contenido de <script>
        self.images = []          # src de <img>, en orden
        self.section_ids = []     # id de <section>
        self.stylesheets = []     # href de <link rel="stylesheet">
        self.nav_anchors = []     # hrefs del nav (#nosotros, etc.)
        self.lang = None
        self._tag_stack = []
        self._in_skip = None
        self._skip_buf = ""
        self._depth = 0
        self._in_lang_switcher = False

    def _context(self):
        return " > ".join(self._tag_stack[-4:]) if self._tag_stack else "(root)"

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        self._depth += 1

        if tag == "html" and "lang" in ad:
            self.lang = ad["lang"]

        cls = ad.get("class", "")

        if "lang-switcher" in cls:
            self._in_lang_switcher = True

        # Normalizar: quitar class="active" dentro del lang-switcher
        if self._in_lang_switcher:
            cls = re.sub(r'\bactive\b', '', cls).strip()

        if cls:
            struct_line = f"{'  ' * self._depth}<{tag} class=\"{cls}\">"
        else:
            struct_line = f"{'  ' * self._depth}<{tag}>"
        self.structure.append(struct_line)

        self._tag_stack.append(tag)

        if tag == "img" and "src" in ad:
            self.images.append(ad["src"])
        if tag == "section" and "id" in ad:
            self.section_ids.append(ad["id"])
        if tag == "link" and ad.get("rel") == "stylesheet":
            self.stylesheets.append(ad.get("href", ""))

        in_nav = "nav" in self._tag_stack
        if tag == "a" and in_nav:
            href = ad.get("href", "")
            if href.startswith("#") and href != "#":
                self.nav_anchors.append(href.lstrip("#"))

        if tag in self.SKIP_TEXT_IN:
            self._in_skip = tag
            self._skip_buf = ""

        if tag in self.VOID_ELEMENTS:
            self._tag_stack.pop()
            self._depth -= 1

    def handle_endtag(self, tag):
        if tag in self.VOID_ELEMENTS:
            return

        if self._in_skip == tag:
            if tag == "script":
                self.scripts.append(self._skip_buf.strip())
            self._in_skip = None
            self._skip_buf = ""

        self.structure.append(f"{'  ' * self._depth}</{tag}>")
        self._depth -= 1
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag == "div" and self._in_lang_switcher:
            self._in_lang_switcher = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self._in_skip:
            self._skip_buf += data
            return
        self.texts.append((self._context(), text))


def parse_file(path):
    content = Path(path).read_text(encoding="utf-8")
    parser = StructuralParser()
    parser.feed(content)
    return parser


def compare_structure(a, b, name_a, name_b):
    """Compara estructura HTML normalizada usando diff."""
    issues = []
    diff = list(unified_diff(
        a.structure, b.structure,
        fromfile=name_a, tofile=name_b,
        lineterm="",
    ))
    if diff:
        added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
        issues.append(
            f"Estructura HTML difiere ({removed} línea(s) solo en {name_a}, "
            f"{added} solo en {name_b})"
        )
        context_lines = [l for l in diff if l.startswith(("@@", "+", "-")) and not l.startswith(("+++", "---"))]
        for line in context_lines[:20]:
            issues.append(f"  {line}")
        if len(context_lines) > 20:
            issues.append(f"  ... y {len(context_lines) - 20} líneas más")
    return issues


CLOSE_LANG_PAIRS = {
    frozenset({"index.html", "pt/index.html"}),
}

ALWAYS_SKIP = [
    r"^\(54\)",
    r"@\w+\.\w+",
    r"^https?://",
    r"^linkedin$",
    r"^(ES|EN|PT)$",
    r"^EPM\b",
    r"^(UNC|UCC|UTN|PMI|ITBA|ICDA|EPCM)\b",
    r"&copy;",
    r"^Engineering & Project Management$",
    r"^Project Management$",
    r"^\d+[\.,]\d+",
    r"^U\$D\b|^USD\b|^US\$\b",
    r"^Córdoba,\s*Argentina$",
]

PERSON_NAMES = [
    "Darío Romero", "Gastón Sanchez", "Leonardo Poldi",
    "Giuliana Lenarduzzi", "Renzo Lenarduzzi", "Marcelo Quaranta",
    "Federico", "Lucio",
]


def should_be_translated(text, close_langs=False):
    """Determina si un texto debería estar traducido entre idiomas."""
    if re.match(r"^[\d\s\.\,\+\$%&@|/()–—\-:]+$", text):
        return False
    if len(text) <= 2:
        return False
    for pat in ALWAYS_SKIP:
        if re.search(pat, text, re.IGNORECASE):
            return False
    for name in PERSON_NAMES:
        if name in text:
            return False
    # Idiomas cercanos (ES↔PT) comparten muchos cognados cortos
    if close_langs and len(text) <= 30:
        return False
    return True


def compare_texts(a, b, name_a, name_b):
    """Verifica que ambos archivos tengan textos traducidos y ninguno vacío."""
    issues = []
    close = frozenset({name_a, name_b}) in CLOSE_LANG_PAIRS

    if len(a.texts) != len(b.texts):
        issues.append(
            f"Cantidad de nodos de texto difiere: {name_a} tiene {len(a.texts)}, "
            f"{name_b} tiene {len(b.texts)}"
        )
        min_len = min(len(a.texts), len(b.texts))
        if len(a.texts) > len(b.texts):
            for i in range(min_len, len(a.texts)):
                ctx, txt = a.texts[i]
                issues.append(f"  Texto extra en {name_a}: \"{txt[:80]}\" ({ctx})")
        else:
            for i in range(min_len, len(b.texts)):
                ctx, txt = b.texts[i]
                issues.append(f"  Texto extra en {name_b}: \"{txt[:80]}\" ({ctx})")
    else:
        min_len = len(a.texts)

    for i in range(min(min_len, len(a.texts), len(b.texts))):
        ctx_a, text_a = a.texts[i]
        ctx_b, text_b = b.texts[i]
        if text_a == text_b and should_be_translated(text_a, close_langs=close):
            issues.append(
                f"Texto idéntico (¿falta traducción?): \"{text_a[:70]}\" ({ctx_a})"
            )

    return issues


def compare_scripts(a, b, name_a, name_b):
    """Compara bloques <script> — deben ser idénticos."""
    issues = []
    if len(a.scripts) != len(b.scripts):
        issues.append(
            f"Cantidad de <script> difiere: {name_a} tiene {len(a.scripts)}, "
            f"{name_b} tiene {len(b.scripts)}"
        )
    for i, (sa, sb) in enumerate(zip(a.scripts, b.scripts)):
        if sa != sb:
            issues.append(f"Contenido de <script> #{i+1} difiere entre {name_a} y {name_b}")
    return issues


def compare_images(a, b, name_a, name_b):
    """Compara referencias a imágenes en orden."""
    issues = []
    if len(a.images) != len(b.images):
        issues.append(
            f"Cantidad de <img> difiere: {name_a} tiene {len(a.images)}, "
            f"{name_b} tiene {len(b.images)}"
        )
    for i, (ia, ib) in enumerate(zip(a.images, b.images)):
        if ia != ib:
            issues.append(f"Imagen #{i+1} difiere: {name_a}=\"{ia}\", {name_b}=\"{ib}\"")
    return issues


def compare_stylesheets(a, b, name_a, name_b):
    """Hojas de estilo referenciadas deben ser idénticas."""
    issues = []
    if a.stylesheets != b.stylesheets:
        issues.append(
            f"Stylesheets difieren: {name_a}={a.stylesheets}, {name_b}={b.stylesheets}"
        )
    return issues


def _lang_of(name):
    """Infiere el código de idioma esperado a partir del path del archivo."""
    p = Path(name)
    parent = p.parent.name
    if parent in ("en", "pt", "fr", "de"):
        return parent
    # archivo en la raíz → español
    if parent in (".", ""):
        return "es"
    return None


def check_internal(parsed, name):
    """Verifica consistencia interna de un archivo."""
    issues = []

    for anchor in parsed.nav_anchors:
        if anchor not in parsed.section_ids:
            issues.append(
                f"Nav apunta a #{anchor} pero no existe como section id "
                f"(ids existentes: {parsed.section_ids})"
            )

    expected = _lang_of(name)
    if expected and parsed.lang != expected:
        issues.append(f'<html lang="{parsed.lang}"> debería ser lang="{expected}"')

    return issues


def main():
    if len(sys.argv) < 3:
        print("Uso: check_parity.py <archivo1.html> <archivo2.html> [archivo3.html ...]")
        sys.exit(2)

    files = sys.argv[1:]
    parsed = {}

    for f in files:
        path = Path(f)
        if not path.exists():
            print(f"ERROR: {f} no existe")
            sys.exit(2)
        parsed[str(path)] = parse_file(f)

    all_issues = {}

    names = list(parsed.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            pa, pb = parsed[na], parsed[nb]
            pair = f"{na} ↔ {nb}"

            issues = []
            issues.extend(compare_structure(pa, pb, na, nb))
            issues.extend(compare_texts(pa, pb, na, nb))
            issues.extend(compare_scripts(pa, pb, na, nb))
            issues.extend(compare_images(pa, pb, na, nb))
            issues.extend(compare_stylesheets(pa, pb, na, nb))

            if issues:
                all_issues[pair] = issues

    for name, p in parsed.items():
        issues = check_internal(p, name)
        if issues:
            all_issues[f"{name} (consistencia interna)"] = issues

    if not all_issues:
        print("✓ Todos los archivos están sincronizados correctamente.")
        sys.exit(0)

    total = 0
    for category, issues in sorted(all_issues.items()):
        print(f"\n{'='*60}")
        print(f"  {category}")
        print(f"{'='*60}")
        for issue in issues:
            print(f"  • {issue}")
            total += 1

    print(f"\n{'─'*60}")
    print(f"  Total: {total} problema(s) encontrado(s)")
    print(f"{'─'*60}")
    sys.exit(1)


if __name__ == "__main__":
    main()
