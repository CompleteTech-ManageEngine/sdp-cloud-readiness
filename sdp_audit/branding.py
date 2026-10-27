"""Presentation identity for branded copies, loaded from a brand file or preset.

A preset is ``templates/branding.<name>.json`` beside the entry point; the
CompleteTech LLC preset (``completetech``) is the default identity of the
entry points. Any other brand file can be passed with ``--brand`` or
``SDP_BRAND_FILE``. Two layouts are accepted:

* skill layout: ``{"company": {"name", "website", "email", "tagline"},
  "logo": "assets/logo.png", "themes": {"light": {...}}}``
* flat layout: ``{"name", "website", "email", "tagline", "logo", "light": {...}}``

The logo must be a local PNG or JPEG. A relative logo path resolves against the
brand file's folder and then up to three parent folders, so a skill-relative
path such as ``assets/logo.png`` works from ``templates/``. Remote and data-URI
logos are rejected; nothing is fetched. Unknown palette tokens are ignored and
missing ones fall back to the neutral defaults below.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import html
import json
from pathlib import Path
import re
import struct
from typing import Any, Mapping


MAX_BRAND_BYTES = 256 * 1024
MAX_LOGO_BYTES = 2 * 1024 * 1024
HEX = re.compile(r"#?[0-9A-Fa-f]{6}\Z")
DEFAULT_TOKENS = {
    "page": "#FFFFFF", "band": "#1F2937", "band_ink": "#FFFFFF", "accent": "#177D8D",
    "accent_2": "#55728C", "ink": "#0F172A", "ink_2": "#334155", "ink_3": "#64748B",
    "line": "#E2E8F0", "surface": "#F8FAFC", "surface_2": "#F1F5F9", "link": "#0E7490",
}


@dataclass(frozen=True)
class Brand:
    name: str
    website: str = ""
    email: str = ""
    tagline: str = ""
    prepared_for: str = ""
    logo: bytes = b""
    logo_mime: str = ""
    logo_size: tuple[int, int] = (0, 0)
    logo_path: str = ""
    logo_background: str = ""
    tokens: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_TOKENS))

    @property
    def contact(self) -> str:
        return " · ".join(part for part in (self.name, self.website, self.email) if part)

    @property
    def logo_uri(self) -> str:
        return f"data:{self.logo_mime};base64," + base64.b64encode(self.logo).decode("ascii") if self.logo else ""

    def hex(self, token: str) -> str:
        """Palette value without the leading '#', for spreadsheet and PDF writers."""
        return self.tokens[token].lstrip("#")


def _text(value: Any, label: str, limit: int = 200) -> str:
    if value is None:
        return ""
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError(f"Brand {label} must be a short single-line string.")
    return value.strip()


def _image_size(data: bytes) -> tuple[str, tuple[int, int]]:
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return "image/png", struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        offset = 2
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                break
            marker, length = data[offset + 1], struct.unpack(">H", data[offset + 2:offset + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[offset + 5:offset + 9])
                return "image/jpeg", (width, height)
            offset += 2 + length
    raise ValueError("Brand logo must be a PNG or JPEG image.")


def _resolve_logo(value: str, brand_dir: Path) -> Path:
    if value.startswith(("http://", "https://", "data:", "//")):
        raise ValueError("Remote and data-URI brand logos are not accepted; point the brand file at a local image.")
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        if candidate.is_file():
            return candidate
    else:
        for base in (brand_dir, *list(brand_dir.parents)[:3]):
            if (base / candidate).is_file():
                return base / candidate
    raise ValueError("Brand logo file was not found next to the brand file or its parent folders.")


PRESET = re.compile(r"[a-z0-9][a-z0-9-]{0,40}\Z")


def resolve_brand_path(value: str, app_dir: Path) -> Path:
    """A file path (as given, or relative to the application folder) or a preset name."""
    candidate = Path(value).expanduser()
    if candidate.is_file():
        return candidate
    if not candidate.is_absolute() and (app_dir / candidate).is_file():
        return app_dir / candidate
    if PRESET.fullmatch(value) and (app_dir / "templates" / f"branding.{value}.json").is_file():
        return app_dir / "templates" / f"branding.{value}.json"
    raise ValueError("Brand file or preset not found. Pass a brand JSON path or a preset name from templates/.")


def load_brand(path: str | Path, prepared_for: str = "") -> Brand:
    """Read and validate an operator brand file; never fetches anything."""
    source = Path(path).expanduser().resolve()
    raw = source.read_bytes()
    if len(raw) > MAX_BRAND_BYTES:
        raise ValueError("Brand file exceeds 256 KiB.")
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("Brand file must be a JSON object.")
    company = data.get("company") if isinstance(data.get("company"), dict) else data
    themes = data.get("themes") if isinstance(data.get("themes"), dict) else data
    light = themes.get("light") or {}
    if not isinstance(light, dict):
        raise ValueError("Brand light palette must be an object.")
    tokens = dict(DEFAULT_TOKENS)
    for key, value in light.items():
        key = key.replace("-", "_")
        if key not in tokens:
            continue
        if not isinstance(value, str) or not HEX.fullmatch(value):
            raise ValueError(f"Brand colour {key} must be a 6-digit hex value.")
        tokens[key] = "#" + value.lstrip("#").upper()
    name = _text(company.get("name"), "name")
    if not name:
        raise ValueError("Brand file must name the preparing company.")
    logo, mime, size, logo_path = b"", "", (0, 0), ""
    if data.get("logo"):
        resolved = _resolve_logo(_text(data["logo"], "logo", 1024), source.parent)
        logo = resolved.read_bytes()
        if len(logo) > MAX_LOGO_BYTES:
            raise ValueError("Brand logo exceeds 2 MB; use a smaller image.")
        mime, size = _image_size(logo)
        logo_path = str(resolved)
    background = data.get("logo_background") or ""
    if background and (not isinstance(background, str) or not HEX.fullmatch(background)):
        raise ValueError("Brand logo_background must be a 6-digit hex value.")
    return Brand(
        name=name, website=_text(company.get("website"), "website"), email=_text(company.get("email"), "email"),
        tagline=_text(company.get("tagline"), "tagline"), prepared_for=_text(prepared_for, "prepared-for name"),
        logo=logo, logo_mime=mime, logo_size=size, logo_path=logo_path, tokens=tokens,
        logo_background="#" + background.lstrip("#").upper() if background else "",
    )


def slug(value: str, fallback: str = "Assessment") -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    return text[:60] or fallback


def tint(colour: str, amount: float) -> str:
    """Blend a #RRGGBB colour toward white by amount (0 = unchanged, 1 = white)."""
    rgb = [int(colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join("%02X" % round(c + (255 - c) * amount) for c in rgb)


def html_css(brand: Brand, gutter: int = 40) -> str:
    """Brand layer appended after a report's base stylesheet."""
    t = brand.tokens
    # An opaque logo sits on a tile of its own background colour inside the band.
    tile = (f".brand-band img {{ background:{brand.logo_background}; padding:8px 14px; border-radius:6px; box-sizing:content-box; }}\n"
            if brand.logo_background else "")
    return tile + f"""
:root {{ --ink:{t['ink']}; --ink-2:{t['ink_2']}; --muted:{t['ink_3']}; --line:{t['line']}; --paper:{t['page']}; --tint:{t['surface_2']};
  --band:{t['band']}; --band-ink:{t['band_ink']}; --accent:{t['accent']}; --accent-2:{t['accent_2']}; --surface:{t['surface']}; --link:{t['link']}; }}
body {{ background:var(--tint); color:var(--ink-2); font-family:"Helvetica Neue",Helvetica,Arial,system-ui,sans-serif; }}
main {{ padding:0 {gutter}px 32px; border-radius:6px; overflow:hidden; box-shadow:0 1px 3px rgba(15,23,42,.08); }}
.brand-band,.brand-stripe {{ margin-left:-{gutter}px; margin-right:-{gutter}px; }}
.brand-band {{ background:var(--band); color:var(--band-ink); display:flex; align-items:center; justify-content:space-between;
  gap:24px; flex-wrap:wrap; padding:30px {gutter}px; }}
.brand-band img {{ height:62px; width:auto; display:block; }}
.brand-band .brand-name {{ font-size:22px; font-weight:700; color:var(--band-ink); margin:0; }}
.brand-band .doc {{ text-align:right; }}
.brand-band .doc-type {{ font-size:30px; line-height:1.1; font-weight:400; color:var(--band-ink); margin:0; white-space:normal; }}
.brand-band .doc-ref {{ font-size:13px; font-weight:700; color:var(--accent-2); margin:6px 0 0; white-space:normal; }}
.brand-stripe {{ height:4px; background:linear-gradient(90deg,var(--accent) 0 38%,var(--accent-2) 38% 100%); margin-bottom:30px; }}
.brand-parties {{ display:flex; gap:56px; flex-wrap:wrap; margin-bottom:22px; }}
.brand-parties p {{ white-space:normal; margin:0; font-size:13px; line-height:1.5; }}
.brand-parties .label,.eyebrow {{ color:var(--accent); font-size:11px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }}
.brand-parties strong {{ color:var(--ink); font-size:15px; }}
header {{ border-bottom:0; border-left:4px solid var(--accent); padding:4px 0 6px 18px; margin-bottom:28px; }}
h1,h2,h3,h4,caption {{ color:var(--ink); }}
h1 {{ font-size:32px; font-weight:700; }}
h2 {{ border-bottom:2px solid var(--line); }}
a {{ color:var(--link); }}
thead th {{ background:var(--band); color:var(--band-ink); border-color:var(--band); }}
.key-values th {{ background:var(--surface); color:var(--ink); }}
tbody tr:nth-child(even) td {{ background:var(--surface); }}
.status-card {{ border-radius:4px; background:var(--paper); }}
.status-card .number {{ color:var(--ink); }}
.status-card.impact {{ border-top-color:var(--accent); }}
.finding,.question,details {{ border-radius:4px; }}
.finding {{ border-left:4px solid var(--band); }}
.action {{ background:{tint(t['accent_2'], 0.925)}; border-left:3px solid var(--accent-2); }}
footer {{ margin-top:34px; }}
.brand-footer {{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-top:12px; color:var(--muted); }}
@media (max-width:850px) {{ main {{ padding:0 22px 22px; }} .brand-band,.brand-stripe {{ margin-left:-22px; margin-right:-22px; }}
  .brand-band {{ padding:22px; }} .brand-band .doc {{ text-align:left; }} }}
@media print {{ * {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }} body {{ background:white; }}
  main {{ box-shadow:none; padding:0; border-radius:0; overflow:visible; }} .brand-band,.brand-stripe {{ margin-left:0; margin-right:0; }} }}
@page {{ size:letter; margin:0.6in; }}
"""


def html_masthead(brand: Brand, doc_type: str, reference: str) -> str:
    """Band with logo and document type, the accent stripe, and prepared by/for."""
    mark = (f'<img src="{brand.logo_uri}" alt="{html.escape(brand.name)}">' if brand.logo
            else f'<p class="brand-name">{html.escape(brand.name)}</p>')
    by = "<br>".join(html.escape(part) for part in (brand.website, brand.email) if part)
    parties = ('<div class="brand-parties"><p><span class="label">Prepared by</span><br>'
               f"<strong>{html.escape(brand.name)}</strong>" + (f"<br>{by}" if by else "") + "</p>")
    if brand.prepared_for:
        parties += (f'<p><span class="label">Prepared for</span><br>'
                    f"<strong>{html.escape(brand.prepared_for)}</strong></p>")
    return (f'<div class="brand-band">{mark}<div class="doc"><p class="doc-type">{html.escape(doc_type)}</p>'
            f'<p class="doc-ref">{html.escape(reference)}</p></div></div><div class="brand-stripe"></div>'
            + parties + "</div>")


def html_footer(brand: Brand) -> str:
    right = f"Prepared for {brand.prepared_for}" if brand.prepared_for else brand.tagline
    return (f'<div class="brand-footer"><span>{html.escape(brand.contact)}</span>'
            f"<span>{html.escape(right)}</span></div>")


def html_title(brand: Brand, title: str) -> str:
    return " · ".join(part for part in (brand.prepared_for, title) if part) + " | " + brand.name


def markdown_header(brand: Brand, doc_type: str) -> str:
    """Brand block prepended to a branded Markdown copy."""
    lines = [f"**{brand.name}** · {doc_type}"]
    if brand.prepared_for:
        lines.append(f"Prepared for **{brand.prepared_for}**")
    if brand.contact:
        lines.append(brand.contact)
    return "  \n".join(lines) + "\n\n---\n\n"
