# Track 3: Mastering Prometheus (Packt, 2024). Lessons for chapters 1-4. My own words throughout.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import h2, h3, note, deeper, code, ol

L = []
BOOK = 'Mastering Prometheus'


def meta(part, chs, poc):
    return (f'<span class="chip">Prometheus · {part}</span>{chs}' + (f' · {poc}' if poc else ''))


def box(x, y, w, h, title, sub='', cls='pn'):
    out = f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
    out += f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 6)}" text-anchor="middle" class="b" dominant-baseline="middle">{title}</text>'
    if sub:
        out += f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" text-anchor="middle" class="m" style="font-size:12px">{sub}</text>'
    return out


def arrow(x1, y1, x2, y2, label='', dx=0, dy=-6, dash=False):
    out = f'<line class="{"dash" if dash else "ln"}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#ah)"/>'
    if label:
        out += f'<text x="{(x1 + x2) / 2 + dx}" y="{(y1 + y2) / 2 + dy}" text-anchor="middle" class="m" style="font-size:12px">{label}</text>'
    return out


# ══════════════════════════════════════════════════════════════ intro
L.append(dict(
    id='m', dot='M', part='M1', nav='About this book', h1='Mastering Prometheus: the third book on the map',
    meta='<span class="chip">Mastering Prometheus</span>William Hegedus · Packt, April 2024 · 15 chapters',
    learn=['Why this book follows the SRE and platform books', 'How its two halves are organised', 'Which POCs go with which lessons, and what is AWS-specific'],
    body=(
        h2('Why Prometheus, and why now')
        + p('The SRE book told you to measure reliability from the user’s side, to page on how fast an error budget burns, and to make telemetry consistent across services. It did not tell you how to build the system that does the measuring. In most companies that system is Prometheus, or something that speaks its protocols: Amazon Managed Service for Prometheus, Grafana Mimir, Thanos or VictoriaMetrics.')
        + p('This book is written by an SRE manager who runs Prometheus at scale, and it reads like one. It skips the beginner material and goes straight to how the storage engine works, how service discovery and relabeling really behave, why alerts flap, where Prometheus stops scaling, and what the ecosystem offers past that point. That is exactly the depth interviewers probe when a role says “observability”.')
        + h2('How the lessons are organised')
        + table(['Lesson', 'Topic', 'Chapters', 'Code'],
                [['<a href="#m-1">1</a>', 'Observability, the architecture and deploying on Kubernetes', '1–2', 'POC 22'],
                 ['<a href="#m-3">2</a>', 'The data model and the TSDB on disk', '3', 'POC 21'],
                 ['<a href="#m-3q">3</a>', 'PromQL: selectors, operators, functions', '3', 'POC 20'],
                 ['<a href="#m-4">4</a>', 'Service discovery and relabeling', '4', 'POC 22'],
                 ['<a href="#m-5">5</a>', 'Alertmanager and alerts that don’t flap', '5', 'POC 23'],
                 ['<a href="#m-6">6</a>', 'Sharding, federation and high availability', '6', 'POC 22, 25'],
                 ['<a href="#m-7">7</a>', 'Cardinality, recording rules, jitter, profiling, GC', '7', 'POC 21'],
                 ['<a href="#m-8">8</a>', 'Node Exporter and writing exporters', '8', 'POC 21'],
                 ['<a href="#m-9">9</a>', 'Remote write, VictoriaMetrics and Mimir', '9', 'POC 25'],
                 ['<a href="#m-10">10</a>', 'Thanos, component by component', '10', 'POC 25'],
                 ['<a href="#m-11">11</a>', 'Jsonnet and monitoring mixins', '11', 'POC 29'],
                 ['<a href="#m-12">12</a>', 'CI for Prometheus: promtool, amtool, Pint', '12', 'POC 23'],
                 ['<a href="#m-13">13</a>', 'SLOs and burn-rate alerts, Sloth and Pyrra', '13', 'POC 24'],
                 ['<a href="#m-14">14</a>', 'OpenTelemetry, logs, traces and exemplars', '14–15', 'POC 27, 28']])
        + tiles([('Part 1 · Fundamentals', 'Lessons 1 to 5: how Prometheus stores, finds, queries and alerts on data. Everything later rests on these.', 'ember'),
                 ('Part 2 · Scaling and extending', 'Lessons 6 to 14: what to do when one server isn’t enough, how to keep it healthy, and how it fits with the rest of observability.', 'rust'),
                 ('On AWS', 'Every lesson maps the idea to Amazon Managed Service for Prometheus, Amazon Managed Grafana, ADOT, CloudWatch or EKS. The POCs carry Terraform for AMP and AMG.')])
        + note('How I read it', 'All fifteen chapters in full, and all thirty-nine figures. Where the book is wrong or out of date, the lesson says so: there are a handful of places, and they make good interview material because they show you understand the mechanism rather than the text.')
        + h2('Words this book uses constantly')
        + table(['Term', 'Meaning'],
                [['Sample', 'One value at one timestamp: a float64 and a millisecond time'],
                 ['Series', 'A metric name plus one unique set of labels, and all its samples'],
                 ['Cardinality', 'How many series exist. The single most important number for Prometheus cost and speed'],
                 ['Target', 'Something Prometheus scrapes, found by service discovery'],
                 ['Head block', 'The last couple of hours of data, in memory and protected by a write-ahead log'],
                 ['Relabeling', 'Rules that rewrite labels on targets (before a scrape) or series (after it)'],
                 ['External labels', 'Labels a Prometheus server adds to everything it sends out, used to tell servers and replicas apart']])),
    take=['This book is about running Prometheus, not just using it.', 'Part 1 is storage, discovery, queries and alerting; part 2 is scale, health and the wider ecosystem.', 'Every lesson maps to AWS managed services and to a runnable POC.']))

# ══════════════════════════════════════════════════════════════ 1 Observability + deploying
_arch = (
    box(20, 30, 150, 54, 'Service discovery', 'Kubernetes, EC2, HTTP SD')
    + box(20, 140, 150, 54, 'Targets', '/metrics endpoints')
    + box(250, 140, 150, 54, 'Scrape manager', 'relabel, pull, parse')
    + box(250, 30, 150, 54, 'Rule manager', 'recording + alerting')
    + box(480, 120, 170, 94, 'TSDB', '')
    + '<text x="565" y="160" text-anchor="middle" class="m" style="font-size:12px">head block + WAL</text><text x="565" y="178" text-anchor="middle" class="m" style="font-size:12px">2-hour blocks on disk</text><text x="565" y="196" text-anchor="middle" class="m" style="font-size:12px">compaction, retention</text>'
    + box(480, 20, 170, 54, 'Alertmanager', 'route, group, notify')
    + box(250, 250, 150, 54, 'HTTP API and UI', 'PromQL queries')
    + box(480, 250, 170, 54, 'Remote storage', 'AMP, Mimir, Thanos…')
    + box(20, 250, 150, 54, 'Grafana', 'dashboards')
    + arrow(95, 84, 95, 138, 'targets', dx=28)
    + arrow(170, 167, 248, 167, 'pull', dy=-8)
    + arrow(400, 167, 478, 167, 'append', dy=-8)
    + arrow(480, 140, 400, 70, 'query', dx=-10)
    + arrow(400, 50, 478, 47, 'alerts', dy=-8)
    + arrow(565, 214, 565, 248, 'remote write', dx=46)
    + arrow(480, 200, 400, 262, 'read', dx=-14)
    + arrow(248, 277, 172, 277, 'PromQL', dy=-8))
L.append(dict(
    id='m-1', dot='1', part='M1', nav='Architecture and deployment', h1='Observability, the Prometheus architecture, and deploying it',
    meta=meta('Fundamentals', 'Chapters 1–2', 'POC 22'),
    learn=['Monitoring versus observability, and where metrics fit among the signals', 'What makes Prometheus different: pull, labels, PromQL, service discovery', 'The components inside one Prometheus server and how data moves between them', 'How kube-prometheus-stack and the Prometheus Operator deploy it on Kubernetes'],
    body=(
        h2('The big picture')
        + p('Monitoring means checking for conditions you decided in advance were bad. Observability means being able to ask a new question of a running system and get an answer without shipping new code. Metrics, logs and traces are the three classic signals; metrics are the cheapest to keep and the fastest to query, which is why they drive dashboards and alerts.')
        + p('Prometheus is a metrics system with four ideas that set it apart. It <b>pulls</b> metrics over HTTP rather than waiting for them to be pushed. Every series is identified by <b>labels</b>, so you slice data by any dimension at query time. It has its own query language, <b>PromQL</b>. And it <b>discovers</b> what to scrape from Kubernetes, clouds and other sources, so targets come and go without config changes.')
        + h2('Why pull?')
        + table(['Pull gives you', 'What it costs'],
                [['An <code>up</code> series for every target: you know when collection fails, not just when data stops', 'Prometheus must be able to reach every target over the network'],
                 ['Targets need no knowledge of where metrics go; any number of servers can scrape them', 'Short-lived jobs may finish before a scrape; they need the Pushgateway or the textfile collector'],
                 ['A target can be inspected by hand: open <code>/metrics</code> in a browser', 'Scrape interval sets the resolution; nothing between scrapes is seen']])
        + h2('Inside one server')
        + pic(670, 320, _arch, 'My layout of the book’s architecture figure. Discovery feeds the scrape manager, samples go into the TSDB, the rule manager queries it on a schedule and sends alerts to Alertmanager, and the same storage answers PromQL from Grafana and, optionally, streams samples to remote storage.',
              'Prometheus architecture: service discovery, scrape manager, TSDB, rule manager, Alertmanager, HTTP API, Grafana and remote storage, with arrows for the data flow.')
        + p('Two things in that picture matter later. First, <b>Alertmanager is a separate program</b>: Prometheus decides that an alert is firing, Alertmanager decides who hears about it. Second, everything leaves through the same storage, so a slow query and a heavy rule both compete with ingestion for memory and CPU.')
        + h2('Deploying it on Kubernetes')
        + p('The book deploys everything with the <b>kube-prometheus-stack</b> Helm chart, which installs the Prometheus Operator, a Prometheus server, Alertmanager, Grafana, node exporter, kube-state-metrics and a large set of ready-made rules and dashboards (the kubernetes-mixin, which lesson 11 explains).')
        + table(['Operator resource', 'What it becomes'],
                [['<code>Prometheus</code>', 'A StatefulSet of Prometheus servers with replicas, shards, retention, external labels, remote write'],
                 ['<code>ServiceMonitor</code> / <code>PodMonitor</code>', 'Scrape jobs with <code>kubernetes_sd_configs</code> and the relabeling to select services or pods by label'],
                 ['<code>Probe</code>', 'Blackbox-exporter checks of URLs or ingresses'],
                 ['<code>PrometheusRule</code>', 'Recording and alerting rule files, loaded automatically'],
                 ['<code>Alertmanager</code> / <code>AlertmanagerConfig</code>', 'An Alertmanager cluster and per-namespace routing fragments'],
                 ['<code>ScrapeConfig</code>', 'Raw scrape configs for non-Kubernetes discovery, such as EC2 or HTTP SD']])
        + p('The point of the Operator is that teams describe <i>what</i> to monitor in their own namespaces, as Kubernetes objects, and the Operator turns that into a valid Prometheus configuration and reloads it. Nobody edits a shared prometheus.yml by hand.')
        + deeper('what the chapters add on the details')
        + h2('Small things worth knowing')
        + ul(['The book’s cluster is Linode Kubernetes Engine; nothing in it depends on Linode. On AWS the same chart runs on EKS.',
              'Prometheus is a single Go binary; a server is not clustered. High availability means running copies (lesson 6).',
              'Grafana is installed by the chart and pre-loaded with dashboards for the cluster, nodes and Prometheus itself.',
              'The UI under <i>Status</i> has the pages you will use most when something is wrong: Targets, Service Discovery, TSDB Status, Configuration and Rules.'])),
    say='Prometheus pulls metrics over HTTP from targets it discovers, stores each series by name and labels in a local time-series database, evaluates recording and alerting rules on a schedule, and hands firing alerts to a separate Alertmanager. On Kubernetes I deploy it with the Prometheus Operator so teams declare ServiceMonitors and PrometheusRules in their own namespaces instead of editing a central config.',
    aws='On EKS you have three options. Self-managed: kube-prometheus-stack on EKS with gp3 volumes for the TSDB. Hybrid: keep Prometheus (or Prometheus in agent mode, or the ADOT collector) as the scraper and remote-write to Amazon Managed Service for Prometheus, which stores, replicates and serves PromQL. Fully managed: the AMP managed collector scrapes the cluster agentlessly from a Prometheus-format scrape config. Amazon Managed Grafana reads AMP with SigV4. For alerting, AMP has rule groups namespaces and a managed Alertmanager whose receivers are SNS topics.',
    iq=[('Walk me through what happens between an application incrementing a counter and an engineer getting paged.',
         ['The application exposes the counter on an HTTP <code>/metrics</code> endpoint in the Prometheus text format, usually through a client library. On Kubernetes, a ServiceMonitor tells the Prometheus Operator which services to scrape, and the Operator writes the matching scrape job.',
          'Prometheus discovers the pod through the Kubernetes API, runs relabeling to decide whether to keep it and what labels it gets, then scrapes it every scrape interval. Each sample is appended to the head block in memory and to the write-ahead log on disk.',
          'On every evaluation interval the rule manager runs the alerting rule’s PromQL. If the expression returns series, each becomes a pending alert; if it stays true for the rule’s <code>for</code> duration, it becomes firing and Prometheus sends it to every configured Alertmanager, and keeps re-sending while it fires.',
          'Alertmanager matches the alert’s labels against its routing tree, groups it with similar alerts, waits <code>group_wait</code> to collect more, checks inhibitions and silences, and then notifies the receiver: PagerDuty, Slack, or on AWS an SNS topic that pages through Incident Manager.',
          'The useful thing to add in an interview is where it can break: no <code>up</code> means the scrape failed, a missing sample can reset a pending alert, and the alert only reaches someone if every Prometheus can reach every Alertmanager.'])],
    quiz=[['Which component decides who gets notified about a firing alert?', ['The Prometheus rule manager', 'Alertmanager', 'The Prometheus Operator', 'Grafana'], 1, 'Prometheus evaluates rules and sends firing alerts; Alertmanager routes, groups, inhibits and notifies.'],
          ['What does the pull model give you that push does not?', ['Lower network use', 'An up series that tells you when collection itself fails', 'No need for service discovery', 'Unlimited resolution'], 1, 'Because Prometheus initiates every scrape, it knows when a target didn’t answer and records up = 0.']],
    turn='Install kube-prometheus-stack on a local kind or k3d cluster (or EKS). Open <i>Status → Targets</i> and <i>Status → Service Discovery</i>, pick one ServiceMonitor and find the scrape job the Operator generated for it in <i>Status → Configuration</i>. Then read POC 22’s <code>prometheus-ec2.yml</code> to see the same ideas outside Kubernetes.',
    take=['Pull, labels, PromQL and service discovery are what make Prometheus different.', 'Prometheus decides alerts fire; Alertmanager decides who hears.', 'On Kubernetes, the Operator turns ServiceMonitors and PrometheusRules into config; on AWS, AMP can take over storage and rules.']))

# ══════════════════════════════════════════════════════════════ 2 TSDB
_tsdb = (
    '<rect class="pn" x="20" y="40" width="210" height="200" rx="10"/><text x="125" y="64" text-anchor="middle" class="b">Head block</text>'
    '<text x="125" y="84" text-anchor="middle" class="m" style="font-size:12px">last ~2–3 hours, in memory</text>'
    + box(40, 100, 170, 40, 'active chunks', '', 'pn') + box(40, 150, 170, 40, 'mmapped full chunks', '', 'pn')
    + '<text x="125" y="222" text-anchor="middle" class="m" style="font-size:12px">every sample also → WAL</text>'
    + box(20, 270, 210, 44, 'WAL + checkpoints', '128 MB segments')
    + arrow(125, 240, 125, 268)
    + arrow(232, 140, 300, 140, 'cut every 2h', dy=-8)
    + '<rect class="pn" x="302" y="40" width="190" height="200" rx="10"/><text x="397" y="64" text-anchor="middle" class="b">Block (2h)</text>'
    + ''.join(f'<text x="322" y="{y}" class="m" style="font-size:13px">{t}</text>' for y, t in [(94, 'chunks/000001…'), (122, 'index'), (150, 'meta.json'), (178, 'tombstones')])
    + '<text x="322" y="214" class="m" style="font-size:12px">immutable, self-contained</text>'
    + arrow(494, 140, 560, 140, 'compact ×3', dy=-8)
    + '<rect class="pn" x="562" y="70" width="170" height="44" rx="8"/><text x="647" y="97" text-anchor="middle" class="b">6h block</text>'
    + '<rect class="pn" x="562" y="124" width="170" height="44" rx="8"/><text x="647" y="151" text-anchor="middle" class="b">18h, 54h …</text>'
    + '<text x="647" y="196" text-anchor="middle" class="m" style="font-size:12px">max 31 days or 10% of retention</text>'
    + '<text x="647" y="226" text-anchor="middle" class="m" style="font-size:12px">deleted after retention</text>')
L.append(dict(
    id='m-3', dot='2', part='M1', nav='Data model and TSDB', h1='The data model and the TSDB: how samples are stored and found',
    meta=meta('Fundamentals', 'Chapter 3, first half', 'POC 21'),
    learn=['Metric, series, sample, and why labels decide cost', 'The four metric types and what each is for', 'The head block, the write-ahead log, checkpoints and memory-mapped chunks', 'Blocks, the index and postings, compaction and retention', 'Why delta-of-delta and XOR compression make samples cost about a byte'],
    body=(
        h2('The big picture')
        + p('A <b>sample</b> is a float64 value and a millisecond timestamp. A <b>series</b> is all the samples that share one metric name and one exact set of label values. A <b>metric</b> is the family of series with the same name. Change any label value and you have a new series, with its own memory, index entries and chunks.')
        + code('http_requests_total{job="checkout", method="POST", code="500"}  1027  @1714052400000\n└── metric name ──┘ └──────────── labels ───────────────┘ value  timestamp (ms)')
        + p('Under the hood the metric name is just another label, <code>__name__</code>. So <code>http_requests_total{code="500"}</code> and <code>{__name__="http_requests_total", code="500"}</code> are the same selector.')
        + h2('Metric types')
        + table(['Type', 'Behaviour', 'Typical query'],
                [['Counter', 'Only goes up; resets to zero when the process restarts', '<code>rate()</code>, <code>increase()</code>'],
                 ['Gauge', 'Goes up and down: temperature, queue depth, memory', 'the value itself, <code>delta()</code>, <code>*_over_time()</code>'],
                 ['Histogram', 'Counts observations into cumulative buckets: <code>_bucket{le=…}</code>, <code>_sum</code>, <code>_count</code>', '<code>histogram_quantile()</code> over <code>rate()</code> of buckets'],
                 ['Summary', 'Quantiles computed in the client, plus <code>_sum</code> and <code>_count</code>', 'read the quantile; you can’t aggregate it across instances']])
        + note('Why histograms usually win', 'A summary’s p99 from ten pods can’t be combined into a service p99: averaging percentiles is wrong. Histogram buckets are counters, so you sum them across pods first and compute the quantile once. The price is that the answer is interpolated inside a bucket, so bucket boundaries should sit near your SLO thresholds.')
        + h2('Where samples live')
        + pic(750, 330, _tsdb, 'My drawing of the storage layout described across chapter 3. New samples go into the head block in memory and the write-ahead log on disk; every two hours the oldest part of the head becomes an immutable block; the compactor merges blocks in steps of three.',
              'Head block with active and memory-mapped chunks, backed by a WAL; a cut every two hours produces a 2-hour block with chunks, index, meta.json and tombstones; compaction merges blocks into larger ones.')
        + h3('The head block and the WAL')
        + p('Incoming samples are appended to an in-memory chunk per series. When a chunk fills (120 samples) it is written to disk and memory-mapped, so memory holds only the active chunk per series. To survive a crash, every sample is also written to the <b>write-ahead log</b>: 128 MB segment files that are replayed on startup. Periodically a <b>checkpoint</b> condenses old WAL segments so replay doesn’t have to read all of them.')
        + p('That replay is why a Prometheus with millions of series can take many minutes to start, and why the book lists slow startup as one of the first signs of trouble.')
        + h3('Blocks')
        + p('Every two hours the oldest two hours of the head are written out as a <b>block</b>: a directory named by a ULID containing <code>chunks/</code>, an <code>index</code>, <code>meta.json</code> and <code>tombstones</code>. Each block is a complete, immutable database for its time range. Deleting data writes a tombstone; the data disappears at the next compaction.')
        + p('The <b>compactor</b> merges three adjacent blocks into one three times as long (2h, 6h, 18h, 54h…), up to 31 days or a tenth of the retention period. Fewer, larger blocks mean a smaller combined index and fewer files to open. <b>Retention</b> deletes whole blocks once they fall outside the retention time or size.')
        + h3('The index')
        + p('The index is an inverted index. A <b>symbol table</b> stores every string once. For each <code>label=value</code> pair there is a <b>postings list</b>: the sorted IDs of every series that has it. A selector such as <code>{job="api", code=~"5.."}</code> fetches the postings for each matcher and intersects them, starting from the shortest list, then reads only the chunks of the surviving series.')
        + p('That is why cardinality hurts. A label with a hundred thousand values adds a hundred thousand postings lists, symbols and series, and any query that touches it has to merge enormous lists.')
        + deeper('compression, and why scrape timing matters')
        + h2('Gorilla compression')
        + p('Prometheus uses the encoding from Facebook’s Gorilla paper. Timestamps are stored as the <b>difference between consecutive differences</b>. If scrapes are exactly fifteen seconds apart, that delta-of-delta is zero and costs one bit. Values are XOR’d with the previous value; a value that didn’t change costs one bit, and a slowly growing counter costs a few bits more.')
        + p('Together a sample averages one to two bytes instead of sixteen. POC 21 reproduces the arithmetic: a counter scraped on time costs about a byte per sample, and the same counter with ±30 ms of scrape jitter costs more than twice that. Lesson 7 shows how to find and fix jitter.')
        + table(['Delta-of-delta', 'Bits spent'], [['0 (perfectly regular)', '1'], ['fits in 14 bits', '16'], ['fits in 17 bits', '20'], ['fits in 20 bits', '24'], ['anything else', '68']])
        + h2('Further reading the book recommends')
        + p('Ganesh Vernekar’s blog series on the TSDB (head block, WAL, mmapping, compaction) and Fabian Reinartz’s original design write-up are the canonical deep dives if an interviewer goes further.')),
    say='A series is a metric name plus a unique label set; every new label value is a new series with its own memory, index entries and chunks, which is why cardinality is the cost driver. Samples land in an in-memory head block backed by a write-ahead log, get cut into immutable two-hour blocks, and the compactor merges those up to 31 days. Queries use an inverted index of postings lists, intersecting the lists for each label matcher.',
    aws='AMP runs a Cortex-based storage engine that keeps the same data model in S3-backed blocks, so cardinality is still what you pay for: AMP bills per sample ingested and per GB stored, and has per-workspace quotas on active series. If you self-manage on EKS, give each Prometheus replica its own gp3 EBS volume in its own AZ, size memory for head-block series, and expect WAL replay after a restart to scale with series count.',
    iq=[('Why does adding a user_id label to a request counter cause problems, and what would you do instead?',
         ['Every distinct label value creates a new series. A counter with a user ID label goes from a handful of series per pod to one per active user, potentially millions. Each series costs memory in the head block, entries in the index, its own chunks on disk and WAL records, and any query over that metric has to merge postings across all of them.',
          'The symptoms show up together: memory climbs, WAL replay after a restart gets slow, queries on that metric time out, and on a managed service the bill jumps because you pay per sample and per active series.',
          'The fix is to keep metrics low-cardinality and push the per-user detail into the signals designed for it. The request counter keeps labels like method, route template and status class. Per-user information goes in logs or as span attributes in traces, which can hold high-cardinality fields cheaply, and exemplars can link a metric data point to a specific trace.',
          'If the label is already being scraped, drop it at the edge with <code>metric_relabel_configs</code> or <code>labeldrop</code>, check that the series stay unique, and add <code>sample_limit</code> on the scrape job so the next mistake fails one scrape instead of the server.'])],
    quiz=[['How often does Prometheus cut a new block from the head by default?', ['Every 15 seconds', 'Every 2 hours', 'Every 24 hours', 'Only on shutdown'], 1, 'Blocks cover two hours; the compactor then merges them in steps of three.'],
          ['Why can’t you average summaries from ten pods to get a service-wide p99?', ['Summaries don’t have a _count', 'Averaging percentiles is mathematically wrong; histograms can be summed first', 'Summaries are gauges', 'PromQL has no avg function'], 1, 'Histogram buckets are counters you can sum across pods; the quantile is computed once on the total.']],
    turn='Run POC 21. Change the jitter in <code>test_jitter_costs_disk_and_tolerance_wins_it_back</code> from ±30 ms to ±2 ms and watch the bytes per sample fall. Then feed <code>cardinality_report()</code> the <code>/metrics</code> output of any exporter you have and find the label with the most values.',
    take=['Every unique label set is a series, and series are what cost memory, disk and query time.', 'Head block plus WAL for recent data; immutable two-hour blocks compacted up to 31 days.', 'Regular scrapes and steady values compress to about a byte per sample.']))

# ══════════════════════════════════════════════════════════════ 3 PromQL
_rate = (
    '<line class="ln" x1="40" y1="250" x2="720" y2="250"/><text x="720" y="272" text-anchor="end" class="m">time</text>'
    '<line class="dash" x1="120" y1="40" x2="120" y2="250"/><line class="dash" x1="620" y1="40" x2="620" y2="250"/>'
    '<text x="120" y="32" text-anchor="middle" class="m" style="font-size:12px">t − 5m</text><text x="620" y="32" text-anchor="middle" class="m" style="font-size:12px">t</text>'
    + ''.join(f'<circle cx="{x}" cy="{y}" r="6" class="fc"/>' for x, y in [(150, 220), (230, 200), (310, 180), (390, 160), (470, 230), (550, 210)])
    + '<text x="430" y="252" class="m" style="font-size:12px" text-anchor="middle">reset</text>'
    + '<path class="hl" d="M150 220L230 200L310 180L390 160"/><path class="hl" d="M470 230L550 210"/>'
    + '<path class="dash" d="M120 228L150 220"/><path class="dash" d="M550 210L620 192"/>'
    + '<text x="135" y="270" text-anchor="middle" class="m" style="font-size:12px">extrapolate</text><text x="585" y="270" text-anchor="middle" class="m" style="font-size:12px">extrapolate</text>'
    + '<text x="520" y="120" class="b">irate: last two points only</text><path class="ln" d="M520 130L540 200" marker-end="url(#ah)"/>'
    + '<text x="160" y="100" class="b">rate: whole window, reset-aware</text>')
L.append(dict(
    id='m-3q', dot='3', part='M1', nav='PromQL', h1='PromQL: selecting, combining and computing',
    meta=meta('Fundamentals', 'Chapter 3, second half', 'POC 20'),
    learn=['Instant vectors, range vectors, instant and range queries, staleness', 'Aggregation with by and without, and when to prefer without', 'Vector matching: on, ignoring, group_left, group_right, and info-metric joins', 'and, or, unless, and why unless is the alerting favourite', 'rate, irate, increase, changes and delta, including how rate extrapolates'],
    body=(
        h2('The big picture')
        + p('PromQL works on vectors of series, not on rows. A <b>selector</b> picks series by name and labels. An <b>instant vector</b> holds one sample per series at one moment. A <b>range vector</b> holds every sample in a window, like <code>[5m]</code>, and only functions accept it. An <b>instant query</b> evaluates once; a <b>range query</b> (what Grafana graphs use) evaluates the same expression at every step across a time range.')
        + h3('Staleness and the five-minute lookback')
        + p('At any evaluation time an instant selector returns the newest sample of each series that is at most five minutes old. When a target disappears, Prometheus writes a <b>staleness marker</b> so its series end immediately rather than lingering for five minutes. That lookback is also why a missing scrape doesn’t make a graph gap, and why an alert can reset when the series vanishes for longer.')
        + table(['Selector', 'Means'],
                [['<code>up{job="api"}</code>', 'Exact label match'], ['<code>http_requests_total{code=~"5.."}</code>', 'Regex, always anchored: matches 500 to 599, never 1500'],
                 ['<code>{__name__=~"node_.*", instance!=""}</code>', 'The name is a label too; every selector needs one matcher that doesn’t match empty'],
                 ['<code>rate(x[5m] offset 1w)</code>', 'Same window one week earlier'], ['<code>max_over_time(rate(x[1m])[1h:1m])</code>', 'Subquery: evaluate the inner expression every minute for an hour']])
        + h2('Aggregation: by versus without')
        + p('<code>sum by (namespace) (…)</code> keeps only the listed labels. <code>sum without (pod, instance) (…)</code> drops the listed ones and keeps everything else. The book prefers <b>without</b>, because it preserves labels you didn’t think about, such as <code>cluster</code> or <code>job</code>, which later joins and alert routing often need.')
        + code('count(kube_pod_info) by (namespace)                         # pods per namespace\ncount(kube_pod_container_status_running) without (uid, pod, container)')
        + h2('Vector matching')
        + p('Arithmetic between two vectors pairs up elements with <b>identical label sets</b> (ignoring the name). Anything without a partner is dropped silently, which is the most common reason a ratio returns nothing.')
        + table(['Modifier', 'Use'],
                [['<code>on (node)</code>', 'Match only on the listed labels'], ['<code>ignoring (code)</code>', 'Match on everything except the listed labels'],
                 ['<code>group_left (os_image)</code>', 'Many on the left may match one on the right; copy <code>os_image</code> from the right'],
                 ['<code>group_right</code>', 'The mirror image: many on the right']])
        + code('# copy node metadata onto every pod, using an info metric whose value is always 1\nkube_pod_info * on (node) group_left (kubelet_version, os_image) kube_node_info\n\n# one-to-one on node: memory used by containers over node capacity\nsum by (node) (container_memory_rss) / on (node) machine_memory_bytes')
        + p('An <b>info metric</b> has the value 1 and carries descriptive labels. Multiplying by it adds labels without changing values. The pattern keeps volatile metadata off every other series.')
        + h3('Set operators')
        + table(['Operator', 'Keeps'],
                [['<code>a and b</code>', 'Elements of a that have a match in b'], ['<code>a or b</code>', 'All of a, plus elements of b with no match in a'], ['<code>a unless b</code>', 'Elements of a that have no match in b']])
        + p('<code>unless</code> is how you write “fire, except when…”. The NTP alert from chapter 5 ignores servers that rebooted in the last half hour: <code>node_timex_offset_seconds > 0.05 unless on (instance) changes(node_boot_time_seconds[30m]) > 0</code>. kube-prometheus’s InfoInhibitor uses it to show info alerts only when nothing worse is firing in the namespace.')
        + h2('Functions on counters and gauges')
        + pic(760, 290, _rate, 'My drawing of rate against irate. rate uses every sample in the window, adds back the value lost at a counter reset, and extrapolates to the window edges. irate uses only the last two samples.',
              'Counter samples in a five-minute window with a reset; rate is drawn across all of them with extrapolated ends, irate as the last segment only.')
        + table(['Function', 'Does', 'Use for'],
                [['<code>rate(c[5m])</code>', 'Per-second average increase over the whole window, reset-aware, extrapolated to the edges', 'Alerts, dashboards, recording rules'],
                 ['<code>irate(c[5m])</code>', 'Per-second rate from the last two samples only', 'Fast-moving graphs; never alerts'],
                 ['<code>increase(c[1h])</code>', '<code>rate × range</code>; can be fractional because of extrapolation', '“how many in the last hour”'],
                 ['<code>changes(g[24h])</code>', 'How many times the value changed', 'Restarts, via <code>kube_pod_start_time</code>'],
                 ['<code>delta(g[24h])</code>', 'Last minus first for gauges; can be negative', '<code>delta(count(up)[24h:])</code> spots targets that quietly vanished']])
        + note('Two rules that prevent most mistakes', '<b>rate, then sum</b>: <code>sum(rate(x[5m]))</code>, never <code>rate(sum(x)[5m:])</code>, because summing counters first hides each one’s reset. And make the window at least four scrape intervals long, so it always holds two samples; in Grafana, <code>$__rate_interval</code> does that for you.')
        + deeper('how rate really extrapolates')
        + h2('Extrapolation, exactly')
        + p('Samples rarely fall on the window edges. <code>rate()</code> takes last minus first (plus any reset corrections) and stretches it to cover the whole window, but only by up to half an average scrape interval at each end when the gap is large, and never back past the point where a counter would have been zero. POC 20 ports the algorithm: a counter growing by 10 per 10 seconds with samples at 5…55 s in a 60 s window gives an increase of exactly 60, and one that starts at zero inside the window gives 55.')
        + p('The book also counts about seventy functions and says a handful cover nine queries in ten. The ones above, plus <code>histogram_quantile</code>, <code>label_replace</code>, <code>absent</code>, <code>predict_linear</code> and the <code>*_over_time</code> family, are that handful.')),
    say='A selector returns an instant vector of the newest sample per series within five minutes; a range selector returns every sample in a window, and functions like rate turn that back into an instant vector. Binary operators match on all labels unless I narrow them with on or ignoring, group_left copies labels from an info metric, and unless is how I suppress an alert in a known condition. For counters I always rate first and aggregate second.',
    aws='AMP and Amazon Managed Grafana speak standard PromQL, so everything here works unchanged: point the Grafana Prometheus data source at the AMP query endpoint with SigV4 enabled. CloudWatch has its own metric math and Metrics Insights for AWS service metrics; for application metrics PromQL is the more portable skill. AMP query limits (samples per query, query time) play the role of Prometheus’ <code>--query.max-samples</code>.',
    iq=[('A teammate writes sum(http_requests_total) / sum(http_requests_total offset 5m) to show request growth and the graph has strange negative spikes. What’s wrong and how do you fix it?',
         ['The expression compares raw counter values. Counters reset to zero when a process restarts, so when any pod restarts the current sum drops, and comparing totals across a restart produces nonsense, including apparent negative growth.',
          'Raw counter values are almost never what you want. The question “how fast are requests arriving” is answered by <code>sum(rate(http_requests_total[5m]))</code>: rate per series first, which handles each reset correctly, then sum.',
          'If the question really is growth compared with earlier, compare two rates: <code>sum(rate(http_requests_total[5m])) / sum(rate(http_requests_total[5m] offset 1w))</code> for week-on-week. In Grafana use <code>$__rate_interval</code> rather than a fixed window so the window always contains at least two scrapes at any zoom level.',
          'I’d also check the labels: if one side of a division has a label the other lacks, the match fails and returns nothing. Aggregating both sides the same way, or using <code>on()</code>, avoids that.'])],
    quiz=[['What does group_left (os_image) do in kube_pod_info * on (node) group_left (os_image) kube_node_info?', ['Drops os_image', 'Lets many pods match one node and copies os_image from the node series', 'Groups the result by os_image', 'Sorts the result'], 1, 'Many-to-one matching on node, with the listed label copied from the one side.'],
          ['Which function should an alert on request rate use?', ['irate', 'rate', 'delta', 'changes'], 1, 'irate uses only the last two samples, so it is too jumpy for alerting.']],
    turn='Run POC 20 and read <code>test_on_and_ignoring_narrow_the_match</code> and <code>test_many_to_one_needs_group_left</code>: they are the Grafana book’s colour/smell vectors. Then write, in your own Prometheus, a query that copies <code>os_image</code> from <code>kube_node_info</code> onto container memory, and one that alerts on clock offset <code>unless</code> the node just rebooted.',
    take=['Instant vectors for values, range vectors for functions, five-minute lookback with staleness markers.', 'Matching is on all labels by default; on, ignoring and group_left are how you join.', 'Rate first, aggregate second; irate for graphs, rate for alerts.']))

# ══════════════════════════════════════════════════════════════ 4 Service discovery and relabeling
_relabel = flow([('Discovery', 'targets + hidden __meta_* labels', 'ember'), ('relabel_configs', 'keep or drop targets, build labels', 'ember'), ('Scrape', 'pull /metrics', 'ember'),
                 ('metric_relabel_configs', 'drop or fix series', 'rust'), ('TSDB', 'store', 'rust'), ('write_relabel_configs', 'choose what to remote-write', 'rust')],
                'Three relabeling hooks at three points in the pipeline. The first works on targets, the other two on series.')
L.append(dict(
    id='m-4', dot='4', part='M1', nav='Service discovery and relabeling', h1='Service discovery and relabeling: deciding what to scrape and what to call it',
    meta=meta('Fundamentals', 'Chapter 4', 'POC 22'),
    learn=['How discovery providers hand targets and metadata to Prometheus', 'How ServiceMonitors become kubernetes_sd_configs and relabel rules', 'Relabel actions, the three places relabeling runs, and how to debug it', 'How a provider works inside (the Linode example) and why HTTP SD replaced file_sd scripts'],
    body=(
        h2('The big picture')
        + p('In a cloud environment targets change by the minute, so a fixed list of hosts goes stale immediately. Prometheus ships more than two dozen <b>service discovery</b> providers, among them Kubernetes, AWS EC2 and Lightsail, Azure, GCP, Consul, Docker, file-based and HTTP. Each refreshes in the background and returns a list of candidate targets with an address and a set of hidden <code>__meta_&lt;provider&gt;_*</code> labels.')
        + p('Discovery deliberately does almost nothing else. Deciding which candidates to keep and what labels they get is the job of <b>relabeling</b>. In the book’s words, relabeling is where the magic happens.')
        + _relabel
        + h2('From ServiceMonitor to scrape job')
        + p('With the Prometheus Operator you rarely write <code>kubernetes_sd_configs</code> yourself. A ServiceMonitor says “scrape services with these labels, on the port named <code>http-metrics</code>, and take the job name from the service’s <code>jobLabel</code> label”. The Operator expands that into a scrape job with a short discovery block and a long list of relabel rules.')
        + code('- source_labels: [__meta_kubernetes_endpoint_port_name]\n  regex: http-metrics\n  action: keep                       # endpoints on other ports are dropped\n- source_labels: [__meta_kubernetes_service_label_jobLabel]\n  regex: (.+)\n  target_label: job\n  replacement: ${1}                  # job="node-exporter", not the generated job name')
        + p('That last rule explains a confusing moment in the chapter: the scrape job is named <code>serviceMonitor/prometheus/…-node-exporter/0</code>, yet querying <code>{job="serviceMonitor/…"}</code> returns nothing, because relabeling overwrote <code>job</code> with <code>node-exporter</code>.')
        + h2('Relabel actions')
        + table(['Action', 'Effect'],
                [['<code>replace</code> (default)', 'Join source labels with <code>;</code>, match the anchored regex, write the replacement to <code>target_label</code>; an empty result deletes the label'],
                 ['<code>keep</code> / <code>drop</code>', 'Keep or drop the whole target (or series) if the joined value matches'],
                 ['<code>hashmod</code>', 'md5 of the joined value, modulo N, into a label: the basis of sharding'],
                 ['<code>labelmap</code>', 'Copy every label whose name matches the regex to a new name, e.g. all <code>__meta_ec2_tag_(.+)</code> to <code>$1</code>'],
                 ['<code>labeldrop</code> / <code>labelkeep</code>', 'Remove or keep labels by name']])
        + p('After target relabeling, any label still starting with <code>__</code> is removed, and <code>instance</code> defaults to <code>__address__</code> if you didn’t set it. Setting <code>instance</code> to a friendly host name while <code>__address__</code> stays an IP is the book’s trick for readable labels without depending on DNS to scrape.')
        + h2('Debugging')
        + p('Two pages under <i>Status</i>. <b>Targets</b> shows each target and, on hover, its labels before relabeling. <b>Service Discovery</b> is better: per job it lists every discovered target, whether it was dropped, and its labels before and after relabeling side by side.')
        + deeper('inside a provider, and writing your own')
        + h2('How a provider works: the Linode example')
        + p('Every provider implements one Go interface with a single <code>Run</code> method that sends groups of targets on a channel. Most reuse a shared refresh helper that calls the provider’s refresh function on an interval. Linode’s refresh first asks the cheap events API whether anything changed since the last run and only lists every instance when it did, with a full refresh every tenth interval as a safety net.')
        + p('A target group is just a set of target label sets plus labels common to the group. Providers may only set <code>__address__</code> and <code>__meta_*</code> labels; everything visible is your relabeling’s doing.')
        + h2('HTTP SD')
        + p('For years the project refused new providers; the moratorium ended in late 2019 and the count went from 11 to about 25. A provider must serve a widely used platform, so for your CMDB or inventory the answer is <b>HTTP SD</b>, added in 2021. It replaced cron jobs that wrote <code>file_sd</code> files nobody monitored.')
        + table(['Requirement', 'Detail'], [['Status', 'HTTP 200'], ['Header', '<code>Content-Type: application/json</code>'], ['Encoding', 'UTF-8'], ['Body', 'A JSON list of <code>{"targets": [...], "labels": {...}}</code>, the same shape as a static config']])
        + p('The chapter builds one in Go on SQLite. POC 22 builds one in Python from an EC2-style inventory, validates the contract, and shows how to label by name while connecting by IP.')),
    say='Discovery returns candidate targets with hidden meta labels; relabel_configs decide which to scrape and what labels they get, metric_relabel_configs fix or drop series after the scrape, and write_relabel_configs choose what goes to remote storage. I debug with the Service Discovery page, which shows labels before and after relabeling. For anything without a built-in provider I serve HTTP SD.',
    aws='On EC2, <code>ec2_sd_configs</code> needs <code>ec2:DescribeInstances</code>; filter by tag server-side and turn tags into labels with <code>labelmap</code> on <code>__meta_ec2_tag_(.+)</code>. On EKS, use ServiceMonitors with the Operator, or give the AMP managed collector a scrape config with <code>kubernetes_sd_configs</code>. For anything else (Cloud Map, a CMDB, an inventory in DynamoDB), serve HTTP SD from a small Lambda behind a function URL or internal ALB. POC 22 includes the IRSA role and a full EC2 scrape config.',
    iq=[('After a deploy, Prometheus stops scraping a service. The pods are healthy. How do you debug it?',
         ['I’d start at <i>Status → Service Discovery</i> for the job. It answers the first question directly: was the target discovered at all, and if so, was it dropped by relabeling? The page shows the discovered labels next to the labels after relabeling.',
          'If it was never discovered, the discovery side is wrong: the ServiceMonitor’s selector no longer matches the service’s labels, the service is in a namespace the Prometheus isn’t watching (<code>serviceMonitorNamespaceSelector</code>), or the Prometheus CR’s <code>serviceMonitorSelector</code> doesn’t match the ServiceMonitor’s own labels. A changed label in the deploy is the usual culprit.',
          'If it was discovered but dropped, a <code>keep</code> rule no longer matches; most often the port was renamed and the rule keeps only <code>http-metrics</code>. The before-and-after view shows which meta label changed.',
          'If it is kept and appears under <i>Targets</i> but is down, it is a scrape problem: wrong path, TLS, a network policy, or the scrape timing out. The error on the Targets page says which.',
          'Afterwards I’d add an alert on <code>absent(up{job="checkout"})</code> or on the target count dropping, because a target that silently disappears doesn’t fire any <code>up == 0</code> alert.'])],
    quiz=[['When does metric_relabel_configs run?', ['Before the scrape, on targets', 'After the scrape, before samples are stored', 'Only on remote write', 'At query time'], 1, 'relabel_configs works on targets before scraping; metric_relabel_configs works on series after it.'],
          ['What are the three requirements of an HTTP SD endpoint?', ['200, JSON content type, UTF-8', 'TLS, auth, gzip', 'YAML, 201, ASCII', '200, XML, UTF-16'], 0, 'HTTP 200, Content-Type application/json, UTF-8, with a static_config-shaped body.']],
    turn='Run POC 22 and change <code>EC2_RELABEL</code> so the <code>job</code> label comes from a <code>Component</code> tag and instances without it are dropped. Then start the HTTP SD server from <code>http_sd_app()</code> and point a local Prometheus at it with <code>http_sd_configs</code>.',
    take=['Discovery finds candidates; relabeling decides everything else.', 'Three hooks: targets before the scrape, series after it, and series before remote write.', 'Debug with the Service Discovery page; build custom discovery with HTTP SD.']))
