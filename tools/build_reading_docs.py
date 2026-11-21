"""Generate per-chapter summary files and the claims list from the built course page.

Pass 1 of the reading workflow, done mechanically: for every chapter lesson, pull out the
summary paragraphs, the section outline, sentences that carry a number, the named terms,
the interview line, the AWS mapping and the takeaways.

    python course/build.py                      # builds course/index.html
    python tools/build_reading_docs.py course/index.html

Writes docs/chapters/<book>/chapter-NN-summary.md and docs/claims.md, and (through
course/synthesis.py) docs/executive-summary.md, knowledge-map.md and requirements.md.
"""
import html as H
import os
import re
import sys

SRC = open(sys.argv[1] if len(sys.argv) > 1 else "course/index.html", encoding="utf-8").read()
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

PE_FINAL = {1: 9, 2: 10, 3: 12, 4: 14, 5: 15, 6: 16, 7: 18, 8: 19, 9: 22, 10: 24}
SRE_READ = {**{n: "full text, two passes" for n in list(range(4, 8)) + list(range(10, 24))},
            **{n: "full text, re-read in a third pass" for n in (1, 2, 3, 9)}, 8: "full text, first pass"}
UNIT = re.compile(r"(%|×|\bminutes?\b|\bhours?\b|\bdays?\b|\bweeks?\b|\bmonths?\b|\byears?\b|billion|million|quadrillion|\$|\bnines\b|"
                  r"\bengineers?\b|\btimes\b|-fold|\bfold\b|\bpeople\b|\bteams?\b|\bregions?\b|\bzones?\b|\brecommendations\b|\bpercent\b|\bh\b)", re.I)


def text(fragment):
    t = re.sub(r"<(svg|pre|details|button|table)\b.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"</(p|li|h\d|td|th|div|span|b)>", lambda m: ". " if m.group(1) in ("p", "li", "h2", "h3", "td", "div") else " ", t)
    t = H.unescape(re.sub(r"<[^>]+>", "", t))
    return re.sub(r"\s+", " ", re.sub(r"\.(\s*\.)+", ".", t)).strip()


def md(fragment):
    t = re.sub(r"<b>(.*?)</b>", r"**\1**", fragment, flags=re.S)
    t = re.sub(r"<i>(.*?)</i>", r"*\1*", t, flags=re.S)
    t = re.sub(r"<code>(.*?)</code>", r"`\1`", t, flags=re.S)
    return H.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+(?=[A-Z“\"(0-9])", t) if s.strip()]


def claims_from(body):
    out, seen = [], set()
    for s in sentences(text(body)):
        if not (40 <= len(s) <= 260) or not re.search(r"\d", s) or not UNIT.search(s):
            continue
        if re.match(r"(After Figure|Figure|Chapter|POC|Run |My drawing|Days? \d)", s) or s.endswith("?") or "→" in s or " . " in s:
            continue
        key = re.sub(r"\W+", "", s.lower())[:60]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out[:10]


def terms_from(body):
    out, seen = [], set()
    for b in re.findall(r"<b>(.*?)</b>", re.sub(r"<(svg|details)\b.*?</\1>", "", body, flags=re.S), re.S):
        t = H.unescape(re.sub(r"<[^>]+>", "", b)).strip(" .:,")
        if 1 <= len(t.split()) <= 4 and len(t) > 3 and t.lower() not in seen and not re.match(r"(Yes|No|Now|Next|Later|Before|After|Type \d|\d)", t):
            seen.add(t.lower())
            out.append(t)
    return out[:16]


def lesson(sec_id):
    m = re.search(r'<section class="lesson" id="%s"[^>]*>(.*?)</section>' % re.escape(sec_id), SRC, re.S)
    s = m.group(1)
    title = md(re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))
    meta = md(re.search(r'<div class="meta">(.*?)</div>', s, re.S).group(1))
    learn = [md(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<div class="learn">.*?<ul>(.*?)</ul>', s, re.S).group(1), re.S)]
    after_learn = s[re.search(r'<div class="learn">.*?</ul></div>', s, re.S).end():]
    cut = min([i for i in (after_learn.find('<div class="say">'), after_learn.find('<h2>Interview practice</h2>'), after_learn.find('<div class="take">')) if i >= 0])
    body = after_learn[:cut]
    say = re.search(r'<div class="say"><b>.*?</b><p>(.*?)</p></div>', s, re.S)
    aws = re.search(r'<div class="note aws"><b>On AWS</b>(.*?)</div>', s, re.S)
    take = [md(x) for x in re.findall(r"<li>(.*?)</li>", re.search(r'<div class="take">.*?<ul>(.*?)</ul>', s, re.S).group(1), re.S)]
    head = re.sub(r"<(figure|table|details)\b.*?</\1>", "", body.split('<div class="deeper">')[0], flags=re.S)
    paras, n_p = [], 0
    for m in re.finditer(r'<p>(.*?)</p>|<div class="(?:flow|tiles)">(.*?)</div></div>', head, re.S):
        if m.group(1) is not None:
            t = md(m.group(1))
            if len(t) > 60:
                paras.append(t)
                n_p += 1
        elif n_p < 2:  # a diagram that opens the lesson carries the definitions: keep it as a list
            boxes = re.findall(r"<b>(.*?)</b><span>(.*?)</span>", m.group(2) + "</div>", re.S)
            paras.append("\n".join(f"- **{md(a)}**" + (f": {md(b)}" if md(b) else "") for a, b in boxes))
        if n_p >= 4:
            break
    outline = [md(h) for h in re.findall(r"<h2>(.*?)</h2>", body, re.S)]
    poc = re.search(r"POC [\d ·,]+\d", meta)
    return dict(title=title, meta=meta, learn=learn, summary=paras, outline=outline, claims=claims_from(body), terms=terms_from(body),
                say=md(say.group(1)) if say else "", aws=md(aws.group(1)) if aws else "", take=take, poc=poc.group(0) if poc else "")


def write_chapter(book, n, sec_id, coverage, suffix=""):
    d = lesson(sec_id)
    lines = [f"# {book['short']} chapter {n}{' (' + suffix.strip('-') + ')' if suffix else ''}: {d['title']}", "",
             f"*{book['name']}. Course lesson: `#{sec_id}`." + (f" Code: {d['poc']}." if d["poc"] else "") + f" Read: {coverage}.*", "",
             "## Summary", ""] + [p + "\n" for p in d["summary"]]
    lines += ["## Key ideas", ""] + [f"- {x}" for x in d["learn"]] + [""]
    lines += ["## What the lesson covers", ""] + [f"- {x}" for x in d["outline"]] + [""]
    if d["claims"]:
        lines += ["## Claims and numbers", ""] + [f"- {x}" for x in d["claims"]] + [""]
    if d["terms"]:
        lines += ["## Terms", "", ", ".join(d["terms"]), ""]
    if d["say"]:
        lines += ["## Interview line", "", d["say"], ""]
    if d["aws"]:
        lines += ["## On AWS", "", d["aws"], ""]
    lines += ["## Takeaways", ""] + [f"- {x}" for x in d["take"]] + [""]
    path = os.path.join(ROOT, "docs", "chapters", book["dir"], f"chapter-{n:02d}{suffix}-summary.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return d


SRE = dict(name="Site Reliability Engineering, 2nd Edition", short="SRE", dir="sre")
PE = dict(name="Platform Engineering at Google (early release)", short="Platform", dir="platform")

rows = []
for n in range(1, 24):
    d = write_chapter(SRE, n, f"ch-{n}", SRE_READ[n])
    rows += [("SRE", n, c) for c in d["claims"]]
for k, n in PE_FINAL.items():
    d = write_chapter(PE, n, f"pe-{k}", "full text, one pass; all figures seen")
    rows += [("Platform", n, c) for c in d["claims"]]

PROM = dict(name="Mastering Prometheus (William Hegedus, Packt, 2024)", short="Prometheus", dir="prometheus")
GRAF = dict(name="Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024)", short="Grafana", dir="grafana")
OBS_READ = "full text, one pass; all figures seen"
for n, sec, suffix in [(1, "m-1", ""), (3, "m-3", ""), (3, "m-3q", "-promql")] + [(n, f"m-{n}", "") for n in range(4, 15)]:
    d = write_chapter(PROM, n, sec, OBS_READ + ("; lesson covers chapters 1–2" if n == 1 else "; lesson covers chapters 14–15" if n == 14 else ""), suffix)
    rows += [("Prometheus", n, c) for c in d["claims"]]
for n, sec, note in [(1, "g-1", ""), (2, "g-2", "; lesson covers chapters 2–3"), (4, "g-4", ""), (5, "g-5", ""), (6, "g-6", ""), (7, "g-7", ""), (8, "g-8", ""),
                     (9, "g-9", ""), (10, "g-10", ""), (11, "g-11", ""), (12, "g-12", "; lesson covers chapters 12–13"), (14, "g-14", "; lesson covers chapters 14–15")]:
    d = write_chapter(GRAF, n, sec, OBS_READ + note)
    rows += [("Grafana", n, c) for c in d["claims"]]

sys.path.insert(0, os.path.join(ROOT, "course"))
import synthesis  # noqa: E402

curated, _ = synthesis.write_docs()
out = ["# Claims and numbers", "", curated, "## Extracted from each chapter", "",
       "Statements that carry a figure, extracted mechanically from the chapter lessons (`tools/build_reading_docs.py`) and grouped by chapter. "
       "They are in my own words; check the book before quoting a number in writing. Platform chapters use the final book's numbering; Prometheus and Grafana chapters are the Packt books.", ""]
last = None
for book, n, c in rows:
    if (book, n) != last:
        out += ["", f"### {book} chapter {n}", ""]
        last = (book, n)
    out.append(f"- {c}")
open(os.path.join(ROOT, "docs", "claims.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(len(rows), "claims;", 33 + 14 + 12, "chapter files")
