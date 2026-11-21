# Extra diagrams for the Prometheus and Grafana tracks: one or more per lesson that had none.
# Each entry: lesson id -> [(h2 title, figure html)]; the figure goes after the first paragraph under that heading.
from extras2 import pic
from obs1 import box, arrow


def fbox(x, y, w, h, title, sub=''):
    """A filled box in the lesson colour with light text."""
    out = f'<rect class="fc" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'
    out += f'<text x="{x + w / 2}" y="{y + (h / 2 if not sub else h / 2 - 6)}" text-anchor="middle" class="b" dominant-baseline="middle" style="fill:var(--bg)">{title}</text>'
    if sub:
        out += f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" text-anchor="middle" style="fill:var(--bg);font-size:12px">{sub}</text>'
    return out


def hbox(x, y, w, h, title, sub=''):
    """A panel box with a highlighted outline."""
    return box(x, y, w, h, title, sub) + f'<rect class="hl" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>'


def t(x, y, s, cls='m', anchor='start', size=13, fill=''):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}" style="font-size:{size}px{";fill:" + fill if fill else ""}">{s}</text>'


P = {}

# ─────────────────────────────── m-4: ServiceMonitor to targets
P['m-4'] = [('From ServiceMonitor to scrape job', pic(760, 300,
    box(20, 30, 170, 60, 'ServiceMonitor', 'selector + endpoint port') + box(20, 130, 170, 60, 'Service', 'labels app=checkout')
    + fbox(250, 75, 170, 60, 'Prometheus Operator', 'watches resources')
    + box(480, 30, 260, 60, 'Secret: scrape_configs', 'kubernetes_sd_configs role endpoints') + box(480, 130, 260, 60, 'Prometheus reloads', 'discovers Endpoints of the Service')
    + hbox(480, 225, 260, 55, 'Targets', 'pod IP:port, relabeled labels')
    + arrow(192, 60, 248, 95) + arrow(192, 160, 248, 115) + t(20, 114, 'selector matches Service labels', size=12) + arrow(422, 95, 478, 60) + t(430, 120, 'generates', size=12) + arrow(610, 92, 610, 128)
    + arrow(610, 192, 610, 223) + t(600, 212, 'keep only the named port', anchor='end', size=12)
    + t(20, 252, 'The operator never scrapes. It turns custom resources into ordinary', size=12) + t(20, 268, 'Prometheus configuration and lets Kubernetes discovery do the rest.', size=12),
    'My drawing of how a ServiceMonitor becomes targets. The selector picks Services by label, the operator writes the scrape job, and Kubernetes endpoint discovery plus relabeling produce one target per pod port.',
    'ServiceMonitor and Service feed the Prometheus Operator, which writes scrape configuration; Prometheus discovers endpoints and relabeling keeps the named port as targets.'))]

# ─────────────────────────────── m-7: cardinality multiplies
_card = ''
for i, (lab, n, tot) in enumerate([('http_requests_total', '1 name', '1'), ('× method', '5 values', '5'), ('× status', '10 values', '50'), ('× route', '50 values', '2,500'), ('× pod', '20 replicas', '50,000'), ('× user_id', '10,000 users', '500,000,000')]):
    y = 25 + i * 44
    w = [30, 60, 110, 200, 330, 560][i]
    _card += t(20, y + 22, lab, 'b', size=13) + t(20, y + 37, n, size=11)
    _card += (f'<rect class="fc" x="180" y="{y + 6}" width="{w}" height="28" rx="5" style="opacity:{0.35 + i * 0.12}"/>' if i < 5 else
              f'<rect x="180" y="{y + 6}" width="{w}" height="28" rx="5" style="fill:var(--red);opacity:.85"/>')
    _card += t(190 + w if i < 5 else 730, y + 25, tot + ' series', 'b', 'start' if i < 5 else 'end', 13, 'var(--bg)' if i == 5 else '')
P['m-7'] = [('Finding cardinality', pic(760, 300, _card,
    'My illustration of why one careless label hurts. Series are the product of every label’s values: the first five labels give 50,000 series; adding a user ID multiplies that ten-thousandfold. The bars are not to scale; the last one would be far off the page.',
    'Series counts multiply by each label: 1, 5, 50, 2,500, 50,000, and 500 million after adding user_id.'))]

# ─────────────────────────────── m-8: node exporter and textfile collector
P['m-8'] = [('The textfile collector', pic(760, 270,
    box(20, 30, 150, 50, '/proc and /sys', 'kernel counters') + fbox(230, 30, 230, 50, 'node_exporter collectors', 'cpu · meminfo · filesystem · pressure')
    + hbox(520, 80, 220, 60, ':9100/metrics', 'one scrape, all collectors')
    + box(20, 150, 150, 60, 'cron job', 'backup, cert expiry') + box(230, 150, 230, 60, 'write job.prom.tmp', 'then mv to job.prom (atomic)')
    + box(230, 222, 230, 36, 'textfile collector dir', '')
    + arrow(172, 55, 228, 55) + arrow(462, 55, 518, 100) + arrow(172, 180, 228, 180) + arrow(345, 212, 345, 220) + arrow(462, 240, 518, 125) + t(500, 200, 'plus node_textfile_mtime_seconds', size=12),
    'My drawing of the two ways the Node Exporter gets data. Built-in collectors read the kernel; batch jobs write files that the textfile collector exposes. Write to a temporary file and rename it so a scrape never sees half a file, and alert on the file’s age.',
    'Kernel counters flow through node_exporter collectors to /metrics; a cron job writes a temp file, renames it into the textfile directory, and the textfile collector exposes it with its modification time.'))]

# ─────────────────────────────── m-9: remote write internals
P['m-9'] = [('Tuning remote write', pic(760, 290,
    box(20, 40, 120, 50, 'Scrape', 'samples') + box(170, 40, 120, 50, 'WAL', 'on local disk') + box(320, 40, 130, 50, 'WAL watcher', 'tails segments')
    + ''.join(fbox(490, 20 + i * 38, 110, 30, f'shard {i + 1}') for i in range(3)) + t(545, 140, '… up to max_shards', anchor='middle', size=12)
    + hbox(640, 40, 110, 50, 'Remote store', 'AMP · Mimir')
    + arrow(142, 65, 168, 65) + arrow(292, 65, 318, 65) + ''.join(arrow(452, 65, 488, 35 + i * 38) for i in range(3)) + ''.join(arrow(602, 35 + i * 38, 638, 65) for i in range(3))
    + t(20, 185, 'Each shard is a queue of capacity samples, sent in batches of max_samples_per_send.', size=13)
    + t(20, 207, 'Shards scale between min_shards and max_shards with the backlog.', size=13)
    + t(20, 229, 'On 429 or 5xx the batch is retried with backoff from min_backoff to max_backoff;', size=13)
    + t(20, 251, 'if the store is down longer than the WAL keeps data (about 2 hours), samples are lost.', size=13),
    'My drawing of the remote write path. Samples are read back from the write-ahead log, not from memory, which is why a slow endpoint shows up as growing WAL lag rather than lost scrapes.',
    'Scrape to WAL to WAL watcher, fanned out to parallel shards that batch samples to the remote store, with retry and backoff.'))]

# ─────────────────────────────── m-11: mixins
P['m-11'] = [('Monitoring mixins', pic(760, 280,
    box(20, 20, 200, 44, 'config.libsonnet', '_config: selectors, thresholds') + box(20, 76, 200, 44, 'alerts.libsonnet', 'prometheusAlerts')
    + box(20, 132, 200, 44, 'rules.libsonnet', 'prometheusRules') + box(20, 188, 200, 44, 'dashboards.libsonnet', 'grafanaDashboards')
    + fbox(290, 95, 150, 60, 'jsonnet', 'render + override')
    + box(510, 30, 230, 44, 'prometheus_alerts.yaml', '') + box(510, 103, 230, 44, 'prometheus_rules.yaml', '') + box(510, 176, 230, 44, 'dashboards/&#42;.json', '')
    + ''.join(arrow(222, 42 + i * 56, 288, 125) for i in range(4)) + arrow(442, 115, 508, 52) + arrow(442, 125, 508, 125) + arrow(442, 135, 508, 198)
    + t(510, 245, 'rules → Prometheus or AMP', size=12) + t(510, 262, 'dashboards → Grafana', size=12) + t(20, 262, 'You change the hidden _config, never the generated files.', size=12),
    'My drawing of a monitoring mixin. One Jsonnet package holds alerts, recording rules and dashboards that agree with each other; you override its config for your labels and render everything together.',
    'Config, alerts, rules and dashboards libsonnet files rendered by jsonnet into alert YAML, rule YAML and dashboard JSON.'))]

# ─────────────────────────────── m-12: CI layers
_ci = ''
for i, (a, b) in enumerate([('Pull request', 'rules, tests'), ('Syntax', 'promtool check'), ('Unit tests', 'promtool test'), ('Pint', 'live data'), ('Routing', 'amtool check'), ('Deploy', 'AMP rules')]):
    x = 15 + i * 124
    _ci += (fbox if i in (0, 5) else box)(x, 60, 112, 70, a, b)
    if i:
        _ci += arrow(x - 12, 95, x - 2, 95)
_ci += t(15, 175, 'Fails fast and cheap on the left; the right-hand checks need a running Prometheus.', size=13)
_ci += t(15, 197, 'Pint comments inline on the pull request: missing series, missing annotations,', size=13) + t(15, 217, 'and whether the alert would have fired recently.', size=13)
P['m-12'] = [('Three layers of checks', pic(760, 240, _ci,
    'My drawing of a CI pipeline for monitoring changes. Syntax first, then unit tests that pin when an alert fires and with which labels, then Pint against real data, then the Alertmanager config, and only then deploy.',
    'Pipeline: pull request, promtool check, promtool test rules, Pint, amtool check-config, deploy to AMP.'))]

# ─────────────────────────────── m-14: OpenTelemetry picture
P['m-14'] = [('OpenTelemetry in one picture', pic(760, 300,
    box(20, 30, 150, 60, 'App', 'OTel API + SDK') + box(20, 120, 150, 60, 'App', 'auto-instrumented') + box(20, 210, 150, 60, 'Legacy app', '/metrics endpoint')
    + '<rect class="pn" x="230" y="30" width="280" height="240" rx="10"/>' + t(370, 52, 'Collector', 'b', 'middle', 15)
    + fbox(245, 70, 80, 50, 'receivers') + fbox(340, 70, 80, 50, 'processors') + fbox(435, 70, 65, 50, 'export')
    + t(255, 150, 'otlp · prometheus · filelog', size=12) + t(255, 170, 'batch · memory_limiter', size=12) + t(255, 190, 'k8sattributes · tail_sampling', size=12) + t(255, 210, 'prometheusremotewrite', size=12) + t(255, 230, 'otlp · awsxray', size=12)
    + arrow(327, 95, 338, 95) + arrow(422, 95, 433, 95)
    + hbox(570, 30, 170, 55, 'Prometheus / AMP', 'metrics') + hbox(570, 120, 170, 55, 'Tempo / X-Ray', 'traces') + hbox(570, 210, 170, 55, 'Loki / CloudWatch', 'logs')
    + arrow(172, 60, 228, 90, 'OTLP') + arrow(172, 150, 228, 150, 'OTLP') + arrow(172, 240, 228, 210, 'scraped', 0, 22)
    + arrow(512, 90, 568, 57) + arrow(512, 150, 568, 147) + arrow(512, 210, 568, 237),
    'My summary of where OpenTelemetry fits beside Prometheus. Applications emit OTLP or expose /metrics; the collector receives, processes and exports, so backends can change without touching application code.',
    'Apps send OTLP or are scraped by the collector, whose receivers, processors and exporters send metrics to Prometheus or AMP, traces to Tempo or X-Ray, and logs to Loki or CloudWatch.'))]

# ─────────────────────────────── g-1: the stack
P['g-1'] = [('The Grafana stack', pic(760, 300,
    box(20, 20, 150, 46, 'Applications', 'OTel SDKs') + box(20, 86, 150, 46, 'Kubernetes', 'nodes, pods') + box(20, 152, 150, 46, 'Browsers', 'Faro SDK') + box(20, 218, 150, 46, 'Cloud', 'AWS · GCP · Azure')
    + fbox(220, 100, 130, 80, 'Collector', 'OTel · Alloy')
    + hbox(400, 15, 150, 46, 'Loki', 'logs') + hbox(400, 75, 150, 46, 'Mimir · Prometheus', 'metrics') + hbox(400, 135, 150, 46, 'Tempo', 'traces') + hbox(400, 195, 150, 46, 'Pyroscope', 'profiles')
    + fbox(600, 70, 140, 120, 'Grafana', 'explore · dashboards')
    + t(600, 215, 'Alerting · OnCall', size=12) + t(600, 233, 'Incident · k6 · SLOs', size=12)
    + ''.join(arrow(172, 43 + i * 66, 218, 140) for i in range(4)) + ''.join(arrow(352, 140, 398, 38 + i * 60) for i in range(4)) + ''.join(arrow(552, 38 + i * 60, 598, 130) for i in range(4))
    + t(20, 290, 'Same horizontally scalable design behind each store: write path, read path, object storage.', size=12),
    'My drawing of the stack the book teaches. One collector feeds a store per signal; Grafana queries all of them and links between them.',
    'Applications, Kubernetes, browsers and clouds feed a collector, which sends to Loki, Mimir, Tempo and Pyroscope; Grafana queries all four.'))]

# ─────────────────────────────── g-2: a trace as a tree of spans
_tr = '<line class="ln" x1="200" y1="270" x2="740" y2="270"/>' + ''.join(t(200 + k * 108, 288, f'{k * 100} ms', anchor='middle', size=11) for k in range(6))
for i, (name, svc, s, e, f) in enumerate([('GET /checkout', 'frontend', 0, 480, 1), ('POST /cart', 'cart', 40, 200, .8), ('SELECT cart', 'cart → db', 70, 180, .6),
                                          ('POST /charge', 'payment', 220, 450, .8), ('fraud check', 'payment', 240, 300, .6), ('publish event', 'kafka', 400, 440, .6)]):
    y = 22 + i * 40
    _tr += t(20, y + 18, name, 'b', size=13) + t(20, y + 33, svc, size=11)
    _tr += f'<rect class="fc" x="{200 + s * 1.08}" y="{y + 4}" width="{(e - s) * 1.08}" height="26" rx="4" style="opacity:{f}"/>'
P['g-2'] = [('Traces', pic(760, 300, _tr,
    'My drawing of one trace as a waterfall. Every bar is a span with the same trace ID; each child records its parent’s span ID, which is how the tree is rebuilt. The gap between the cart and payment calls is time the frontend spent on its own work.',
    'A trace waterfall: GET /checkout spans 480 ms, with child spans for the cart call and its database query, the payment call with a fraud check, and a Kafka publish.'))]

# ─────────────────────────────── g-5: Mimir architecture
P['g-5'] = [('Where metrics are stored', pic(760, 300,
    t(20, 24, 'write path', 'b') + box(20, 40, 130, 50, 'Prometheus', 'remote write') + fbox(190, 40, 130, 50, 'Distributor', 'validates, shards')
    + ''.join(box(360, 25 + i * 34, 130, 28, f'Ingester {i + 1}') for i in range(3)) + t(360, 135, 'replicated ×3', size=11)
    + hbox(560, 110, 180, 70, 'Object storage', 'S3 · GCS · Azure blobs') + box(560, 210, 180, 44, 'Compactor', 'merges, dedups blocks')
    + t(20, 184, 'read path', 'b') + box(20, 200, 130, 50, 'Grafana', 'PromQL') + fbox(190, 200, 130, 50, 'Query frontend', 'split, cache')
    + box(360, 200, 130, 50, 'Querier', '') + box(360, 260, 130, 32, 'Store gateway', '')
    + arrow(152, 65, 188, 65) + arrow(322, 65, 358, 40) + arrow(322, 65, 358, 74) + arrow(322, 65, 358, 108) + arrow(492, 74, 558, 135) + t(530, 92, 'blocks every 2 h', size=12)
    + arrow(152, 225, 188, 225) + arrow(322, 225, 358, 225) + arrow(470, 198, 470, 128, 'recent', 28, 10, True) + arrow(425, 252, 425, 258) + arrow(492, 276, 558, 160, '', 0, 0, True) + arrow(650, 208, 650, 182),
    'My drawing of Mimir’s architecture from the chapter. Writes are sharded and replicated across ingesters, which upload blocks to object storage; queries are split and cached at the front, then read recent data from ingesters and older data through store gateways.',
    'Mimir write path: Prometheus to distributor to three ingesters to object storage; read path: Grafana to query frontend to querier, which reads ingesters and store gateways; a compactor merges blocks.'))]

# ─────────────────────────────── g-6: context propagation
P['g-6'] = [('Context propagation', pic(760, 270,
    fbox(20, 40, 150, 60, 'Frontend', 'span a1') + fbox(300, 40, 150, 60, 'Checkout', 'span b2, parent a1') + fbox(580, 40, 160, 60, 'Shipping', 'span c3, parent b2')
    + arrow(172, 70, 298, 70) + arrow(452, 70, 578, 70)
    + t(235, 120, 'HTTP header', anchor='middle', size=12) + t(515, 120, 'Kafka message header', anchor='middle', size=12)
    + box(20, 150, 720, 48, 'traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01', '')
    + t(225, 222, 'version', anchor='middle', size=12) + t(385, 222, '32-hex trace ID: same on every hop', anchor='middle', size=12) + t(585, 222, '16-hex parent span ID', anchor='middle', size=12) + t(705, 222, 'sampled', anchor='middle', size=12)
    + t(20, 255, 'baggage: key=value pairs travel alongside (≤ 64 members, 8,192 bytes); X-Ray and B3 use their own headers.', size=12),
    'My drawing of W3C trace context. Each service keeps the trace ID, makes a new span ID, and passes its own span ID on as the parent. Any hop that drops the header breaks the trace in two.',
    'Frontend, checkout and shipping pass a traceparent header with the same trace ID and changing parent span IDs.'))]

# ─────────────────────────────── g-7: AWS query in place or ingest
P['g-7'] = [('AWS: query in place or ingest', pic(760, 300,
    box(20, 110, 150, 70, 'AWS services', 'EC2, RDS, Lambda…')
    + box(230, 30, 180, 50, 'CloudWatch', 'metrics + Logs') + box(230, 100, 180, 50, 'AWS X-Ray', 'traces')
    + box(230, 180, 180, 50, 'YACE or metric streams', 'metrics out') + box(230, 245, 180, 46, 'Lambda or Firehose', 'logs out')
    + hbox(480, 180, 120, 50, 'Prometheus', 'AMP · Mimir') + hbox(480, 245, 120, 46, 'Loki', '')
    + fbox(640, 70, 100, 140, 'Grafana', '')
    + arrow(172, 130, 228, 55) + arrow(172, 145, 228, 125) + arrow(172, 160, 228, 205) + arrow(172, 170, 228, 268)
    + arrow(412, 55, 638, 80) + t(430, 50, 'query in place: CloudWatch data source', size=12) + arrow(412, 125, 638, 125) + t(430, 118, 'X-Ray data source', size=12)
    + arrow(412, 205, 478, 205) + arrow(412, 268, 478, 268) + arrow(602, 205, 638, 180) + arrow(602, 268, 638, 200),
    'My summary of the chapter’s two routes. Querying CloudWatch and X-Ray in place is quick and keeps data in AWS, but each query costs API calls and the data stays separate; ingesting into Prometheus and Loki puts AWS data beside application data, at the cost of a pipeline and duplicate storage.',
    'AWS services report to CloudWatch and X-Ray, which Grafana queries in place, or are exported via YACE, metric streams, Lambda or Firehose into Prometheus and Loki.'))]

# ─────────────────────────────── g-9: Grafana alerting flow
P['g-9'] = [('Grafana Alerting', pic(760, 300,
    fbox(20, 30, 140, 64, 'Alert rule', 'reduce + threshold') + box(200, 30, 150, 64, 'Evaluation group', 'every 1 m, pending 5 m')
    + box(390, 30, 160, 64, 'Notification policy', 'tree, matched on labels') + box(590, 30, 150, 64, 'Contact point', 'chat, email, webhook')
    + arrow(162, 62, 198, 62) + arrow(352, 62, 388, 62) + arrow(552, 62, 588, 62)
    + box(390, 130, 160, 50, 'Mute timings', 'and silences') + arrow(470, 128, 470, 96, '', 0, 0, True)
    + hbox(590, 130, 150, 64, 'OnCall', 'alert group, escalation') + arrow(665, 96, 665, 128)
    + hbox(590, 225, 150, 60, 'Incident', 'roles, timeline, review') + arrow(665, 196, 665, 223) + t(675, 214, 'declare', size=12)
    + t(20, 140, 'Normal → Pending → Firing', 'b', size=13) + t(20, 160, 'Pending holds a rule until the condition', size=12) + t(20, 177, 'has lasted the whole pending period.', size=12)
    + t(20, 215, 'Annotations carry summary, description,', size=12) + t(20, 232, 'runbook URL and dashboard link; labels', size=12) + t(20, 249, 'such as team and severity drive routing.', size=12),
    'My drawing of the path from a rule to an incident in Grafana. The rule decides whether something is wrong; the policy tree and contact points decide who hears about it; OnCall escalates; Incident runs the response.',
    'Alert rule, evaluation group, notification policy and contact point in sequence, with mute timings, then OnCall escalation and Grafana Incident.'))]

# ─────────────────────────────── g-10: connectors
P['g-10'] = [('The collector’s Helm chart', pic(760, 290,
    t(20, 18, 'traces pipeline', 'b') + box(20, 50, 110, 46, 'otlp', 'receiver') + box(160, 50, 110, 46, 'batch', 'processor')
    + box(310, 10, 170, 40, 'otlp → Tempo', '') + fbox(310, 60, 170, 34, 'spanmetrics') + fbox(310, 104, 170, 34, 'servicegraph')
    + t(495, 34, 'exporters', size=12) + t(495, 104, 'connectors: exporter here …', size=12)
    + arrow(132, 73, 158, 73) + arrow(272, 68, 308, 30) + arrow(272, 73, 308, 77) + arrow(272, 80, 308, 121)
    + t(20, 168, 'metrics pipeline', 'b') + box(20, 180, 230, 46, 'otlp, spanmetrics, servicegraph', '… receiver there')
    + box(280, 180, 190, 46, 'memory_limiter, filter,', 'transform, batch') + hbox(500, 180, 240, 46, 'prometheusremotewrite', 'exporter → Mimir / AMP')
    + arrow(395, 140, 160, 178, '', 0, 0, True) + arrow(252, 203, 278, 203) + arrow(472, 203, 498, 203)
    + t(20, 258, 'RED metrics and service graphs come from 100% of spans, before any sampling,', size=12) + t(20, 276, 'so tail sampling later in the traces pipeline doesn’t distort them.', size=12),
    'My drawing of the book’s collector pipeline. The spanmetrics and servicegraph connectors sit at the end of the traces pipeline and the start of the metrics pipeline, turning spans into rate, error and duration series.',
    'Traces pipeline from otlp to batch to Tempo, with spanmetrics and servicegraph connectors feeding the metrics pipeline that exports via Prometheus remote write.'))]

# ─────────────────────────────── g-12: RUM, flame graph, load shapes
_flame = ''
for x, y, w, name, op in [(20, 160, 720, 'main', .35), (20, 122, 450, 'handleRequest', .5), (470, 122, 270, 'gcWorker', .5), (20, 84, 300, 'renderTemplate', .65),
                          (320, 84, 150, 'json.Marshal', .65), (20, 46, 220, 'regexp.Compile', .85), (240, 46, 80, 'Join', .65), (470, 84, 180, 'markSweep', .65)]:
    _flame += f'<rect class="fc" x="{x}" y="{y}" width="{w}" height="34" rx="3" style="opacity:{op}"/><text x="{x + 8}" y="{y + 22}" class="b" style="fill:var(--bg);font-size:13px">{name}</text>'
_flame += t(20, 220, 'Width = share of CPU samples, including children. Depth = call stack. The x-axis is not time.', size=12)
_flame += t(20, 30, 'regexp.Compile has wide self time: compiling a pattern on every request is a classic find.', size=12)
_shape = '<line class="ln" x1="60" y1="240" x2="740" y2="240"/><line class="ln" x1="60" y1="240" x2="60" y2="20"/>' + t(740, 262, 'duration →', anchor='end', size=12) + t(70, 18, 'load', size=12)
for pts, lab, lx, ly, dash in [('60,232 110,232', 'smoke', 75, 225, False), ('60,240 90,160 300,160 330,240', 'average', 190, 152, False), ('60,240 100,90 330,90 360,240', 'stress', 190, 82, False),
                               ('370,240 380,30 395,240', 'spike', 400, 40, False), ('420,240 600,30', 'breakpoint', 560, 60, True), ('60,240 90,170 720,170 735,240', 'soak', 690, 162, True)]:
    _shape += f'<polyline class="{"dash" if dash else "hl"}" points="{pts}"/>' + t(lx, ly, lab, 'b', size=12)
P['g-12'] = [
    ('Real user monitoring', pic(760, 230,
        box(20, 30, 160, 60, 'Browser', 'Faro Web SDK') + fbox(240, 30, 150, 60, 'Collector', 'hosted or Alloy')
        + hbox(450, 10, 130, 44, 'Loki', 'vitals, errors, events') + hbox(450, 70, 130, 44, 'Tempo', 'frontend traces')
        + fbox(630, 30, 110, 60, 'Frontend app', '') + box(450, 150, 290, 54, 'Backend traces and logs', 'same trace ID from the browser span')
        + arrow(182, 60, 238, 60) + arrow(392, 55, 448, 32) + arrow(392, 65, 448, 92) + arrow(582, 32, 628, 55) + arrow(582, 92, 628, 70) + arrow(515, 116, 515, 148, 'session → trace → logs', 75, 6),
        'My drawing of Grafana’s RUM pipeline. Metrics in the Frontend Observability app are computed from Loki logs with LogQL, and a session links through traces to the backend.',
        'Faro in the browser sends to a collector, which writes to Loki and Tempo; the frontend app reads both and links a session to backend traces and logs.')),
    ('Continuous profiling', pic(760, 235, _flame,
        'My illustrative flame graph, not real data. Look for wide boxes near the top: functions with a lot of self time. A wide box with wide children above it is a hot path, not a hot function.',
        'A flame graph with main at the bottom, handleRequest and gcWorker above it, then renderTemplate, json.Marshal and markSweep, with a wide regexp.Compile at the top.')),
    ('Load testing', pic(760, 270, _shape,
        'My sketch of the six load test shapes from the chapter: how much load, for how long. Soak and breakpoint are dashed because they run longest.',
        'Six load profiles: smoke tiny and short; average and stress plateaus; spike a sudden peak; breakpoint a steady ramp; soak a long plateau.')),
]

# ─────────────────────────────── g-14: DevOps loop and deployment verification
import math
_loop = '<circle cx="380" cy="160" r="110" class="dash"/>' + t(380, 155, 'observability', 'b', 'middle', 15) + t(380, 175, 'in every phase', anchor='middle', size=12)
for i, (ph, what) in enumerate([('Code', 'local stack'), ('Test', 'k6, CI data'), ('Release', 'SLOs under load'), ('Deploy', 'annotations, verify'), ('Operate', 'SLOs, incidents'), ('Monitor', 'RUM, profiles, trends'), ('Plan', 'capacity, impact')]):
    a = -math.pi / 2 + i * 2 * math.pi / 7
    cx, cy = 380 + 220 * math.cos(a), 160 + 125 * math.sin(a)
    _loop += (fbox if ph in ('Deploy', 'Monitor') else box)(round(cx - 75), round(cy - 25), 150, 50, ph, what)
P['g-14'] = [
    ('The life cycle, with a caution', pic(760, 320, _loop,
        'My drawing of the DevOps life cycle with what Grafana contributes at each phase. Operate and monitor use the same tools; operate keeps customers served now, monitor documents behaviour for the next plan.',
        'Seven phases in a loop: code, test, release, deploy, operate, monitor, plan, each with an observability contribution.')),
    ('Automated deployment verification', pic(760, 230,
        fbox(20, 80, 120, 60, 'Deploy', 'new version') + box(180, 80, 120, 60, 'Annotate', 'Grafana API') + box(340, 80, 120, 60, 'Bake', 'e.g. 10 min')
        + box(500, 20, 240, 40, 'error ratio from logs < SLO', '') + box(500, 70, 240, 40, 'smoke test logins succeed', '') + box(500, 120, 240, 40, 'downstream calls healthy', '')
        + hbox(500, 175, 110, 44, 'Continue', '') + '<rect x="630" y="175" width="110" height="44" rx="8" style="fill:var(--red);opacity:.85"/>' + t(685, 202, 'Roll back', 'b', 'middle', 14, 'var(--bg)')
        + arrow(142, 110, 178, 110) + arrow(302, 110, 338, 110) + arrow(462, 110, 498, 40) + arrow(462, 110, 498, 90) + arrow(462, 110, 498, 140)
        + t(20, 190, 'All checks pass: continue the rollout.', size=12) + t(20, 208, 'Any check fails: roll back automatically.', size=12),
        'My drawing of the deployment gate the chapter recommends once deploys are frequent: the pipeline queries telemetry itself instead of a person watching a dashboard.',
        'Deploy, annotate, bake, then three telemetry checks decide between continuing and rolling back.')),
]
