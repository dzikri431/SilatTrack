import os
import re
import html

DOCS_DIR = r"c:\absensi eskul pencak silat\docs"
UML_DIR = os.path.join(DOCS_DIR, "UML")

# Clean, Word-safe CSS without page-break-inside avoid loops
CSS_STYLES = """
<style>
body {
    font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.35;
    color: #24292f;
    margin: 20pt;
}

/* Cover Page */
.cover-page {
    text-align: center;
    padding: 30pt 10pt;
}

.cover-header {
    border-bottom: 3.5pt solid #8A1C14;
    padding-bottom: 16pt;
    margin-bottom: 25pt;
}

.cover-tagline {
    font-size: 11pt;
    font-weight: bold;
    color: #7D5800;
    text-transform: uppercase;
    letter-spacing: 2pt;
    margin-bottom: 12pt;
}

.cover-title {
    font-size: 24pt;
    font-weight: 800;
    color: #8A1C14;
    margin: 0 0 10pt 0;
    line-height: 1.2;
}

.cover-subtitle {
    font-size: 13pt;
    font-weight: 600;
    color: #4b5563;
    margin: 0 0 20pt 0;
}

.cover-meta-table {
    width: 90%;
    margin: 25pt auto;
    border-collapse: collapse;
    text-align: left;
}

.cover-meta-table th {
    background-color: #8A1C14;
    color: #ffffff;
    padding: 8pt 12pt;
    font-size: 9.5pt;
    font-weight: bold;
    border: 1pt solid #70150e;
    width: 32%;
}

.cover-meta-table td {
    background-color: #faf7f6;
    padding: 8pt 12pt;
    font-size: 9.5pt;
    border: 1pt solid #e5e7eb;
    color: #1f2937;
}

.cover-footer {
    margin-top: 40pt;
    font-size: 9pt;
    color: #6b7280;
    border-top: 1pt solid #e5e7eb;
    padding-top: 12pt;
}

/* Headings */
h1 {
    font-size: 17pt;
    font-weight: bold;
    color: #8A1C14;
    border-bottom: 2pt solid #8A1C14;
    padding-bottom: 4pt;
    margin-top: 22pt;
    margin-bottom: 10pt;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    color: #8A1C14;
    border-left: 4pt solid #7D5800;
    padding-left: 8pt;
    margin-top: 18pt;
    margin-bottom: 8pt;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #1f2937;
    margin-top: 13pt;
    margin-bottom: 5pt;
}

h4 {
    font-size: 10pt;
    font-weight: bold;
    color: #4b5563;
    margin-top: 10pt;
    margin-bottom: 4pt;
}

p {
    margin-top: 0;
    margin-bottom: 6pt;
    text-align: justify;
}

/* Tables */
table.content-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8pt;
    margin-bottom: 12pt;
    font-size: 9pt;
}

table.content-table th {
    background-color: #8A1C14;
    color: #ffffff;
    font-weight: bold;
    text-align: left;
    padding: 6pt 8pt;
    border: 1pt solid #70150e;
}

table.content-table td {
    padding: 5pt 8pt;
    border: 1pt solid #d1d5db;
    vertical-align: top;
    line-height: 1.25;
}

table.content-table tr:nth-child(even) td {
    background-color: #faf7f6;
}

table.content-table tr:nth-child(odd) td {
    background-color: #ffffff;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 2pt 5pt;
    font-size: 8pt;
    font-weight: bold;
    border-radius: 3pt;
}
.badge-wajib {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1pt solid #f87171;
}
.badge-penting {
    background-color: #fef3c7;
    color: #92400e;
    border: 1pt solid #fcd34d;
}
.badge-opsional {
    background-color: #e0f2fe;
    color: #075985;
    border: 1pt solid #7dd3fc;
}

/* Blockquotes / Callouts */
blockquote {
    margin: 8pt 0;
    padding: 8pt 12pt;
    background-color: #fdf8f7;
    border-left: 3.5pt solid #8A1C14;
    color: #374151;
    font-style: italic;
}

blockquote p {
    margin: 2pt 0;
}

/* Code Blocks */
pre {
    background-color: #f8fafc;
    border: 1pt solid #e2e8f0;
    border-radius: 4pt;
    padding: 8pt 10pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    line-height: 1.35;
    color: #0f172a;
    margin: 6pt 0 10pt 0;
}

code.inline-code {
    background-color: #f1f5f9;
    color: #8A1C14;
    padding: 1pt 4pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    border-radius: 3pt;
    border: 1pt solid #e2e8f0;
}

/* Lists */
ul, ol {
    margin-top: 4pt;
    margin-bottom: 8pt;
    padding-left: 18pt;
}

li {
    margin-bottom: 3pt;
}

/* Images & Captions */
.image-placeholder-block {
    text-align: center;
    margin: 14pt auto;
}

.image-caption {
    font-size: 8.5pt;
    font-style: italic;
    color: #4b5563;
    margin-top: 4pt;
    font-weight: 600;
}

/* Page Breaks */
.page-break {
    page-break-before: always;
}

hr.divider {
    border: 0;
    height: 1pt;
    background-color: #e5e7eb;
    margin: 14pt 0;
}
</style>
"""

def clean_math(text):
    replacements = [
        (r'\$< 200\\text\{ ms\}\$', '< 200 ms'),
        (r'\$< 5\\text\{ KB\}\$', '< 5 KB'),
        (r'\$< 100\\text\{ ms\}\$', '< 100 ms'),
        (r'\$\\le 0\{,\}60\$', '≤ 0,60'),
        (r'\$\\le 0\{,\}58\$', '≤ 0,58'),
        (r'\$> 0\{,\}60\$', '> 0,60'),
        (r'\$< 0\{,\}5\$', '< 0,5'),
        (r'\$75\\% - 80\\%\$', '75% - 80%'),
        (r'\$\\ge 75\\%\$', '≥ 75%'),
        (r'\$85\{,\}6\\text\{ mm\} \\times 54\\text\{ mm\}\$', '85,6 mm × 54 mm'),
        (r'\$50\\text\{ cm\} - 1\\text\{ meter\}\$', '50 cm - 1 meter'),
        (r'\$0\{,\}5 - 1\$', '0,5 - 1'),
        (r'\$100\\%\$', '100%'),
        (r'\$4\{,\}5:1\$', '4,5:1'),
        (r'\$([0-9]+)\$', r'\1'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def parse_markdown_to_html(md_text, doc_key="DOC"):
    md_text = clean_math(md_text)
    lines = md_text.splitlines()
    
    html_out = []
    in_table = False
    table_headers = []
    table_rows = []
    
    in_code = False
    code_lang = ""
    code_lines = []
    
    in_blockquote = False
    blockquote_lines = []
    
    in_ul = False
    in_ol = False
    
    def close_table():
        nonlocal in_table, table_headers, table_rows
        if in_table:
            t_html = ['<table class="content-table"><thead><tr>']
            for th in table_headers:
                t_html.append(f'<th>{th}</th>')
            t_html.append('</tr></thead><tbody>')
            for row in table_rows:
                t_html.append('<tr>')
                for cell in row:
                    t_html.append(f'<td>{cell}</td>')
                t_html.append('</tr>')
            t_html.append('</tbody></table>')
            html_out.append(''.join(t_html))
            in_table = False
            table_headers = []
            table_rows = []

    def close_code():
        nonlocal in_code, code_lang, code_lines
        if in_code:
            code_text = html.escape('\n'.join(code_lines))
            label = code_lang.upper() if code_lang else "SPECIFICATION"
            badge = f'<div style="background:#8A1C14; color:#fff; font-size:8pt; padding:2pt 8pt; font-weight:bold; display:inline-block; border-radius:3pt 3pt 0 0;">{label}</div>'
            html_out.append(f'<div style="margin: 8pt 0 12pt 0;">{badge}<pre><code>{code_text}</code></pre></div>')
            in_code = False
            code_lang = ""
            code_lines = []

    def close_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if in_blockquote:
            bq_content = '<br/>'.join(blockquote_lines)
            html_out.append(f'<blockquote><p>{bq_content}</p></blockquote>')
            in_blockquote = False
            blockquote_lines = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            html_out.append('</ul>')
            in_ul = False
        if in_ol:
            html_out.append('</ol>')
            in_ol = False

    def inline_format(text):
        # Markdown links: [text](#anchor) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', text)
        # Bold: **text**
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic: *text*
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
        
        # Priority badges
        text = text.replace('<strong>Wajib</strong>', '<span class="badge badge-wajib">Wajib</span>')
        text = text.replace('<strong>Penting</strong>', '<span class="badge badge-penting">Penting</span>')
        text = text.replace('<strong>Opsional</strong>', '<span class="badge badge-opsional">Opsional</span>')
        
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Code block delimiter
        if stripped.startswith('```'):
            if in_code:
                close_code()
            else:
                close_table()
                close_blockquote()
                close_lists()
                in_code = True
                code_lang = stripped[3:].strip()
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            close_table()
            close_lists()
            in_blockquote = True
            bq_line = stripped[1:].strip()
            blockquote_lines.append(inline_format(bq_line))
            i += 1
            continue
        elif in_blockquote and stripped != '':
            pass
        else:
            close_blockquote()

        # Table rows
        if stripped.startswith('|') and stripped.endswith('|'):
            close_blockquote()
            close_lists()
            cells = [c.strip() for c in stripped[1:-1].split('|')]
            if not in_table:
                in_table = True
                table_headers = [inline_format(c) for c in cells]
                table_rows = []
                if i + 1 < len(lines) and re.match(r'^\s*\|[:\-\s\|]+\|\s*$', lines[i+1]):
                    i += 1
            else:
                table_rows.append([inline_format(c) for c in cells])
            i += 1
            continue
        else:
            close_table()

        if not stripped:
            close_lists()
            i += 1
            continue

        if re.match(r'^(---|___|\*\*\*)$', stripped):
            close_lists()
            html_out.append('<hr class="divider" />')
            i += 1
            continue

        # Headings
        h_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if h_match:
            close_lists()
            level = len(h_match.group(1))
            h_raw = h_match.group(2).strip()
            h_text = inline_format(h_raw)
            
            # Skip title repeats at the beginning
            if level == 1 and i < 5:
                i += 1
                continue
            if level == 2 and i < 8 and ("Aplikasi" in h_raw or "SilatTrack" in h_raw):
                i += 1
                continue
                
            is_major_section = False
            if level == 2 and re.match(r'^\d+\.', h_raw):
                is_major_section = True
            elif level == 1:
                is_major_section = True
                
            if is_major_section and i > 25:
                html_out.append(f'<div class="page-break"></div>')
                
            html_out.append(f'<h{level}>{h_text}</h{level}>')
            
            # Diagram Placeholders for SRS
            if doc_key == "SRS":
                if "2. Gambaran Umum Sistem" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_USE_CASE]]</p>
                        <div class="image-caption">Gambar 1: Use Case Diagram Sistem Absensi Ekstrakurikuler Pencak Silat (SilatTrack)</div>
                    </div>
                    ''')
                elif "2.2 Kelas Pengguna dan Hak Akses" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_ADMIN]]</p>
                        <div class="image-caption">Gambar 2: Activity Diagram Alur Kerja Administrator & Pembina Eskul</div>
                    </div>
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_PELATIH]]</p>
                        <div class="image-caption">Gambar 3: Activity Diagram Alur Kerja Pelatih / Coach di Lapangan</div>
                    </div>
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_ANGGOTA]]</p>
                        <div class="image-caption">Gambar 4: Activity Diagram Alur Kerja Anggota / Siswa Pesilat</div>
                    </div>
                    ''')

            # Diagram Placeholders for PRD
            elif doc_key == "PRD":
                if "2. User Personas & Roles" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_USE_CASE]]</p>
                        <div class="image-caption">Gambar 1: Arsitektur Interaksi Pengguna & Use Case Diagram SilatTrack</div>
                    </div>
                    ''')

            # Diagram Placeholders for MANUAL_BOOK
            elif doc_key == "MANUAL":
                if "4. PANDUAN PENGGUNA: ADMINISTRATOR" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_ADMIN]]</p>
                        <div class="image-caption">Diagram Alur Operasional Administrator / Pembina Eskul</div>
                    </div>
                    ''')
                elif "5. PANDUAN PENGGUNA: PELATIH" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_PELATIH]]</p>
                        <div class="image-caption">Diagram Alur Operasional Pelatih / Coach di Lapangan</div>
                    </div>
                    ''')
                elif "6. PANDUAN PENGGUNA: ANGGOTA" in h_raw:
                    html_out.append('''
                    <div class="image-placeholder-block">
                        <p style="text-align:center;">[[IMG_ACT_ANGGOTA]]</p>
                        <div class="image-caption">Diagram Alur Operasional Anggota / Siswa Pesilat</div>
                    </div>
                    ''')

            i += 1
            continue

        # Ordered List
        ol_match = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if ol_match:
            if not in_ol:
                close_lists()
                in_ol = True
                html_out.append('<ol>')
            html_out.append(f'<li>{inline_format(ol_match.group(2))}</li>')
            i += 1
            continue

        # Unordered List
        ul_match = re.match(r'^[\*\-]\s+(.*)$', stripped)
        if ul_match:
            if not in_ul:
                close_lists()
                in_ul = True
                html_out.append('<ul>')
            html_out.append(f'<li>{inline_format(ul_match.group(1))}</li>')
            i += 1
            continue

        close_lists()
        html_out.append(f'<p>{inline_format(stripped)}</p>')
        i += 1

    close_table()
    close_code()
    close_blockquote()
    close_lists()

    return '\n'.join(html_out)

def generate_cover_page(doc_type, title, subtitle, meta_items):
    meta_rows = []
    for k, v in meta_items.items():
        meta_rows.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
    meta_table_html = f'<table class="cover-meta-table">{"".join(meta_rows)}</table>'

    return f"""
    <div class="cover-page">
        <div class="cover-header">
            <div class="cover-tagline">DOKUMENTASI RESMI REKAYASA PERANGKAT LUNAK</div>
            <div class="cover-title">{title}</div>
            <div class="cover-subtitle">{subtitle}</div>
        </div>
        {meta_table_html}
        <div class="cover-footer">
            <strong>SilatTrack Multi-School System Architecture & Documentation</strong><br/>
            Sistem Absensi & Manajemen Ekstrakurikuler Pencak Silat Berbasis Multi-Sekolah<br/>
            &copy; 2026 Tim Pengembang SilatTrack. All rights reserved.
        </div>
    </div>
    <div class="page-break"></div>
    """

DOCUMENTS = [
    {
        "key": "SRS",
        "src_md": os.path.join(DOCS_DIR, "SRS.md"),
        "out_html": os.path.join(DOCS_DIR, "SRS_SilatTrack.html"),
        "out_docx": os.path.join(DOCS_DIR, "SRS_SilatTrack.docx"),
        "title": "SOFTWARE REQUIREMENTS SPECIFICATION (SRS)",
        "subtitle": "SilatTrack: Sistem Absensi dan Manajemen Ekstrakurikuler Pencak Silat Multi-Sekolah",
        "meta": {
            "Nama Dokumen": "Software Requirements Specification (SRS)",
            "Produk Target": "SilatTrack Multi-School System",
            "Versi Dokumen": "1.3.0 (Official Production Release)",
            "Tanggal Rilis": "09 November 2026",
            "Target Implementasi": "Institusi Sekolah Mitra & Dewan Perguruan Silat",
            "Tech Stack": "DATH Stack (Django 5.2, Alpine.js 3, Tailwind M3, HTMX 2, face-api.js)",
            "Status Persetujuan": "Telah Diverifikasi & Siap Produksi (Approved)"
        }
    },
    {
        "key": "PRD",
        "src_md": os.path.join(DOCS_DIR, "PRD.md"),
        "out_html": os.path.join(DOCS_DIR, "PRD_SilatTrack.html"),
        "out_docx": os.path.join(DOCS_DIR, "PRD_SilatTrack.docx"),
        "title": "PRODUCT REQUIREMENTS DOCUMENT (PRD)",
        "subtitle": "SilatTrack: Sistem Absensi & Manajemen Eskul Pencak Silat Multi-Sekolah",
        "meta": {
            "Nama Dokumen": "Product Requirements Document (PRD)",
            "Nama Produk": "SilatTrack (Sistem Absensi Eskul Pencak Silat)",
            "Versi Dokumen": "1.3.0 (Komprehensif November 2026)",
            "Arsitektur": "HTML-over-the-Wire / Modern Monolith (DATH Stack)",
            "Design System": "Google Material Design 3 (M3) Crimson & Gold",
            "Target Pengguna": "Pembina Sekolah, Pelatih Silat, Anggota, Orang Tua",
            "Status Rilis": "Production Deployment Ready"
        }
    },
    {
        "key": "ERD",
        "src_md": os.path.join(DOCS_DIR, "ERD.md"),
        "out_html": os.path.join(DOCS_DIR, "ERD_SilatTrack.html"),
        "out_docx": os.path.join(DOCS_DIR, "ERD_SilatTrack.docx"),
        "title": "ENTITY RELATIONSHIP DIAGRAM (ERD) & DATA DICTIONARY",
        "subtitle": "Spesifikasi Model Data Relasional & Django ORM SilatTrack",
        "meta": {
            "Nama Dokumen": "ERD & Data Dictionary Specification",
            "Database Engine": "PostgreSQL 15+ / SQLite 3 (Django ORM 5.2)",
            "Tingkat Normalisasi": "Third Normal Form (3NF) Verified",
            "Versi Dokumen": "1.3.0 (Updated: November 2026)",
            "Jumlah Entitas Inti": "12 Entitas Utama (Multi-School, Biometrik, Sesi, RBAC)",
            "Status Model": "Normalized, Indexed, and Production-Ready"
        }
    },
    {
        "key": "MANUAL",
        "src_md": os.path.join(DOCS_DIR, "MANUAL_BOOK.md"),
        "out_html": os.path.join(DOCS_DIR, "MANUAL_BOOK_SilatTrack.html"),
        "out_docx": os.path.join(DOCS_DIR, "MANUAL_BOOK_SilatTrack.docx"),
        "title": "BUKU PANDUAN PENGGUNA (MANUAL BOOK)",
        "subtitle": "SilatTrack: Sistem Absensi & Manajemen Eskul Pencak Silat Multi-Sekolah",
        "meta": {
            "Nama Dokumen": "Buku Panduan Pengguna (User Manual Book)",
            "Aplikasi": "SilatTrack Multi-School Edition",
            "Versi Dokumen": "1.2.0 (Edisi Rilis Resmi)",
            "Target Pengguna": "Administrator, Pelatih (Coach), Anggota (Pesilat), Orang Tua",
            "Teknologi": "DATH Stack (Django, Alpine.js, Tailwind M3, HTMX, face-api.js)",
            "Tanggal Rilis": "November 2026",
            "Panduan Utama": "Presensi Wajah AI, Rolling QR, KTA Digital, Laporan & Cetak Kop"
        }
    }
]

def build_all_html():
    print("Generating HTML files from Markdown...")
    for doc in DOCUMENTS:
        with open(doc["src_md"], "r", encoding="utf-8") as f:
            md_content = f.read()

        cover_html = generate_cover_page(
            doc["key"], doc["title"], doc["subtitle"], doc["meta"]
        )
        body_html = parse_markdown_to_html(md_content, doc["key"])

        full_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>{doc["title"]}</title>
{CSS_STYLES}
</head>
<body>
{cover_html}
{body_html}
</body>
</html>
"""
        with open(doc["out_html"], "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"  [OK] HTML written: {os.path.basename(doc['out_html'])}")

if __name__ == "__main__":
    build_all_html()
