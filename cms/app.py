from __future__ import annotations

import re
import secrets
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import bleach
import frontmatter
import markdown
from flask import Flask, abort, flash, jsonify, redirect, render_template_string, request, session, url_for


ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "_drafts"
POSTS = ROOT / "_posts"
PORT = 8765
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict")

MARKDOWN = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists"])
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "p", "pre", "code", "hr", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td",
    "br", "img", "del", "input",
}
ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "th": ["align"], "td": ["align"], "input": ["type", "checked", "disabled"],
}

SHELL = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ page_title }} · CMS Projeto Abandonado</title>
<style>
:root{color-scheme:dark;--bg:#0a0a0a;--panel:#111;--text:#ece9df;--muted:#99958a;--line:#303030;--purple:#8755cf;--lime:#c7f45a;--mono:'Courier New',monospace;--sans:Arial,sans-serif}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 var(--sans)}a{color:var(--lime)}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--lime);outline-offset:3px}.bar{display:flex;justify-content:space-between;align-items:center;gap:20px;padding:16px max(20px,calc((100% - 1180px)/2));border-bottom:1px solid var(--line);font:12px var(--mono);text-transform:uppercase}.bar strong{color:var(--lime);letter-spacing:.1em}.bar nav{display:flex;gap:18px}.container{width:min(calc(100% - 32px),1180px);margin:36px auto 72px}h1{font-size:clamp(30px,5vw,48px);line-height:1.05;letter-spacing:-.04em}h2{font-size:23px}.subtle{color:var(--muted)}.flash{padding:12px 16px;border:1px solid var(--lime);background:#c7f45a12}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:14px}.button,button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:9px 14px;border:1px solid var(--lime);background:transparent;color:var(--lime);font:12px var(--mono);text-transform:uppercase;cursor:pointer;text-decoration:none}.button:hover,button:hover{background:var(--lime);color:#111}.button.primary{background:var(--lime);color:#111}.post-table{width:100%;border-collapse:collapse;margin-top:24px}.post-table th,.post-table td{padding:13px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}.post-table th{color:var(--muted);font:11px var(--mono);text-transform:uppercase}.badge{display:inline-block;padding:2px 7px;border:1px solid var(--line);color:var(--lime);font:10px var(--mono);text-transform:uppercase}.actions{white-space:nowrap}.actions a{margin-right:9px}.danger{color:#ff827c}.editor-form{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px}.fields,.preview-panel{padding:20px;border:1px solid var(--line);background:var(--panel)}.field{margin-bottom:14px}.field label{display:block;margin-bottom:5px;color:var(--lime);font:11px var(--mono);letter-spacing:.04em;text-transform:uppercase}.field input,.field textarea,.field select{width:100%;padding:10px;border:1px solid #444;background:#080808;color:var(--text);font:14px var(--sans)}.field textarea{min-height:340px;resize:vertical;font:14px/1.6 var(--mono)}.field input:focus,.field textarea:focus,.field select:focus{border-color:var(--lime)}.grid-two{display:grid;grid-template-columns:1fr 1fr;gap:12px}.preview-panel{min-height:520px}.preview-panel h2{margin-top:0}.preview-body{overflow-wrap:anywhere}.preview-body img{max-width:100%}.preview-body pre{overflow:auto;padding:12px;background:#080808}.preview-body blockquote{border-left:2px solid var(--purple);padding-left:14px;color:#ccc}.preview-body a{color:var(--lime)}.form-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.hint{color:var(--muted);font-size:12px}.empty{margin-top:22px;padding:24px;border:1px dashed var(--line);color:var(--muted)}@media(max-width:800px){.editor-form{grid-template-columns:1fr}.preview-panel{min-height:300px}.post-table th:nth-child(3),.post-table td:nth-child(3){display:none}}@media(max-width:520px){.bar{align-items:flex-start;flex-direction:column}.bar nav{flex-wrap:wrap}.container{margin-top:24px}.grid-two{grid-template-columns:1fr}.post-table th:nth-child(2),.post-table td:nth-child(2){display:none}.post-table th,.post-table td{padding-inline:5px}}
</style></head><body>
<header class="bar"><a href="{{ url_for('home') }}"><strong>Projeto Abandonado</strong> / CMS local</a><nav><a href="{{ url_for('home') }}">Posts</a><a href="{{ url_for('editor') }}">Novo post</a><a href="{{ url_for('instructions') }}">Ajuda</a><a href="http://127.0.0.1:4000/" target="_blank" rel="noreferrer">Site local</a></nav></header>
<main class="container">{% with messages = get_flashed_messages() %}{% for message in messages %}<p class="flash" role="status">{{ message }}</p>{% endfor %}{% endwith %}{{ content|safe }}</main>
</body></html>"""

HOME = """<div class="toolbar"><div><p class="subtle">Editor local · os arquivos permanecem neste computador</p><h1>Entradas</h1></div><a class="button primary" href="{{ url_for('editor') }}">+ Escrever</a></div>
{% if posts %}<table class="post-table"><thead><tr><th>Título</th><th>Data</th><th>Estado</th><th>Ações</th></tr></thead><tbody>{% for item in posts %}<tr><td><a href="{{ url_for('editor', kind=item.kind, filename=item.filename) }}">{{ item.title }}</a></td><td>{{ item.date }}</td><td><span class="badge">{{ 'Rascunho' if item.kind == 'draft' else 'Publicado' }}</span></td><td class="actions"><a href="{{ url_for('editor', kind=item.kind, filename=item.filename) }}">Editar</a>{% if item.kind == 'post' %}<a href="{{ item.url }}" target="_blank" rel="noreferrer">Abrir</a>{% endif %}<form action="{{ url_for('delete_post') }}" method="post" style="display:inline" onsubmit="return confirm('Excluir esta entrada? Esta ação não pode ser desfeita.');"><input type="hidden" name="csrf_token" value="{{ csrf_token }}"><input type="hidden" name="kind" value="{{ item.kind }}"><input type="hidden" name="filename" value="{{ item.filename }}"><button class="danger" type="submit">Excluir</button></form></td></tr>{% endfor %}</tbody></table>{% else %}<div class="empty">Ainda não há entradas. Crie um rascunho para começar.</div>{% endif %}
<p class="hint">O CMS não envia arquivos ao GitHub. Publique pelo seu fluxo Git habitual, quando decidir.</p>"""

EDITOR = """<p><a href="{{ url_for('home') }}">← Todas as entradas</a></p><h1>{{ 'Editar entrada' if editing else 'Nova entrada' }}</h1>
<form class="editor-form" action="{{ url_for('save_post') }}" method="post">
<section class="fields" aria-label="Editor">
<input type="hidden" name="csrf_token" value="{{ csrf_token }}"><input type="hidden" name="original_kind" value="{{ item.kind if item else '' }}"><input type="hidden" name="original_filename" value="{{ item.filename if item else '' }}">
<div class="field"><label for="title">Título</label><input id="title" name="title" required maxlength="160" value="{{ item.title if item else '' }}"></div>
<div class="grid-two"><div class="field"><label for="date">Data</label><input id="date" name="date" type="date" required value="{{ item.date if item else today }}"></div><div class="field"><label for="kind">Estado</label><select id="kind" name="kind"><option value="draft" {% if not item or item.kind == 'draft' %}selected{% endif %}>Rascunho</option><option value="post" {% if item and item.kind == 'post' %}selected{% endif %}>Publicado</option></select></div></div>
<div class="field"><label for="excerpt">Resumo</label><textarea id="excerpt" name="excerpt" rows="2" maxlength="300">{{ item.excerpt if item else '' }}</textarea></div>
<div class="field"><label for="tags">Tags</label><input id="tags" name="tags" value="{{ item.tags if item else '' }}" placeholder="design, ideias, diário"></div>
<div class="field"><label for="image">Imagem (caminho ou URL)</label><input id="image" name="image" value="{{ item.image if item else '/assets/images/og-cover.svg' }}" placeholder="/assets/images/minha-imagem.jpg"></div>
<div class="field"><label for="image_alt">Descrição da imagem</label><input id="image_alt" name="image_alt" value="{{ item.image_alt if item else '' }}"></div>
<div class="field"><label for="body">Texto em Markdown</label><textarea id="body" name="body" required>{{ item.body if item else '' }}</textarea></div>
<div class="form-actions"><button class="primary" type="submit">Salvar entrada</button><a class="button" href="{{ url_for('home') }}">Cancelar</a></div><p class="hint">Salvar em “Publicado” cria um arquivo em _posts. A publicação online depende de você enviar as mudanças ao GitHub.</p>
</section><aside class="preview-panel"><h2>Pré-visualização</h2><div class="preview-body" id="preview" aria-live="polite">{% if item %}{{ preview|safe }}{% else %}<p class="hint">Escreva no campo Markdown para ver a prévia.</p>{% endif %}</div></aside>
</form><meta name="csrf-token" content="{{ csrf_token }}"><script>
const bodyField=document.getElementById('body'),preview=document.getElementById('preview'),csrf=document.querySelector('meta[name="csrf-token"]').content;let timer;
bodyField.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(async()=>{try{const response=await fetch('{{ url_for('preview') }}',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:JSON.stringify({body:bodyField.value})});if(response.ok){preview.innerHTML=(await response.json()).html}}catch(error){preview.textContent='Não foi possível atualizar a prévia.'}},180)});
</script>"""

HELP = """<p><a href="{{ url_for('home') }}">← Todas as entradas</a></p><h1>Como usar o CMS</h1><ol><li>Na lista, selecione <strong>Escrever</strong> para criar uma entrada.</li><li>Preencha título, data, resumo, tags e imagem. Escreva o corpo em Markdown.</li><li>Veja a prévia à direita. Escolha “Rascunho” ou “Publicado” e salve.</li><li>Edite uma entrada na lista. Para excluir, use “Excluir” e confirme.</li><li>Para conferir o layout final do Jekyll, inicie o site local em outro terminal com <code>bundle exec jekyll serve --drafts --baseurl ""</code>.</li></ol><p>O CMS só altera arquivos no seu computador. Ele não faz commit, push ou deploy.</p>"""


def csrf_token() -> str:
    token = session.get("csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


@app.context_processor
def inject_csrf_token() -> dict[str, str]:
    return {"csrf_token": csrf_token()}


@app.before_request
def restrict_to_localhost() -> None:
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        abort(403)
    if request.host.split(":", 1)[0] not in {"127.0.0.1", "localhost"}:
        abort(403)
    if request.method == "POST":
        origin = request.headers.get("Origin")
        if origin and urlparse(origin).netloc not in {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}:
            abort(403)
        supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        if not supplied or not secrets.compare_digest(supplied, session.get("csrf_token", "")):
            abort(400, "Token de segurança inválido. Atualize a página e tente novamente.")


def render_page(title: str, body: str, **context: object) -> str:
    content = render_template_string(body, **context)
    return render_template_string(SHELL, page_title=title, content=content)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"[-\s]+", "-", value).strip("-") or "sem-titulo"


def safe_existing_path(kind: str, filename: str) -> Path:
    if kind not in {"draft", "post"} or Path(filename).name != filename or not re.fullmatch(r"[\w.-]+\.md", filename):
        abort(404)
    directory = DRAFTS if kind == "draft" else POSTS
    path = directory / filename
    if not path.is_file() or path.resolve().parent != directory.resolve():
        abort(404)
    return path


def list_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for kind, folder in (("draft", DRAFTS), ("post", POSTS)):
        folder.mkdir(parents=True, exist_ok=True)
        for path in folder.glob("*.md"):
            try:
                post = frontmatter.load(path)
            except Exception:
                continue
            post_date = str(post.get("date", ""))[:10]
            entries.append({"kind": kind, "filename": path.name, "title": str(post.get("title", path.stem)), "date": post_date})
    return sorted(entries, key=lambda entry: (entry["date"], entry["title"].casefold()), reverse=True)


def markdown_html(source: str) -> str:
    rendered = MARKDOWN.convert(source)
    MARKDOWN.reset()
    return bleach.clean(rendered, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, protocols={"http", "https", "mailto"}, strip=True)


@app.get("/")
def home() -> str:
    return render_page("Entradas", HOME, posts=list_entries())


@app.get("/help")
def instructions() -> str:
    return render_page("Ajuda", HELP)


@app.get("/new")
def editor() -> str:
    kind = request.args.get("kind")
    filename = request.args.get("filename")
    item = None
    preview = ""
    if kind or filename:
        if not kind or not filename:
            abort(404)
        path = safe_existing_path(kind, filename)
        post = frontmatter.load(path)
        tags = post.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        item = {
            "kind": kind,
            "filename": filename,
            "title": post.get("title", ""),
            "date": str(post.get("date", date.today()))[:10],
            "excerpt": post.get("excerpt", ""),
            "tags": ", ".join(str(tag) for tag in tags),
            "image": post.get("image", "/assets/images/og-cover.svg"),
            "image_alt": post.get("image_alt", ""),
            "body": post.content,
        }
        preview = markdown_html(post.content)
    return render_page("Editar entrada" if item else "Nova entrada", EDITOR, item=item, editing=bool(item), preview=preview, today=date.today().isoformat())


@app.post("/preview")
def preview() -> tuple[object, int] | object:
    data = request.get_json(silent=True) or {}
    return jsonify(html=markdown_html(str(data.get("body", ""))))


@app.post("/save")
def save_post():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    excerpt = request.form.get("excerpt", "").strip()
    image = request.form.get("image", "").strip() or "/assets/images/og-cover.svg"
    image_alt = request.form.get("image_alt", "").strip()
    kind = request.form.get("kind", "draft")
    date_text = request.form.get("date", "")
    if not title or not body or kind not in {"draft", "post"}:
        flash("Preencha título, texto e estado.")
        return redirect(url_for("editor"))
    try:
        published_date = date.fromisoformat(date_text)
    except ValueError:
        flash("Informe uma data válida.")
        return redirect(url_for("editor"))

    original_kind = request.form.get("original_kind", "")
    original_filename = request.form.get("original_filename", "")
    old_path = safe_existing_path(original_kind, original_filename) if original_kind and original_filename else None
    tags = [part.strip() for part in request.form.get("tags", "").split(",") if part.strip()]
    metadata = {"title": title, "date": published_date.isoformat(), "excerpt": excerpt, "image": image, "image_alt": image_alt, "tags": tags}
    document = frontmatter.Post(body, **metadata)
    slug = slugify(title)
    filename = f"{published_date.isoformat()}-{slug}.md" if kind == "post" else f"{slug}.md"
    directory = POSTS if kind == "post" else DRAFTS
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / filename
    if destination.exists() and destination != old_path:
        suffix = 2
        while True:
            candidate = directory / (f"{published_date.isoformat()}-{slug}-{suffix}.md" if kind == "post" else f"{slug}-{suffix}.md")
            if not candidate.exists():
                destination = candidate
                break
            suffix += 1
    destination.write_text(frontmatter.dumps(document), encoding="utf-8")
    if old_path and old_path != destination:
        old_path.unlink()
    flash("Entrada salva localmente.")
    return redirect(url_for("home"))


@app.post("/delete")
def delete_post():
    path = safe_existing_path(request.form.get("kind", ""), request.form.get("filename", ""))
    path.unlink()
    flash("Entrada excluída do computador.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    DRAFTS.mkdir(exist_ok=True)
    POSTS.mkdir(exist_ok=True)
    print(f"CMS local em http://127.0.0.1:{PORT}/ (Ctrl+C para encerrar)")
    app.run(host="127.0.0.1", port=PORT, debug=False)
