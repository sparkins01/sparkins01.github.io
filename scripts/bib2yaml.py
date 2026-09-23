#!/usr/bin/env python3
"""Convert a Pure BibTeX export into the site's publication data.

Usage:
    python3 scripts/bib2yaml.py [path/to/export.bib]

Writes:
    _data/publications.yml   - data used to render publications.html
    files/publications.bib   - cleaned BibTeX offered as a download
                               (internal Pure "note" fields are removed)

Re-run this whenever you export a fresh .bib file from Pure.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scripts" / "pure_export.bib"

CATEGORIES = {
    "article": "Journal Articles",
    "inproceedings": "Conference Papers",
    "inbook": "Book Chapters",
    "incollection": "Book Chapters",
    "book": "Books",
}

# Papers that received an award (matched on a fragment of the title)
AWARDS = {
    "Repetition and Template Generalisability": "Best Presentation Award, CCAI 2023",
}

# Pure exports reports as books; reclassify them (matched on a title fragment)
TYPE_OVERRIDES = {
    "Recommendations on Bilateral Government-Private Sector": "Technical Reports",
    "Rapid Evidence Assessment": "Technical Reports",
}

MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

LATEX = [
    (r"{\textcopyright}", "©"), (r"{\textquoteright}", "’"), (r"{\textquoteleft}", "‘"),
    (r"\textasciitilde{}", "~"), (r"\textasciitilde", "~"), (r"\textbackslash", ""), (r"{\textendash}", "–"), (r"{\textemdash}", "—"), (r"\&amp;", "&"), (r"\&", "&"),
    (r"\%", "%"), (r"\_", "_"), (r"\$", "$"),
]
ACCENTS = {"'": "\u0301", "`": "\u0300", '"': "\u0308", "^": "\u0302", "~": "\u0303",
           "c": "\u0327", "v": "\u030c", "u": "\u0306", "=": "\u0304", ".": "\u0307"}


def delatex(s):
    import unicodedata
    s = s.replace("\\{", "{").replace("\\}", "}")  # Pure escapes grouping braces
    for a, b in LATEX:
        s = s.replace(a, b)
    s = re.sub(r"\{\\([\'`\"^~=.])\s*\{?([A-Za-z])\}?\}",
               lambda m: unicodedata.normalize("NFC", m.group(2) + ACCENTS[m.group(1)]), s)
    s = re.sub(r"\{\\([cvu])\s+\{?([A-Za-z])\}?\}",
               lambda m: unicodedata.normalize("NFC", m.group(2) + ACCENTS[m.group(1)]), s)
    s = re.sub(r"\\([\'`\"^~=.])\{?([A-Za-z])\}?",
               lambda m: unicodedata.normalize("NFC", m.group(2) + ACCENTS[m.group(1)]), s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def clean_link(s):
    from urllib.parse import unquote
    s = s.split(",")[0].strip()  # Pure sometimes lists several URLs
    for a, b in (("\\_", "_"), ("\\%", "%"), ("\\&", "&"), ("\\textasciitilde{}", "~")):
        s = s.replace(a, b)
    return unquote(s)


def parse_value(text, i):
    """Parse a BibTeX field value starting at text[i]; return (raw, next_index)."""
    c = text[i]
    if c == '"':
        j, depth = i + 1, 0
        while j < len(text):
            ch = text[j]
            if ch == "\\":
                j += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == '"' and depth == 0:
                return text[i + 1:j], j + 1
            j += 1
        raise ValueError("unterminated string")
    if c == "{":
        j, depth = i, 0
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    return text[i + 1:j], j + 1
            j += 1
        raise ValueError("unterminated brace")
    m = re.match(r"[^,\s}]+", text[i:])
    return m.group(0), i + m.end()


def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key, i = m.group(1).lower(), m.group(2), m.end()
        fields, order = {}, []
        while True:
            fm = re.compile(r"\s*(\w+)\s*=\s*").match(text, i)
            if not fm:
                break
            name = fm.group(1).lower()
            raw, i = parse_value(text, fm.end())
            fields[name] = raw
            order.append(name)
            cm = re.compile(r"\s*,").match(text, i)
            if cm:
                i = cm.end()
        entries.append((etype, key, fields, order))
    return entries


def fmt_authors(raw):
    names = []
    for a in re.split(r"\s+and\s+", raw):
        a = delatex(a)
        if "," in a:
            last, first = [p.strip() for p in a.split(",", 1)]
            a = f"{first} {last}"
        names.append(a)
    return names


def main():
    text = SRC.read_text(encoding="utf-8")
    entries = parse_bib(text)
    pubs, bib_out = [], []
    for etype, key, f, order in entries:
        year = int(f.get("year", "0") or 0)
        month = MONTHS.get(f.get("month", "").strip().lower()[:3], 0)
        venue = f.get("journal") or f.get("booktitle") or ""
        if etype == "book":
            venue = f.get("series", "")
        pub = {
            "type": CATEGORIES.get(etype, "Other"),
            "title": delatex(f.get("title", "")),
            "authors": fmt_authors(f.get("author", "")) if f.get("author") else [],
            "editors": fmt_authors(f["editor"]) if f.get("editor") else [],
            "venue": delatex(venue),
            "year": year,
            "month": month,
            "volume": delatex(f.get("volume", "")),
            "number": delatex(f.get("number", "")),
            "pages": delatex(f.get("pages", "")).replace("--", "–"),
            "publisher": delatex(f.get("publisher", "")),
            "doi": clean_link(f.get("doi", "")),
            "url": clean_link(f.get("url", "")),
            "abstract": delatex(f.get("abstract", "")),
            "key": key,
        }
        pubs.append({k: v for k, v in pub.items() if v not in ("", [], 0) or k == "year"})

        # Re-emit values in brace form, dropping Pure's internal notes
        lines = []
        for n in order:
            if n == "note":
                continue
            v = f[n].replace("\\{", "{").replace("\\}", "}")
            lines.append(f"  {n} = {v}" if re.fullmatch(r"[a-z]{3}", v) else f"  {n} = {{{v}}}")
        bib_out.append(f"@{etype}{{{key},\n" + ",\n".join(lines) + "\n}\n")

    extra = ROOT / "scripts" / "extra_publications.yml"
    if extra.exists():
        pubs.extend(yaml.safe_load(extra.read_text(encoding="utf-8")) or [])
    for p in pubs:
        for match, ptype in TYPE_OVERRIDES.items():
            if match.lower() in p["title"].lower():
                p["type"] = ptype
        for match, award in AWARDS.items():
            if match.lower() in p["title"].lower():
                p["award"] = award

    pubs.sort(key=lambda p: (-p["year"], -p.get("month", 0), p["title"]))
    (ROOT / "_data" / "publications.yml").write_text(
        "# Generated by scripts/bib2yaml.py from a Pure export - do not edit by hand.\n"
        + yaml.safe_dump(pubs, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8")
    (ROOT / "files" / "publications.bib").write_text("\n".join(bib_out), encoding="utf-8")
    counts = {}
    for p in pubs:
        counts[p["type"]] = counts.get(p["type"], 0) + 1
    print(f"Wrote {len(pubs)} publications: {counts}")


if __name__ == "__main__":
    main()
