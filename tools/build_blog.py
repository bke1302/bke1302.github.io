"""FlowOps AI blog builder.

Reads blog/posts/*.json and renders:
  - blog/<slug>.html   (one page per post, site design)
  - blog/index.html    (guides listing)
  - sitemap.xml        (blog URLs merged into existing entries)

Run from repo root:  python tools/build_blog.py
Exits non-zero on any validation error, so a bad post never gets published.
"""
import html
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "blog" / "posts"
OUT = ROOT / "blog"
SITE = "https://flowopsai.co.il"
SHELL_SRC = ROOT / "ai-automation-small-business.html"
WA = "972548080657"

REQUIRED = ["slug", "date", "meta_title", "description", "keywords", "h1", "h1_sub",
            "lead", "body_html", "faq", "cta"]
ALLOWED_TAGS = {"p", "h2", "h3", "ul", "ol", "li", "strong", "em", "b", "a", "div", "br",
                "table", "thead", "tbody", "tr", "th", "td"}
ALLOWED_CLASSES = {"lead-card", "ucase", "uc", "table-wrap"}


class BodyValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.errors.append(f"tag not allowed: <{tag}>")
        for k, v in attrs:
            if k.startswith("on") or k == "style":
                self.errors.append(f"attribute not allowed: {k}")
            elif k == "class" and not set((v or "").split()) <= ALLOWED_CLASSES:
                self.errors.append(f"class not allowed: {v}")
            elif k == "href" and not re.match(r"^(/|https://flowopsai\.co\.il/|https://wa\.me/)", v or ""):
                self.errors.append(f"external/unsafe link: {v}")
            elif k not in ("class", "href"):
                self.errors.append(f"attribute not allowed: {k}")


def shell_parts():
    """Body chrome (nav, footer, a11y widgets) taken from an existing page, paths made absolute."""
    src = SHELL_SRC.read_text(encoding="utf-8")
    top = src[src.index("<body>"):src.index('<header class="page-hero">')]
    bottom = src[src.index("<footer>"):]
    fix = lambda s: (s.replace('src="flowops-mark.png"', 'src="/flowops-mark.png"')
                      .replace('src="pages.js"', 'src="/pages.js"'))
    bottom = bottom.replace(
        '<a href="/portfolio.html" style="color:#9FB6CC">תיק עבודות</a>',
        '<a href="/portfolio.html" style="color:#9FB6CC">תיק עבודות</a>\n'
        '      <span style="opacity:.5;margin:0 8px">·</span>\n'
        '      <a href="/blog/" style="color:#9FB6CC">מדריכים</a>', 1)
    return fix(top), fix(bottom)


def head(title, desc, keywords, url, ld_blocks, og_type="article"):
    e = html.escape
    lds = "\n".join(f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False)}\n</script>'
                    for b in ld_blocks)
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="keywords" content="{e(keywords)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.jpg">
<meta property="og:locale" content="he_IL">
<meta property="og:site_name" content="FlowOps AI">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#0A1424">
<link rel="canonical" href="{url}">
<link rel="icon" href="/flowops-mark.png">
{lds}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/pages.css">
</head>
"""


def wa_link(text):
    return f"https://wa.me/{WA}?text={quote(text)}"


def validate(post, path, slugs):
    errs = [f"missing field: {k}" for k in REQUIRED if not post.get(k)]
    if errs:
        return errs
    if post["slug"] != path.stem:
        errs.append("slug must match file name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", post["slug"]):
        errs.append("slug must be lowercase latin words joined by -")
    if len(post["meta_title"]) > 70:
        errs.append("meta_title over 70 chars")
    if not 70 <= len(post["description"]) <= 165:
        errs.append("description must be 70-165 chars")
    v = BodyValidator()
    v.feed(post["body_html"])
    errs += v.errors
    words = len(re.sub(r"<[^>]+>", " ", post["body_html"]).split())
    if words < 600:
        errs.append(f"body too short: {words} words (min 600)")
    if len(post["faq"]) < 3:
        errs.append("need at least 3 FAQ items")
    for r in post.get("related", []):
        if r not in slugs:
            errs.append(f"related slug not found: {r}")
    for k in ("title", "text", "wa_text"):
        if not post["cta"].get(k):
            errs.append(f"cta.{k} missing")
    return errs


def render_post(post, posts_by_slug, top, bottom):
    e = html.escape
    url = f"{SITE}/blog/{post['slug']}.html"
    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": post["h1"],
         "description": post["description"], "datePublished": post["date"],
         "dateModified": post.get("updated", post["date"]), "inLanguage": "he-IL",
         "mainEntityOfPage": url, "image": f"{SITE}/og-image.jpg",
         "author": {"@type": "Person", "name": "ברק", "url": f"{SITE}/"},
         "publisher": {"@type": "Organization", "name": "FlowOps AI", "url": f"{SITE}/",
                       "logo": {"@type": "ImageObject", "url": f"{SITE}/flowops-mark.png"}}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "דף הבית", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "מדריכים", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": post["h1"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in post["faq"]]},
    ]
    faq = "\n".join(
        f'    <div class="faq-item"><button class="faq-q" aria-expanded="false">{e(f["q"])}</button>'
        f'<div class="faq-a"><p>{e(f["a"])}</p></div></div>' for f in post["faq"])
    cta = post["cta"]
    second = (f'<a href="{e(cta["page"])}">{e(cta.get("page_label", "לפרטים נוספים"))}</a> · '
              if cta.get("page") else "")
    related = [posts_by_slug[s] for s in post.get("related", [])][:3]
    rel_links = "\n".join(
        f'      <a href="/blog/{r["slug"]}.html">{e(r["h1"])}<span>{e(r["h1_sub"])}</span></a>' for r in related)
    if len(related) < 3:
        rel_links += '\n      <a href="/blog/">כל המדריכים<span>עוד מדריכי AI ואוטומציה לעסקים</span></a>'
    d = date.fromisoformat(post["date"])
    return head(post["meta_title"], post["description"], post["keywords"], url, ld) + top + f"""<header class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="פירורי לחם"><a href="/">דף הבית</a> ‹ <a href="/blog/">מדריכים</a> ‹ {e(post["h1"])}</nav>
    <h1>{e(post["h1"])} <span>{e(post["h1_sub"])}</span></h1>
    <p class="lead">{e(post["lead"])}</p>
    <p class="post-meta">ברק, FlowOps AI · <time datetime="{post["date"]}">{d.day}.{d.month}.{d.year}</time></p>
  </div>
</header>
<main id="main">
<section class="content">
  <div class="wrap">
{post["body_html"]}
  </div>
</section>
<section class="content" style="padding-top:0">
  <div class="wrap">
    <h2>שאלות נפוצות</h2>
{faq}
  </div>
</section>
<section class="cta-band">
  <div class="wrap">
    <h2>{e(cta["title"])}</h2>
    <p>{e(cta["text"])}</p>
    <a href="{wa_link(cta["wa_text"])}" class="btn">דברו איתנו בוואטסאפ</a>
    <p style="margin-top:14px">{second}<a href="/demo.html">דוגמה חיה לעובד דיגיטלי, בלי הרשמה</a></p>
  </div>
</section>
<section class="related">
  <div class="wrap">
    <h2>להמשך קריאה</h2>
    <div class="related-grid">
{rel_links}
    </div>
  </div>
</section>
</main>
""" + bottom


def render_index(posts, top, bottom):
    e = html.escape
    url = f"{SITE}/blog/"
    title = "מדריכי AI ואוטומציה לעסקים בישראל | FlowOps AI"
    desc = "מדריכים מעשיים להכנסת בינה מלאכותית לעסק: סוכני AI, אוטומציות משרד, מענה ללידים וחיסכון בזמן. כתוב בשפה פשוטה, עם דוגמאות מעסקים בישראל."
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "מדריכי FlowOps AI", "url": url,
           "inLanguage": "he-IL", "blogPost": [
               {"@type": "BlogPosting", "headline": p["h1"], "url": f"{SITE}/blog/{p['slug']}.html",
                "datePublished": p["date"]} for p in posts]}]
    cards = "\n".join(
        f'      <a href="/blog/{p["slug"]}.html">{e(p["h1"])}<span>{e(p["description"])}</span></a>'
        for p in posts)
    return head(title, desc, "מדריכי AI לעסקים, אוטומציה לעסקים, סוכני AI", url, ld, "website") + top + f"""<header class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="פירורי לחם"><a href="/">דף הבית</a> ‹ מדריכים</nav>
    <h1>מדריכים <span>AI ואוטומציה לעסקים, בלי ז'רגון</span></h1>
    <p class="lead">איך עסקים בישראל חוסכים שעות עבודה, עונים מהר יותר ללקוחות ומחזירים כסף שכבר נמצא אצלם בעסק. מדריכים מעשיים מהשטח.</p>
  </div>
</header>
<main id="main">
<section class="related">
  <div class="wrap">
    <div class="related-grid post-list">
{cards}
    </div>
  </div>
</section>
</main>
""" + bottom


def update_sitemap(posts):
    sm = ROOT / "sitemap.xml"
    xml = sm.read_text(encoding="utf-8")
    xml = re.sub(r"\s*<url>\s*<loc>https://flowopsai\.co\.il/blog/.*?</url>", "", xml, flags=re.S)
    newest = max(p.get("updated", p["date"]) for p in posts)
    entries = [(f"{SITE}/blog/", newest, "weekly", "0.8")] + [
        (f"{SITE}/blog/{p['slug']}.html", p.get("updated", p["date"]), "monthly", "0.7") for p in posts]
    block = "".join(f"\n  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n"
                    f"    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n  </url>"
                    for u, d, c, pr in entries)
    sm.write_text(xml.replace("\n</urlset>", block + "\n</urlset>"), encoding="utf-8")


def main():
    files = sorted(POSTS.glob("*.json"))
    posts, errors = [], []
    for f in files:
        try:
            posts.append((f, json.loads(f.read_text(encoding="utf-8"))))
        except json.JSONDecodeError as ex:
            errors.append(f"{f.name}: invalid JSON: {ex}")
    slugs = {p.get("slug") for _, p in posts}
    for f, p in posts:
        errors += [f"{f.name}: {m}" for m in validate(p, f, slugs)]
    if errors:
        print("BUILD FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)
    posts = sorted((p for _, p in posts), key=lambda p: p["date"], reverse=True)
    if not posts:
        print("no posts")
        return
    by_slug = {p["slug"]: p for p in posts}
    top, bottom = shell_parts()
    for p in posts:
        (OUT / f"{p['slug']}.html").write_text(render_post(p, by_slug, top, bottom), encoding="utf-8")
    (OUT / "index.html").write_text(render_index(posts, top, bottom), encoding="utf-8")
    update_sitemap(posts)
    print(f"built {len(posts)} posts + blog/index.html + sitemap.xml")


if __name__ == "__main__":
    main()
