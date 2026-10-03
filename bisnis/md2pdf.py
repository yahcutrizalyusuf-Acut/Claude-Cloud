import html, re, sys, pathlib

src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
out = pathlib.Path(sys.argv[2])

def inline(t):
    t = html.escape(t)
    codes = []
    def stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes)-1}\x00"
    t = re.sub(r'`([^`]+)`', stash, t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: f"<code>{codes[int(m.group(1))]}</code>", t)
    return t

lines = src.split('\n')
h, i = [], 0
fence = False
while i < len(lines):
    ln = lines[i]

    if ln.startswith('```'):
        if not fence:
            h.append('<pre>'); fence = True
        else:
            h.append('</pre>'); fence = False
        i += 1; continue
    if fence:
        h.append(html.escape(ln)); i += 1; continue

    if re.match(r'^\s*$', ln):
        i += 1; continue

    if re.match(r'^---+\s*$', ln):
        h.append('<hr>'); i += 1; continue

    m = re.match(r'^(#{1,6})\s+(.*)$', ln)
    if m:
        lv = len(m.group(1))
        h.append(f'<h{lv}>{inline(m.group(2))}</h{lv}>'); i += 1; continue

    # tabel
    if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|[\s:|-]+\|\s*$', lines[i+1]):
        def cells(row):
            return [c.strip() for c in row.strip().strip('|').split('|')]
        head = cells(ln)
        h.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>')
        i += 2
        n = 0
        while i < len(lines) and lines[i].lstrip().startswith('|'):
            h.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells(lines[i])) + '</tr>')
            i += 1; n += 1
        if n == 0:
            # tabel tanpa isi = lembar isian; sediakan baris kosong untuk ditulis tangan
            for _ in range(10):
                h.append('<tr class="isian">' + '<td>&nbsp;</td>' * len(head) + '</tr>')
        h.append('</tbody></table>'); continue

    if ln.lstrip().startswith('> '):
        buf = []
        while i < len(lines) and lines[i].lstrip().startswith('>'):
            buf.append(lines[i].lstrip()[1:].strip()); i += 1
        h.append('<blockquote>' + inline(' '.join(x for x in buf if x)) + '</blockquote>'); continue

    # daftar centang
    if re.match(r'^\s*-\s+\[[ xX]\]\s', ln):
        h.append('<ul class="cek">')
        while i < len(lines) and re.match(r'^\s*-\s+\[[ xX]\]\s', lines[i]):
            b = [re.sub(r'^\s*-\s+\[[ xX]\]\s+', '', lines[i])]
            i += 1
            while i < len(lines) and lines[i].startswith('  ') and lines[i].strip() \
                    and not re.match(r'^\s*-\s+\[[ xX]\]\s', lines[i]):
                b.append(lines[i].strip()); i += 1
            h.append('<li>' + inline(' '.join(b)) + '</li>')
        h.append('</ul>'); continue

    if re.match(r'^\s*[-*+]\s+', ln):
        h.append('<ul>')
        while i < len(lines) and (re.match(r'^\s*[-*]\s+', lines[i]) or (lines[i].startswith('   ') and lines[i].strip() and not re.match(r'^\s*[-*0-9]', lines[i].strip()))):
            if re.match(r'^\s*[-*+]\s+', lines[i]):
                b = [re.sub(r'^\s*[-*+]\s+', '', lines[i])]
                i += 1
                while i < len(lines) and lines[i].startswith('  ') and lines[i].strip() and not re.match(r'^\s*[-*+]\s', lines[i]):
                    b.append(lines[i].strip()); i += 1
                h.append('<li>' + inline(' '.join(b)) + '</li>')
            else:
                i += 1
        h.append('</ul>'); continue

    if re.match(r'^\s*\d+\.\s+', ln):
        h.append('<ol>')
        while i < len(lines) and (re.match(r'^\s*\d+\.\s+', lines[i]) or (lines[i].startswith('   ') and lines[i].strip())):
            if re.match(r'^\s*\d+\.\s+', lines[i]):
                b = [re.sub(r'^\s*\d+\.\s+', '', lines[i])]
                i += 1
                while i < len(lines) and lines[i].startswith('   ') and lines[i].strip():
                    b.append(lines[i].strip()); i += 1
                h.append('<li>' + inline(' '.join(b)) + '</li>')
            else:
                i += 1
        h.append('</ol>'); continue

    buf = []
    while i < len(lines) and lines[i].strip() and not re.match(r'^\s*([-*+]\s|>\s|\||#{1,6}\s|\d+\.\s|```|---+\s*$)', lines[i]):
        buf.append(lines[i].strip()); i += 1
    if buf:
        h.append('<p>' + inline(' '.join(buf)) + '</p>')
    else:
        i += 1

CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
        @bottom-right { content: counter(page); } }
* { box-sizing: border-box; }
body { font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
       font-size: 10.2pt; line-height: 1.55; color: #1a1a1a; margin: 0; }
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 4pt; color: #11403a;
     border-bottom: 2.5px solid #11403a; padding-bottom: 8pt; }
h2 { font-size: 13pt; margin: 20pt 0 7pt; color: #11403a;
     page-break-after: avoid; break-after: avoid; }
h3 { font-size: 11pt; margin: 14pt 0 5pt; color: #2a5c54;
     page-break-after: avoid; break-after: avoid; }
p { margin: 0 0 7pt; text-align: justify; }
hr { border: 0; border-top: 1px solid #d4d8d6; margin: 16pt 0; }
ul, ol { margin: 0 0 8pt; padding-left: 17pt; }
li { margin-bottom: 4pt; }
ul.cek { list-style: none; padding-left: 4pt; }
ul.cek li { position: relative; padding-left: 20pt; margin-bottom: 6pt; }
ul.cek li::before { content: "\\2610"; position: absolute; left: 0; top: -1pt;
                    color: #11403a; font-size: 13pt; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 12pt;
        font-size: 9.2pt; page-break-inside: avoid; break-inside: avoid; }
th { background: #11403a; color: #fff; text-align: left;
     padding: 5pt 7pt; font-weight: 600; }
td { border-bottom: 1px solid #dde2e0; padding: 5pt 7pt; vertical-align: top; }
tbody tr:nth-child(even) { background: #f5f8f7; }
blockquote { margin: 8pt 0 10pt; padding: 7pt 12pt; background: #f2f6f5;
             border-left: 3px solid #11403a; font-style: italic;
             page-break-inside: avoid; break-inside: avoid; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt;
       background: #eef2f1; padding: 1px 4px; border-radius: 3px; }
pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt;
      background: #f5f8f7; border: 1px solid #dde2e0; border-radius: 4px;
      padding: 9pt 11pt; line-height: 1.5; white-space: pre-wrap;
      page-break-inside: avoid; break-inside: avoid; margin: 8pt 0 12pt; }
a { color: #11403a; }
tr.isian td { height: 26pt; border-bottom: 1px solid #c2cbc8; }
tr.isian:nth-child(even) { background: #fff; }
strong { color: #0d2f2a; }
.jejak { font-size: 8.5pt; color: #6b7a77; margin-top: 2pt;
         padding-bottom: 10pt; border-bottom: 1px solid #e3e8e6; }
"""

doc = f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<title>Uji Pasar Rumoh Aspirasi</title>
<style>{CSS}</style></head><body>
{chr(10).join(h)}
</body></html>"""
out.write_text(doc, encoding='utf-8')
print(f"html: {len(doc)} bytes")
