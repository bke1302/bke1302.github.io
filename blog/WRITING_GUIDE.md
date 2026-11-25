# FlowOps AI — Blog writing guide (for the cloud writer agent)

## Goal
Each post brings Israeli business owners from Google to flowopsai.co.il and makes them message us on WhatsApp.
One post = one search intent (the topic's `keyword`). Quality over volume: Google penalises thin, mass-produced content.

## Process (every run)
1. Read `blog/topics.json`. Take the FIRST item with `"status": "pending"`. If none: stop and report "queue empty".
2. Read `blog/posts/whatsapp-lead-response-aesthetic-clinic.json` — the reference post. Match its depth, structure and tone.
3. Write `blog/posts/<slug>.json` (schema below). `slug` = topic slug, `date` = today (YYYY-MM-DD, Asia/Jerusalem).
4. Pick up to 3 `related` slugs from existing files in `blog/posts/` (closest topics). Never invent slugs.
5. Run `python3 tools/build_blog.py`. If it fails, fix the JSON and rerun until it passes. Never edit the builder.
6. In `blog/topics.json` set the topic's `"status": "published"` and add `"published": "<date>"`.
7. Commit ONLY `blog/posts/<slug>.json` and `blog/topics.json` (do not commit generated HTML or sitemap; the GitHub Action rebuilds them).
8. Push to a new branch `claude/blog-<slug>`. A GitHub Action publishes it to the live site and notifies search engines. Do not open a PR.

## Voice and content rules
- Hebrew, plain and direct, as a business owner talks. Address the reader in plural ("אתם"). Short paragraphs.
- Open with a concrete scene from the reader's day, not a definition.
- Every section must be useful even if the reader never contacts us: steps, checklists, how to calculate, what to watch for.
- NO invented statistics, studies, percentages, client names or testimonials. If you want a number, show the reader how to calculate it from their own data, or label it clearly as an illustrative example ("לדוגמה").
- No emojis. No exclamation-mark hype. No "בעידן הדיגיטלי", "מהפכה", "game changer".
- Do not name competitors. Do not promise results. No medical, legal or tax advice — say "התייעצו עם איש מקצוע" where relevant.
- Be honest about limits (what AI does NOT do). This builds trust and is a FlowOps differentiator.
- Legal: never suggest sending marketing messages to people who did not opt in (Israeli spam law, section 30A). Inbound and existing customers only.
- Positioning: FlowOps AI "מכניסים בינה מלאכותית לעסק". A bot answers messages; a digital employee (עובד דיגיטלי) does the work end to end and brings back money already in the business. Mention FlowOps lightly, at most twice in the body; the CTA section does the selling.
- What our agent (Danit) does, binding, and it overrides a topic's `angle`: Danit answers a business's customers on WhatsApp according to its price list. She does NOT book appointments in a calendar and does NOT send reminders. A request for an appointment or a visit is passed to the business owner with all the details, and the owner approves. Never write that our agent or FlowOps books, schedules, fills cancellations in the calendar or sends reminders. A general guide may describe such tools on the market, but must not imply that Danit does it.
- Offer facts, if mentioned at all: 490 ש"ח a month, no setup fee; nothing to pay until Danit answers the business's customers, and from that day two weeks free; cancel with one message. No guarantee. The official WhatsApp connection needs Meta approval: never promise a date or a number of days. Only the character Danit. A call with Barak is "שיחה של 20 דקות", never "שיחת וידאו".
- Length: 900-1400 Hebrew words in `body_html`. Use 5-7 `<h2>` sections.
- Include the topic `keyword` naturally in `h1`, `meta_title`, first paragraph and one `<h2>`.
- Internal links (1-3, inside body): `/demo.html`, `/lead-responder.html` (clinics/beauty/booking topics only), `/ai-automation-small-business.html`, `/ai-process-consulting.html`, `/ai-automation-call-center.html`, `/portfolio.html`, or `/blog/<existing-slug>.html`.

## JSON schema
```
{
  "slug": "kebab-case-latin",
  "date": "YYYY-MM-DD",
  "meta_title": "<= 70 chars, keyword first, ends with ' | FlowOps AI'",
  "description": "70-165 chars, benefit + what the guide covers",
  "keywords": "5 comma-separated Hebrew phrases",
  "h1": "short, contains keyword",
  "h1_sub": "one-line promise",
  "lead": "2-3 sentences: the problem and what the reader will get",
  "body_html": "HTML string",
  "faq": [{"q": "...", "a": "..."}],          // 3-5 real objections/questions, plain-text answers
  "cta": {
    "title": "...", "text": "...",
    "wa_text": "היי, הגעתי מהמדריך על <topic> ואשמח לפרטים",
    "page": "<topic cta_page if not empty>", "page_label": "<label for that page>"
  },
  "related": ["existing-slug", ...]
}
```
Omit `page`/`page_label` when the topic's `cta_page` is empty.

## Allowed HTML in body_html
Tags: p, h2, h3, ul, ol, li, strong, em, b, a, br, div, table, thead, tbody, tr, th, td.
Classes: `lead-card` (one highlighted insight box: `<div class="lead-card"><p><strong>..</strong> ..</p></div>`),
`ucase` + `uc` (card grid: `<div class="ucase"><div class="uc"><h3>..</h3><p>..</p></div>...</div>`, 2 or 4 cards),
`table-wrap` (wrap every table). No style/onclick/id attributes, no images, no external links.
