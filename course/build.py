import re, json, random, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extras as X

SRC = open(os.path.join(HERE, 'source-sre-lessons.html'), encoding='utf-8').read()
strip = lambda s: re.sub(r'<[^>]+>', '', s)

# ------------------------------------------------------------------ readability: split walls of text
ABBR = re.compile(r'(?:\b(?:e\.g|i\.e|vs|etc|Dr|St|No|approx)\.|(?:^|[\s>(“"])\d{1,2}\.|(?:^|[\s(])[A-Z]\.)$')
CAND = re.compile(r'([.?!][”"\')]*(?:</[bi]>)?)\s+(?=(?:<[bi]>)?[“"(]?[A-Z0-9])')


def balanced(s):
    return all(len(re.findall(f'<{t}[ >]', s)) == s.count(f'</{t}>') for t in ('b', 'i', 'code', 'a'))


def sentences(inner):
    out, last = [], 0
    for m in CAND.finditer(inner):
        end = m.end(1)
        if ABBR.search(strip(inner[last:end])[-8:]) or ABBR.search(inner[max(0, end - 8):end]):
            continue
        out.append(inner[last:end]); last = m.end()
    out.append(inner[last:])
    return out


def chunk(inner, lo=230, hi=400):
    if len(strip(inner)) <= hi:
        return [inner]
    groups, cur = [], ''
    for s in sentences(inner):
        cand = (cur + ' ' + s).strip()
        if cur and balanced(cur) and (len(strip(cand)) > hi or len(strip(cur)) >= lo):
            groups.append(cur); cur = s
        else:
            cur = cand
    if cur:
        groups.append(cur)
    if len(groups) > 1 and len(strip(groups[-1])) < 110:
        last = groups.pop(); groups[-1] += ' ' + last
    return groups


def split_paras(html):
    def rep(m):
        return ''.join(f'<p>{c}</p>' for c in chunk(m.group(1).strip()))
    return re.sub(r'<p>(.*?)</p>', rep, html, flags=re.S)


def grab(pattern, html):
    m = re.search(pattern, html, flags=re.S)
    return (m.group(1).strip(), html[:m.start()] + html[m.end():]) if m else (None, html)


def card(kind, n):
    key = f'data-id="{n}"' if kind == 'ch' else ''
    if kind == 'ch':
        m = re.search(r'<details class="ch" data-id="%d">.*?<div class="body">(.*?)<button class="mark">' % n, SRC, re.S)
    else:
        m = re.search(r'<details class="dx"><summary><span class="num">%d</span>.*?<div class="body">(.*?)</div></details>' % n, SRC, re.S)
    return m.group(1) if m else None


def qa(div):
    ps = re.findall(r'<p>(.*?)</p>', div, re.S)
    q = re.sub(r'^(Q:|Interview angle:)\s*', '', ps[0]).strip()
    q = re.sub(r'^"(.*)"$', r'\1', q)
    ans = ''.join(f'<p>{c}</p>' for p in ps[1:] for c in chunk(p.strip()))
    return f'<div class="iq"><p class="iqq">{q}</p><details><summary>Show a model answer</summary>{ans}</details></div>'


# ------------------------------------------------------------------ pull the data arrays out of the old page
def arr(name):
    i = SRC.index(f'const {name}=[')
    j = SRC.index('\n];', i)
    return SRC[i + len(f'const {name}=['):j]


def parse_js_rows(src):
    # rows are JS array literals; older rows use single quotes, newer ones are JSON
    rows = []
    for line in src.strip().split('\n'):
        line = line.strip().rstrip(',')
        if not line:
            continue
        if line.startswith('["') or line.startswith('[ "'):
            rows.append(json.loads(line))
        else:
            rows.append(eval(line, {'__builtins__': {}}))
    return rows


CARDS = parse_js_rows(arr('cards'))
QUIZ = parse_js_rows(arr('quiz'))
DRILLS = [[q, ''.join(f'<p>{c}</p>' for c in chunk(a))] for q, a in parse_js_rows(arr('drills'))]
AWS_TABLE = re.search(r'<table class="stack">.*?</table>', SRC, re.S).group(0)

quiz_ch = {}
for ch, idxs in X.QUIZ_OF.items():
    for i in idxs:
        quiz_ch.setdefault(ch, []).append(QUIZ[i])
for ch, q in X.NEWQ.items():
    quiz_ch.setdefault(ch, []).append(q)
    QUIZ.append(q)
import extras2 as X2
import extras3 as X3
import extras4 as X4
import synthesis as SY
CARDS += X3.CARDS
for ch, q in X2.NEWQUIZ.items():
    quiz_ch.setdefault(ch, []).insert(0, q)
    QUIZ.append(q)
CARDS += X2.NEWCARDS
QUIZ += X3.QUIZ
DRILLS += X2.NEWDRILLS


def quick(q, seed):
    order = list(range(len(q[1]))); random.Random(seed).shuffle(order)
    ans = order.index(q[2])
    return (f'<div class="quiz" data-answer="{ans}"><b>Quick check: {q[0]}</b>' + ''.join(f'<button type="button">{q[1][i]}</button>' for i in order)
            + f'<div class="why">{q[3]}</div></div>')


def insert_after(html, heading, extra):
    """place extra after the first block that follows <h2>heading</h2>"""
    tag = f'<h2>{heading}</h2>'
    i = html.find(tag)
    if i < 0:
        raise SystemExit(f'heading not found: {heading}')
    j = i + len(tag)
    m = re.match(r'\s*<(p|ul|ol)>.*?</\1>', html[j:], re.S)
    k = j + (m.end() if m else 0)
    return html[:k] + extra + html[k:]



FIXES = {
 '<b>Rotation design:</b>': '<p><b>Rotation design</b> has six inputs:</p><ul><li><b>Load:</b> roughly two incidents per shift at most. Overload <i>and</i> underload both degrade response.</li><li><b>Coverage that matches users:</b> business hours is “on duty”, daylight across two sites gives about 21 hours, and follow-the-sun gives 24×7.</li><li><b>Response time:</b> three minutes or less needs two people; 30 minutes allows normal life.</li><li><b>System properties that buy slack</b>, such as graceful degradation.</li><li><b>Customer constraints</b>, like where responders must be located.</li><li><b>Labour law.</b></li></ul>',
 '<b>Lifecycle:</b>': '<p><b>The incident lifecycle</b> has six stages:</p><ol><li><b>Detect.</b></li><li><b>Triage.</b> How many users, global or local, which journeys? Declare early. Success means fast, accurate classification and escalation.</li><li><b>Investigate.</b> Root cause analysis is slow and political, and OODA is still linear, so Google prefers <b>multiple hypotheses</b> tested in parallel by trying to disprove them.</li><li><b>Mitigate.</b> Generic, safe mitigations come first: rollback, more capacity, restart, drain. A mitigation is also a diagnostic experiment, and whether you <i>can</i> mitigate is an architectural property.</li><li><b>Resolve.</b> Causes understood, or the change rolled back and blocked, followed by a “wait and see” period.</li><li><b>Learn.</b></li></ol>',
 'The theory to know:': '<p>The chapter also leans on safety science: Swiss cheese, Rasmussen, Safety-II, Cook, Woods and STAMP. Each gets a line in the section on safety-science models below.</p>',
 '<b>STPA</b> (forward-looking': '<p><b>STPA</b> looks forward, and you can run it on a design doc. It has four steps:</p><ol><li>Define losses and <b>hazards</b>: detectable states that lead to a loss in the worst case.</li><li>Model the <b>control structure</b>: controllers, control actions going down, feedback coming up, and each controller’s process or mental model.</li><li>List <b>unsafe control actions</b>: not taken when needed, taken when unsafe, taken too early, too late or in the wrong order, or stopped too soon or applied too long.</li><li>Build <b>causal scenarios</b> for each.</li></ol>',
 '<b>CAST</b> (backward-looking)': '<p><b>CAST</b> looks backward at an incident. It has five steps:</p><ol><li>Basic information: losses, hazards, timeline, questions.</li><li>The control structure <i>as it was</i>.</li><li>Each controller’s contribution, described neutrally (no “should have”), with its mental-model gaps and context.</li><li>Flaws in the control structure through systemic factors: safety culture, communication and coordination, management of change, safety information, and changes in the environment.</li><li>An improvement plan that traces back to those factors.</li></ol>',
}


def apply_fixes(html):
    for start, new in FIXES.items():
        m = re.search(r'<p>\s*' + re.escape(start) + r'.*?</p>', html, re.S)
        if m:
            html = html[:m.start()] + new + html[m.end():]
            USED.add(start)
    return html


USED = set()

ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI'}
lessons = []
for n in range(1, 24):
    e = X.L[n]
    part = X.PART_OF[n]
    ch = card('ch', n)
    say, ch = grab(r'<h4>Say it in an interview</h4>\s*<p>(.*?)</p>', ch)
    aws, ch = grab(r'<div class="aws">(.*?)</div>', ch)
    q1, ch = grab(r'<div class="q">(.*?)</div>', ch)
    ch = apply_fixes(ch.replace('<b>The core idea.</b> ', ''))
    body = ''
    if n == 8:
        body = X.CH8
    elif n == 9:
        body = X.CH9
    else:
        core = split_paras(ch.strip()).replace('<h4>', '<h2>').replace('</h4>', '</h2>')
        # the top diagram sits after the opening paragraphs, before any later section
        k = core.find('<h2>')
        head, tail = (core, '') if k < 0 else (core[:k], core[k:])
        m1 = re.match(r'\s*<p>.*?</p>', head, re.S)
        cut = m1.end() if m1 else 0
        body = '<h2>The big picture</h2>' + head[:cut] + e.get('top', '') + head[cut:] + tail
    body += X2.PICS.get(n, '')
    body += X3.SRE_ADD.get(n, '')
    body += X3.connections(f'ch-{n}', SY.MAP)
    dx = card('dx', n)
    q2 = None
    if n in X2.MORE:
        body += '<div class="deeper"><span>Going deeper</span> what a full re-read of the chapter adds</div>' + X2.MORE[n]
    if dx:
        q2, dx = grab(r'<div class="q">(.*?)</div>', dx)
        deep = split_paras(dx.strip()).replace('<h4>', '<h2>').replace('</h4>', '</h2>')
        if not deep.lstrip().startswith('<h2>'):
            deep = '<h2>More from the chapter</h2>' + deep
        body += '<div class="deeper"><span>Going deeper</span> the case studies, numbers and named models from the full chapter</div>' + deep
    for h, extra in e.get('after', {}).items():
        body = insert_after(body, h, extra)
    body = body.replace('<td>Auto</td>', '<td><span class="pl a">Auto</span></td>').replace('<td>Human</td>', '<td><span class="pl h">Human</span></td>')
    tail = ''
    if say:
        tail += f'<div class="say"><b>Say it in an interview</b><p>{say}</p></div>'
    if aws:
        aws = re.sub(r'^<b>On AWS:</b>\s*', '', aws)
        aws = aws[0].upper() + aws[1:]
        tail += f'<div class="note aws"><b>On AWS</b>{aws}</div>'
    iqs = ''.join(qa(q) for q in (q1, q2) if q)
    if n in X4.IQ:
        iqs = ''.join(f'<div class="iq"><p class="iqq">{q}</p><details><summary>Show a model answer</summary>' + ''.join(f'<p>{a}</p>' for a in ans) + '</details></div>' for q, ans in X4.IQ[n])
    if iqs:
        tail += '<h2>Interview practice</h2><p>Answer aloud for two minutes before you open the model answer.</p>' + iqs
    qs = quiz_ch.get(n, [])[:3 if n in X2.NEWQUIZ else 2]
    tail += ''.join(quick(q, n * 10 + i) for i, q in enumerate(qs))
    tail += f'<div class="ex"><b>Your turn</b>{e["turn"]}</div>'
    tail += '<div class="take"><b>Key takeaways</b><ul>' + ''.join(f'<li>{t}</li>' for t in e['take']) + '</ul></div>'
    words = len(strip(body + tail).split())
    mins = max(4, round(words / 190))
    meta = f'<span class="chip">Part {ROMAN[part]} · {X.PARTS[part][0]}</span>Chapter {n} · {mins} min read' + (f' · {e["poc"]}' if e['poc'] else '')
    learn = '<div class="learn"><b>You will learn</b><ul>' + ''.join(f'<li>{t}</li>' for t in e['learn']) + '</ul></div>'
    lessons.append(f'<section class="lesson" id="ch-{n}" data-part="{part}" data-ch="{n}" data-dot="{n}" data-title="{e["nav"]}">\n<div class="meta">{meta}</div>\n<h1>{e["h1"]}</h1>\n{learn}\n{body}\n{tail}\n</section>')


# ------------------------------------------------------------------ second track: Platform Engineering at Google
import pe, pe2, pe3, pe4
PE_PART = {'P1': 'Architecture and ecosystem design', 'P2': 'Execution and product approach'}
for d in pe.L:
    body = d['body']
    if d['id'] in X3.PE_NAMES:
        body += X3.names(X3.PE_NAMES[d['id']])
    if d['id'] in X3.PE_FINAL:
        body += X3.connections(d['id'], SY.MAP)
    for m in re.finditer(r'<p>(.*?)</p>', body, re.S):
        assert len(strip(m.group(1))) < 640, ('long paragraph', d['id'], strip(m.group(1))[:80])
    tail = ''
    if d.get('say'):
        tail += f'<div class="say"><b>Say it in an interview</b><p>{d["say"]}</p></div>'
    if d.get('aws'):
        tail += f'<div class="note aws"><b>On AWS</b>{d["aws"]}</div>'
    if d.get('iq'):
        tail += '<h2>Interview practice</h2><p>Answer aloud for two minutes before you open the model answer.</p>'
        tail += ''.join(f'<div class="iq"><p class="iqq">{q}</p><details><summary>Show a model answer</summary>' + ''.join(f'<p>{a}</p>' for a in ans) + '</details></div>' for q, ans in d['iq'])
    for i, q in enumerate(d.get('quiz', [])):
        tail += quick(q, 7000 + len(lessons) * 10 + i)
        QUIZ.append(q)
    if d.get('turn'):
        tail += f'<div class="ex"><b>Your turn</b>{d["turn"]}</div>'
    tail += '<div class="take"><b>Key takeaways</b><ul>' + ''.join(f'<li>{t}</li>' for t in d['take']) + '</ul></div>'
    mins = max(4, round(len(strip(body + tail).split()) / 190))
    if 'meta' in d:
        meta, chattr = d['meta'] + f' · {mins} min read', ''
    else:
        meta = (f'<span class="chip">Platform book · {PE_PART[d["part"]]}</span>Chapter {d["final"]} in the final book · {d["by"]} · {mins} min read'
                + (f' · {d["poc"]}' if d['poc'] else ''))
        chattr = f' data-ch="p{d["dot"]}"'
    learn = '<div class="learn"><b>You will learn</b><ul>' + ''.join(f'<li>{t}</li>' for t in d['learn']) + '</ul></div>'
    lessons.append(f'<section class="lesson" id="{d["id"]}" data-part="{d["part"]}"{chattr} data-dot="{d["dot"]}" data-title="{d["nav"]}">\n<div class="meta">{meta}</div>\n<h1>{d["h1"]}</h1>\n{learn}\n{body}\n{tail}\n</section>')
CARDS += pe4.CARDS
DRILLS += pe4.DRILLS
PE_AWS = X.table(['Concept', 'What to say', 'AWS services', 'POC'], pe4.AWS_ROWS)

# ------------------------------------------------------------------ tracks 3 and 4: Mastering Prometheus, Observability with Grafana
import obs1, obs2, obs3, obs4, obs5
import obs_pics
for d in obs1.L + obs4.L:
    body = d['body']
    for head, fig in obs_pics.P.get(d['id'], []):
        i = body.index(f'<h2>{head}</h2>')
        nxt = [k for k in (body.find('<h2>', i + 4), body.find('<div class="deeper">', i)) if k > 0]
        end = min(nxt) if nxt else len(body)
        j = body.find('</p>', i, end)
        j = j + 4 if j > 0 else end
        body = body[:j] + fig + body[j:]
    body += X3.connections(d['id'], SY.MAP)
    for m in re.finditer(r'<p>(.*?)</p>', body, re.S):
        assert len(strip(m.group(1))) < 640, ('long paragraph', d['id'], strip(m.group(1))[:80])
    tail = ''
    if d.get('say'):
        tail += f'<div class="say"><b>Say it in an interview</b><p>{d["say"]}</p></div>'
    if d.get('aws'):
        tail += f'<div class="note aws"><b>On AWS</b>{d["aws"]}</div>'
    if d.get('iq'):
        tail += '<h2>Interview practice</h2><p>Answer aloud for two minutes before you open the model answer.</p>'
        tail += ''.join(f'<div class="iq"><p class="iqq">{q}</p><details><summary>Show a model answer</summary>' + ''.join(f'<p>{a}</p>' for a in ans) + '</details></div>' for q, ans in d['iq'])
    for i, q in enumerate(d.get('quiz', [])):
        tail += quick(q, 9000 + len(lessons) * 10 + i)
        QUIZ.append(q)
    if d.get('turn'):
        tail += f'<div class="ex"><b>Your turn</b>{d["turn"]}</div>'
    tail += '<div class="take"><b>Key takeaways</b><ul>' + ''.join(f'<li>{t}</li>' for t in d['take']) + '</ul></div>'
    mins = max(4, round(len(strip(body + tail).split()) / 190))
    learn = '<div class="learn"><b>You will learn</b><ul>' + ''.join(f'<li>{t}</li>' for t in d['learn']) + '</ul></div>'
    lessons.append(f'<section class="lesson" id="{d["id"]}" data-part="{d["part"]}"' + ('' if d['id'] in ('m', 'g') else f' data-ch="{d["id"]}"') + f' data-dot="{d["dot"]}" data-title="{d["nav"]}">\n<div class="meta">{d["meta"]} · {mins} min read</div>\n<h1>{d["h1"]}</h1>\n{learn}\n{body}\n{tail}\n</section>')
CARDS += obs5.CARDS
DRILLS += obs5.DRILLS
OBS_AWS = X.table(['Concept', 'What to say', 'AWS services', 'Lesson, POC'], obs5.AWS_ROWS)

OLD_LABS = re.search(r'<div class="labs">(.*?)</div>\s*</div>\s*</section>', SRC, re.S).group(1)
labs = re.findall(r'<div class="lab">(.*?)</div>\s*(?=<div class="lab">|$)', OLD_LABS.strip() + '', re.S)

page = open(os.path.join(HERE, 'shell.html'), encoding='utf-8').read()
page = page.replace('</style>', X2.CSS + '</style>', 1)
page = page.replace('</style>', SY.CSS + '</style>', 1)
page = page.replace('<div class="pager">', '\n\n'.join(SY.lessons()) + '\n\n<div class="pager">', 1)
page = page.replace('</body>', '<script>' + SY.JS + '</script>\n</body>', 1)
page = page.replace('/*LESSONS*/', '\n\n'.join(lessons))
page = page.replace('/*LABS*/', OLD_LABS)
page = page.replace('/*AWS*/', AWS_TABLE).replace('/*AWS2*/', PE_AWS).replace('/*AWS3*/', OBS_AWS)
js = lambda rows: ',\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)
page = page.replace('/*CARDS*/', js(CARDS)).replace('/*QUIZ*/', js(QUIZ)).replace('/*DRILLS*/', js(DRILLS))
page = page.replace('{NCARDS}', str(len(CARDS))).replace('{NQUIZ}', str(len(QUIZ))).replace('{NDRILLS}', str(len(DRILLS)))
assert '/*' not in page.split('<body>')[1].split('<script>')[0], 'unfilled slot'
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(page)
assert USED == set(FIXES), set(FIXES) - USED
print(len(page), len(CARDS), len(QUIZ), len(DRILLS), len(lessons))
