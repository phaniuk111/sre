# Track 4: Observability with Grafana (Packt, 2024). Chapters 1-7. My own words throughout.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import h2, h3, note, deeper, code, ol
from obs1 import box, arrow

L = []


def meta(part, chs, poc):
    return f'<span class="chip">Grafana · {part}</span>{chs}' + (f' · {poc}' if poc else '')


# ══════════════════════════════════════════════════════════════ intro
L.append(dict(
    id='g', dot='G', part='G1', nav='About this book', h1='Observability with Grafana: the fourth book on the map',
    meta='<span class="chip">Observability with Grafana</span>Rob Chapman and Peter Holmes · Packt, January 2024 · 15 chapters',
    learn=['What this book adds to the Prometheus book', 'The five personas it uses, and why they matter in interviews', 'How the lessons are grouped and which POCs go with them'],
    body=(
        h2('Where it fits')
        + p('The Prometheus book goes deep on one signal. This book goes wide: logs in Loki, metrics in Mimir and Prometheus, traces in Tempo, profiles in Pyroscope, real user monitoring with Faro, load tests with k6, and Grafana itself for dashboards, alerting, on-call and incidents. It then turns to running all of that as a platform: infrastructure as code, architecture, access control, and observability across the DevOps life cycle.')
        + p('It is written for a broad audience, so some chapters are walkthroughs of the Grafana Cloud UI. The lessons here keep the concepts and the decisions, and leave the click-by-click steps to the book’s repository.')
        + h2('Five personas')
        + p('Every chapter frames its advice around five people. Using them in an interview answer (“for the on-call engineer this dashboard needs…, for the service manager…”) shows you design observability for users, not for tools.')
        + table(['Persona', 'Role', 'Needs from observability', 'Pain'],
                [['Diego Developer', 'Frontend, backend, platform', 'Easy instrumentation libraries; clear performance standards', 'Too much noise; being forced to change code when tooling changes'],
                 ['Ophelia Operator', 'SRE, DevOps, support', 'Good data fast; seeing that a deploy happened when trouble started', 'Alerts she can’t fix; burnout'],
                 ['Steven Service', 'Service delivery, incident coordination', 'Comparisons across products; getting the right people on a call; a record for the post-mortem', 'Finding who can fix it'],
                 ['Pelé Product', 'Product manager', 'How customers actually use the product; a shared language with engineers', 'No view of usage; lost trust when stability slips'],
                 ['Masha Manager', 'Leadership', 'Aggregated, trustworthy data on delivery and cost', 'Apologising to customers; cloud overspend']])
        + h2('How the lessons are organised')
        + table(['Lesson', 'Topic', 'Chapters', 'Code'],
                [['<a href="#g-1">1</a>', 'Observability and the Grafana stack', '1', ''],
                 ['<a href="#g-2">2</a>', 'Instrumentation: log formats, metric types, tracing protocols, libraries, the lab', '2–3', 'POC 27'],
                 ['<a href="#g-4">3</a>', 'Logs with Loki and LogQL', '4', 'POC 26'],
                 ['<a href="#g-5">4</a>', 'Metrics with Prometheus and Mimir, protocols, exemplars', '5', 'POC 20, 21'],
                 ['<a href="#g-6">5</a>', 'Traces with Tempo and TraceQL, context propagation', '6', 'POC 27'],
                 ['<a href="#g-7">6</a>', 'Kubernetes, AWS, GCP and Azure', '7', 'POC 28'],
                 ['<a href="#g-8">7</a>', 'Dashboards with a purpose', '8', 'POC 29'],
                 ['<a href="#g-9">8</a>', 'Incident management, alerting, OnCall and Incident', '9', 'POC 23, 24'],
                 ['<a href="#g-10">9</a>', 'Automation with Helm, Ansible and Terraform', '10', 'POC 28, 29'],
                 ['<a href="#g-11">10</a>', 'Architecting an observability platform', '11', 'POC 28'],
                 ['<a href="#g-12">11</a>', 'Real user monitoring, profiling and load testing', '12–13', 'POC 30'],
                 ['<a href="#g-14">12</a>', 'DevOps, troubleshooting and what’s next', '14–15', 'POC 30']])
        + tiles([('Part 1 · Signals and the stack', 'Lessons 1 to 6: what each signal is for, how it is produced, stored and queried, and how to collect it from Kubernetes and clouds.', 'amber'),
                 ('Part 2 · Running observability', 'Lessons 7 to 12: dashboards, incidents, automation, architecture, the frontend and performance, and the life cycle around it.', 'cyan'),
                 ('Overlap with the Prometheus track', 'PromQL, Alertmanager and SLOs are taught in depth there; the lessons here link across rather than repeat.')])
        + note('How I read it', 'All fifteen chapters in full, and every figure (about 190, most of them UI screenshots). Two of the PromQL examples contain small errors, noted where they appear.')),
    take=['This book is the breadth to the Prometheus book’s depth.', 'Design observability for personas, not tools.', 'Part 1 is signals and collection; part 2 is running it as a platform.']))

# ══════════════════════════════════════════════════════════════ 1 Observability and the stack
L.append(dict(
    id='g-1', dot='1', part='G1', nav='Observability and the stack', h1='Observability, the signals, and the Grafana stack',
    meta=meta('Signals', 'Chapter 1', ''),
    learn=['Monitoring versus observability, from control theory and a steam engine', 'Metrics, logs, traces, and the other signals: profiles and events', 'What each part of the LGTM stack does, and what else Grafana Labs offers', 'The alternatives, and the SaaS versus self-hosted choice'],
    body=(
        h2('The big picture')
        + p('Modern systems have moved from <b>complicated</b> (an engine: clear cause and effect) to <b>complex</b> (city traffic: behaviour emerges from interactions). Downtime is expensive; the book quotes an estimate of about $9,000 a minute from a 2016 Ponemon study. Observability is how you manage that risk, and done badly it is a cost of its own.')
        + p('The term comes from control theory. James Watt’s steam-engine governor illustrates both ideas. Its spinning weights measure one predefined quantity, shaft speed, and adjust the throttle: that is <b>monitoring</b>. But if the governor spins oddly fast or slow, you can infer that the sliding ring is sticking or the adjustment is wrong, without having defined “too fast” in advance and without knowing the whole engine: that is <b>observability</b>, inferring internal state from external outputs.')
        + h3('The Panama Canal example')
        + table(['Monitor and alert on', 'Observe within normal limits'],
                [['A gate stuck open', 'A gate that is slowly taking longer to open: maintenance due'],
                 ['Water level dropping fast: a leak', 'Water dropping only when the level is high: a small leak near the top of the wall'],
                 ['A ship taking too long to exit', 'Ships slower when the wind blows from one direction: compare hourly averages']])
        + p('The lesson: the same data that drives alerts also answers questions nobody thought to alert on.')
        + h2('The signals')
        + table(['Signal', 'What it is', 'Strength', 'Weakness'],
                [['Metrics', 'Numbers at points in time with labels', 'Cheap, fast to search, ideal for “is something wrong?”', 'Must be defined in advance'],
                 ['Logs', 'Text records of events, usually unstructured', 'Rich detail about what happened', 'Slow to search; the same failure is worded many ways'],
                 ['Traces', 'The path of one request: a trace ID shared by spans, each with its own ID and parent', 'Shows where time and errors go across services', 'Volume; needs propagation and sampling'],
                 ['Profiles', 'Stack samples of CPU and memory use', 'Finds the expensive function; cuts cost', 'Low level, needs domain knowledge'],
                 ['Events', 'A whole action, such as “deployed v1.4”', 'Context that shortens incidents', 'Overloaded term']])
        + p('A trace across the canal locks: the ship gets a trace ID at the first lock, each lock creates a span (entry, exit, events such as gates opening, attributes such as the ship’s ID) and passes the trace ID and its span ID on to the next lock.')
        + h2('The Grafana stack')
        + tiles([('Loki', 'Logs. Indexes only labels, stores lines compressed in object storage, scales queriers horizontally. GA November 2019.', 'amber'),
                 ('Grafana', 'Visualisation since 2014: 150+ data source plugins and thousands of community dashboards. Began as a fork of Kibana for Graphite.', 'amber'),
                 ('Tempo', 'Traces on object storage, aiming to keep 100% of the read path; 2M+ spans per second at 1.0. Can generate metrics from spans. GA June 2021.', 'amber'),
                 ('Mimir', 'Metrics: a Prometheus-compatible TSDB on object storage, forked from Cortex, load-tested to a billion active series. GA March 2022.', 'amber')])
        + p('Together, LGTM (a joke on “looks good to me”). Around them: Grafana Agent (collection, since succeeded by Grafana Alloy), Enterprise data-source plugins (GitLab, Snowflake, Databricks…), the incident response tools (Alerting, OnCall, Incident), <b>Faro</b> for real user monitoring, <b>k6</b> for load testing (acquired 2021) and <b>Pyroscope</b> for continuous profiling (acquired 2023, merged with Phlare).')
        + deeper('alternatives and deployment choices')
        + h2('Alternatives and deployment')
        + p('The book lists collectors (OpenTelemetry Collector, Fluent Bit, Vector, Beats, Telegraf, StatsD, collectd, rsyslog, Fluentd, Zipkin) and around fifty storage and visualisation products, from CloudWatch and Datadog to Elastic, Honeycomb, Jaeger, New Relic, Splunk, Thanos and VictoriaMetrics. Knowing the landscape matters more than memorising it.')
        + p('Grafana Labs’ products are mostly open source and can run anywhere, packaged for Linux, Windows, containers, Helm and Tanka. The alternative is Grafana Cloud, which gives you the storage backends and Grafana with an SLA and none of the operational work. The book uses Cloud’s free tier for its examples.')),
    say='Monitoring watches for conditions you defined in advance; observability lets you infer internal state from outputs and answer new questions. I use metrics to know something is wrong, traces to find where, logs and profiles to find why, and events like deployments for context. In the Grafana world that is Mimir or Prometheus, Tempo, Loki and Pyroscope, all on object storage, with Grafana on top.',
    aws='The AWS-native equivalents: CloudWatch metrics and Amazon Managed Service for Prometheus for metrics, CloudWatch Logs for logs, X-Ray (and Application Signals) for traces, CloudWatch RUM for the frontend, CloudWatch Synthetics for probes, and Amazon Managed Grafana to view them all. Many teams mix: AMP plus Amazon Managed Grafana for application metrics, CloudWatch for AWS service metrics, and Loki or CloudWatch Logs for logs.',
    iq=[('What is the difference between monitoring and observability, and does the distinction matter in practice?',
         ['Monitoring is watching for conditions you defined in advance: CPU above a threshold, an endpoint returning errors, a queue too long. It answers known questions, and it is how you get alerted.',
          'Observability is a property of the system: how well you can understand its internal state from what it emits, including for questions nobody anticipated. The book’s canal example makes it concrete: the same water-level data that alerts on a big leak can reveal a small leak near the top of the wall, if you can slice it by level and time.',
          'In practice it matters in two ways. It changes what you collect: high-dimensional data you can slice later (traces with attributes, structured logs, labelled metrics) rather than only pre-aggregated checks. And it changes how incidents go: when the failure is novel, which in a complex system is most of the time, you need to ask new questions quickly, not wait for someone to add a dashboard.',
          'I wouldn’t throw monitoring away; alerts on user-facing symptoms are still the entry point. Observability is what you need after the page.'])],
    quiz=[['What does the L in LGTM stand for, and what does it store?', ['Loki, logs', 'Linkerd, traces', 'Lambda, events', 'Loki, metrics'], 0, 'Loki stores logs, indexing only labels.'],
          ['Which signal is best for answering “is something wrong right now?” cheaply?', ['Logs', 'Metrics', 'Profiles', 'Traces'], 1, 'Metrics are small, fast to query and ideal for alerting.']],
    turn='Pick a system you know and write the canal table for it: three things you would alert on, and three questions you could answer from the same data without new alerts.',
    take=['Monitoring answers known questions; observability lets you ask new ones.', 'Metrics, logs, traces, profiles and events each answer a different question.', 'LGTM: Loki, Grafana, Tempo, Mimir, all on object storage.']))

# ══════════════════════════════════════════════════════════════ 2 Instrumentation
L.append(dict(
    id='g-2', dot='2', part='G1', nav='Instrumentation', h1='Instrumenting applications and infrastructure',
    meta=meta('Signals', 'Chapters 2–3', 'POC 27'),
    learn=['Structured, semi-structured and unstructured logs, and seven common formats', 'Counters, gauges, histograms and summaries, and how metric protocols differ', 'Spans, traces and tracing protocols, and best practice for each signal', 'Automatic versus manual instrumentation; infrastructure telemetry through syslog and SNMP', 'The book’s lab: Grafana Cloud plus the OpenTelemetry demo'],
    body=(
        h2('Logs')
        + table(['Structure', 'What it is', 'Trade-off'],
                [['Structured', 'A fixed shape, usually JSON or key=value; can be validated against a schema', 'Easy for machines; JSON is hard for people to scan'],
                 ['Semi-structured', 'Human-readable with a known pattern, parsed by regular expressions', 'Fragile parsing'],
                 ['Unstructured', 'Free text, colours, spacing for terminals', 'Every consumer writes custom parsing; developers can’t change the log without breaking someone. Multi-line entries such as stack traces need encapsulation on the leading timestamp']])
        + table(['Format', 'Where you meet it'],
                [['CEF', 'Security tools (ArcSight, SIEMs): prefix, pipe-separated header, key=value body'], ['NCSA Common Log Format', 'Web servers; fixed fields, <code>-</code> for missing'],
                 ['W3C Extended', 'IIS; configurable <code>#Fields</code>'], ['Windows Event Log', 'Windows; categorised, documented event IDs'],
                 ['JSON', 'Modern applications'], ['Syslog', 'Network devices, Linux; ports 514 and 6514 (TLS)'], ['logfmt', 'Go projects, Prometheus itself; key=value, human-readable']])
        + h2('Metrics')
        + p('A metric is a name, a value and dimensions. The four types behave differently, and protocols define them slightly differently: StatsD resets counters on every flush, Prometheus only when the process restarts. Know which one you are using.')
        + table(['', 'Counter', 'Gauge', 'Histogram', 'Summary'],
                [['Goes down', 'No (resets only)', 'Yes', 'No', 'No'], ['Percentiles', 'No', 'No', 'Estimated at query time', 'Computed in the client'],
                 ['Aggregate across instances', 'Yes', 'Yes', 'Yes', 'No'], ['Typical query', '<code>rate()</code>', 'value', '<code>histogram_quantile(rate(_bucket))</code>', 'read quantile']])
        + note('A correction to the book’s table', 'It says only counters can be used with a rate function. In Prometheus, histogram <code>_bucket</code>, <code>_sum</code> and <code>_count</code> series are counters, and you always take their <code>rate()</code> before <code>histogram_quantile</code>. See <a href="#m-3q">the PromQL lesson</a>.')
        + table(['Protocol', 'Push or pull', 'Types'],
                [['StatsD', 'Push (UDP 8125)', 'Counters, gauges, timers, histograms, meters'], ['DogStatsD', 'Push', 'StatsD plus tags, histograms, service checks, events'],
                 ['OTLP', 'Push (gRPC 4317, HTTP 4318)', 'Counters, gauges, histograms, legacy summaries'], ['Prometheus', 'Pull (/metrics)', 'Counters, gauges, cumulative histograms, summaries']])
        + p('Best practice from the book: decide what you want metrics for first (it feeds SLIs and SLOs), manage cardinality (labelling by server gives hundreds of series, by user millions, and you pay for each), and add context with exemplars so a data point links to a trace.')
        + h2('Traces')
        + p('A trace is a directed acyclic graph of spans. The trace has an ID, a name and start and end times. Each span has the trace ID, its own span ID, its parent’s span ID, a name and timings. If a service receives no trace ID it starts a new one; otherwise it passes the one it received to every call it makes.')
        + table(['Protocol', 'Notes'],
                [['OTLP', 'Attributes, context propagation, span events, span links, span kind'], ['Zipkin', 'Tags, annotations, kind; B3 headers'],
                 ['Jaeger', 'Thrift and Proto formats; the Jaeger SDKs are retired in favour of OpenTelemetry']])
        + table(['Concern', 'Mitigation'],
                [['Performance: latency, memory, startup cost, worse with auto-instrumentation', 'Sampling between 0% and 100%, decided at the root and passed down so traces stay whole'],
                 ['Cost: network and storage', 'Sample, filter, set retention'], ['Accuracy', 'Validate context propagation, or spans split into separate traces']])
        + h2('Libraries')
        + p('<b>Automatic instrumentation</b> is fast to adopt and gives visibility in minutes, by bytecode manipulation in Java or monkey patching in Python and JavaScript; without care it costs performance and money. <b>Manual instrumentation</b> gives exactly the telemetry you want but needs code and API knowledge. The industry is converging on OpenTelemetry SDKs; Spring Boot 3’s Micrometer exports OTLP by default.')
        + deeper('infrastructure telemetry and the lab')
        + h2('Infrastructure')
        + table(['Component', 'Telemetry', 'How'],
                [['Servers (bare metal or VMs)', 'Temperature, CPU, disk, memory: capacity forecasting', 'An agent on the OS'],
                 ['Network and security devices', 'Latency, throughput, packet loss, bandwidth', 'SNMP polling and traps; syslog from firewalls'],
                 ['Power and cooling', 'Supply and backup state, voltage, wattage', 'SNMP; Modbus registers on older kit']])
        + p('Syslog (from Sendmail in the 1980s) and SNMP (part of the original IETF suite, with traps for events) are still everywhere; most collectors, the OpenTelemetry Collector included, can receive them.')
        + h2('The lab')
        + p('Chapter 3 builds the environment the rest of the book uses: a Grafana Cloud free stack (about 10,000 metric series, 50 GB each of logs, traces and profiles, three IRM users, 500 k6 virtual-user hours), a local k3d Kubernetes cluster, the OpenTelemetry Collector Helm chart with credentials in a separate values file, and the OpenTelemetry demo, a polyglot telescope shop with a load generator. The common mistake is endpoints: Loki needs <code>/loki/api/v1/push</code>, Prometheus <code>/api/prom/push</code>, and Tempo a host and port 443 with no scheme.')),
    say='I prefer structured logs in JSON or logfmt so nobody depends on fragile parsing, histograms over summaries because they aggregate across instances, and OpenTelemetry SDKs for traces with context propagated on every call and sampling decided at the root. Before instrumenting I decide what questions the data must answer, because that drives which SLIs I need and keeps cardinality, and cost, under control.',
    aws='The ADOT SDKs and collector are AWS’s OpenTelemetry distribution; auto-instrumentation agents exist for Java, Python, .NET and Node.js and are injected by the ADOT operator on EKS. CloudWatch embedded metric format turns structured JSON logs into metrics for CloudWatch-native setups. For network gear, run an SNMP exporter or the collector’s SNMP receiver in a VPC that can reach devices, and syslog into CloudWatch Logs or Loki through Fluent Bit.',
    iq=[('A team asks whether to use auto-instrumentation or manual instrumentation for a new Java service. What do you recommend?',
         ['Both, in that order. Auto-instrumentation with the OpenTelemetry Java agent gives server and client spans for HTTP, gRPC, database and messaging libraries, plus standard metrics, on day one with no code changes. That covers most of what an on-call engineer needs: where time goes and which dependency fails.',
          'Then add manual instrumentation where the business logic lives: spans around important internal steps, attributes such as tenant or order type (on spans, not metric labels), and a few domain metrics such as orders placed. Auto-instrumentation can’t know those.',
          'I’d watch three things. Overhead: measure startup time and latency with the agent, and turn off instrumentations you don’t need. Sampling: parent-based, decided at the edge, so traces stay complete. And naming: follow semantic conventions so dashboards work across services.',
          'On AWS I’d use the ADOT Java agent, injected by the operator via a pod annotation, exporting OTLP to the node collector.'])],
    quiz=[['Why can’t summaries from several pods be combined into one percentile?', ['They are gauges', 'Percentiles can’t be averaged; histogram buckets can be summed first', 'They lack labels', 'They reset too often'], 1, 'That is why the book marks summaries as not aggregatable across series.'],
          ['What happens if a service drops the incoming trace context?', ['Nothing', 'Its spans start a new trace, so the request appears as separate traces', 'The request fails', 'Sampling increases'], 1, 'Broken propagation splits one request into several traces.']],
    turn='Take one service you know and list: its log format (and whether anyone parses it), its three most important metrics and their types, and where trace context could be dropped (queues, thread pools, third-party calls). Then run POC 27 and check a <code>traceparent</code> header from your own logs with <code>parse_traceparent()</code>.',
    take=['Prefer structured logs; know which format each source uses.', 'Know your metric types and your protocol’s definitions of them.', 'Traces depend on propagation; sample at the root.']))

# ══════════════════════════════════════════════════════════════ 3 Loki
_loki = (
    box(20, 30, 140, 50, 'Writes', '') + box(20, 120, 140, 50, 'Distributor', 'validate, shard') + box(20, 210, 140, 50, 'Ingester', 'WAL, chunks')
    + box(560, 30, 160, 50, 'Reads', '') + box(560, 120, 160, 50, 'Query frontend', 'split, retry') + box(560, 210, 160, 50, 'Querier', 'LogQL, dedup')
    + box(270, 150, 180, 60, 'Backend', 'ruler, compactor, scheduler') + box(270, 270, 180, 50, 'Object storage', 'chunks + index')
    + arrow(90, 80, 90, 118) + arrow(90, 170, 90, 208) + arrow(160, 245, 268, 285)
    + arrow(640, 80, 640, 118) + arrow(640, 170, 640, 208) + arrow(560, 245, 452, 290) + arrow(558, 225, 162, 225, 'recent data', dy=-8)
    + arrow(360, 210, 360, 268))
L.append(dict(
    id='g-4', dot='3', part='G1', nav='Logs with Loki', h1='Logs with Loki and LogQL',
    meta=meta('Signals', 'Chapter 4', 'POC 26'),
    learn=['How Loki stores logs: streams, labels and chunks', 'LogQL’s two halves: stream selectors and the pipeline', 'Parsers, typed label filters, line and label formatting', 'Metric queries over logs, including unwrap', 'Loki’s architecture and the label rules that keep it cheap'],
    body=(
        h2('The big picture')
        + p('Loki was built to be the Prometheus of logs: simple ingestion with no parsing at write time, an index of <b>labels only</b>, and everything in object storage. Each entry has a nanosecond timestamp, a label set and the raw line. Every unique label set is a <b>stream</b>; a stream’s lines are batched, compressed and stored as chunks. Labels are the index and the only thing you can use to find chunks.')
        + h2('LogQL')
        + p('A query is a <b>stream selector</b> followed by an optional <b>pipeline</b>. The selector uses Prometheus matchers and must include at least one that doesn’t match empty (<code>{app=~".+"}</code> is fine, <code>{app=~".*"}</code> isn’t). The pipeline runs line by line, left to right, dropping lines as it goes.')
        + code('{component=~".+service"}\n  |= "emailservice"                                  # line filter: cheap, do it first\n  | json                                              # parse JSON into labels\n  | resources_k8s_container_restart_count > 0        # typed label filter\n  | line_format "{{.body}}"                           # rewrite the line\n  | __error__=""                                       # drop lines that failed to parse')
        + table(['Stage', 'Syntax', 'Notes'],
                [['Line filters', '<code>|=</code> <code>!=</code> <code>|~</code> <code>!~</code>', 'A distributed grep, case-sensitive. <code>|= ip("10.0.0.0/8")</code> matches addresses and ranges. <code>| decolorize</code> strips terminal colour codes'],
                 ['Parsers', '<code>json</code>, <code>logfmt</code>, <code>pattern</code>, <code>regexp</code>, <code>unpack</code>', 'json flattens nested keys with <code>_</code> and skips arrays; pattern is <code>&lt;ip&gt; - &lt;_&gt; …</code> for unstructured lines'],
                 ['Label filters', '<code>status >= 500</code>, <code>latency > 250ms</code>, <code>size > 2MB</code>', 'The value’s form sets the type: string, number, duration or bytes. Failed conversions set <code>__error__</code>. Chain with <code>and</code>, <code>or</code>, commas or spaces'],
                 ['Formatting', '<code>line_format</code>, <code>label_format</code>, <code>drop</code>', 'Go templates with <code>.label</code>, <code>__line__</code>, <code>__timestamp__</code>; <code>new=old</code> renames, <code>new="{{.old}}"</code> copies']])
        + h2('Metrics from logs')
        + table(['Kind', 'Functions', 'Example'],
                [['Log range aggregations', '<code>rate</code>, <code>count_over_time</code>, <code>bytes_rate</code>, <code>bytes_over_time</code>, <code>absent_over_time</code>', '<code>sum by (component) (rate({component=~".+service"} |= "error" [1m]))</code>'],
                 ['Unwrapped range aggregations', '<code>sum_over_time</code>, <code>avg_over_time</code>, <code>quantile_over_time</code>, <code>rate_counter</code>…', '<code>quantile_over_time(0.99, {container="web"} | json | unwrap duration_seconds(request_time) [1m]) by (path)</code>'],
                 ['Aggregation operators', '<code>sum</code>, <code>avg</code>, <code>topk</code>, <code>sort_desc</code>…', '<code>topk(10, sum(rate({region="us-west1"}[10m])) by (name))</code>']])
        + h2('Architecture')
        + pic(740, 330, _loki, 'My layout of the book’s architecture figure. The distributor validates and shards streams to ingesters, which keep a WAL and flush chunks to object storage; the query frontend splits queries across queriers, which read recent data from ingesters and older data from storage.',
              'Loki write path: distributor to ingester to object storage; read path: query frontend to querier, reading ingesters and storage; backend services in the middle.')
        + p('Loki runs as one binary, as a simple scalable deployment (read, write and backend targets) or as full microservices. Reads and writes scale independently. The ruler turns LogQL into recording rules and alerts; the compactor applies retention and deduplicates.')
        + deeper('the rules that keep Loki cheap')
        + h2('Labels are locators, not content')
        + table(['Good labels: few values, used to find streams', 'Bad labels: unbounded values'],
                [['namespace, cluster, job, app, instance, filename', 'user ID, trace ID, path, status code, date']])
        + p('A bad label multiplies streams and chunks: twenty namespaces, sixty apps and three clusters is 3,600 streams; add a user ID with fifty thousand values and it is 180 million. Leave those values in the line and extract them at query time with a parser. And filter first: line filters before parsers, because parsing is the expensive step.')
        + p('The LogQL Analyzer on Grafana’s site explains each step of a query on sample lines, in far more detail than <i>Explain query</i> in the editor. LogCLI runs queries from a terminal, including instant metric queries and label statistics.')),
    say='Loki indexes only labels, so a query is a cheap stream selector plus a pipeline that greps, parses and filters lines at read time. I keep labels to low-cardinality locators like namespace, app and cluster, put IDs and paths in the line, filter with |= before parsing, and use unwrap with quantile_over_time when the latency I need only exists in logs.',
    aws='Self-managed Loki on AWS runs in simple scalable mode on EKS with chunks and the TSDB index in S3 and an IRSA role per component. Ship logs with Fluent Bit (the AWS for Fluent Bit image has a Loki output) or the OpenTelemetry collector’s filelog receiver. CloudWatch Logs with Logs Insights is the AWS-native alternative; POC 26 maps three LogQL queries to their Insights equivalents. Grafana Cloud’s AWS integration can forward CloudWatch Logs into Loki with a Lambda or Firehose.',
    iq=[('Your Loki queries are slow and ingestion costs are rising. What would you look at?',
         ['Streams first. The number of active streams per tenant tells me whether a label with too many values has crept in. Typical culprits are request IDs, pod names on very short-lived pods, status codes and paths as labels. I’d move those into the log line and extract them with a parser at query time.',
          'Then query shape. Queries that start with a broad selector and a parser, with no line filter, decompress and parse everything. Adding a <code>|= "error"</code> or <code>|~</code> before <code>| json</code> often makes them an order of magnitude faster. Narrowing the selector with another label (namespace, app) reduces the chunks fetched.',
          'Then the read path: query frontend splitting and caching, enough queriers, and results cache for dashboards that refresh often.',
          'For cost, I’d look at volume by app with <code>sum by (app) (bytes_over_time({…}[1h]))</code>, drop debug logs at the collector, and set retention by stream. Where people derive metrics from logs, I’d move that to emitting the metric directly, which the Prometheus book also recommends.'])],
    quiz=[['What does Loki index?', ['Every word in every line', 'Only the labels of each stream', 'Timestamps only', 'JSON fields'], 1, 'Lines are stored compressed and searched at query time; the index holds labels.'],
          ['Which is a good Loki label?', ['trace_id', 'namespace', 'user_id', 'path'], 1, 'Labels should be low-cardinality locators.']],
    turn='Run POC 26 and write a pipeline that finds 5xx lines from the access logs with the pattern parser and returns only the URI and status with <code>line_format</code>. Then use <code>label_design()</code> on your own log labels.',
    take=['Streams are label sets; labels are the only index.', 'Selector, then line filters, then parsers, then typed label filters.', 'Labels are locators: keep IDs, paths and codes in the line.']))

# ══════════════════════════════════════════════════════════════ 4 Mimir/Prometheus
L.append(dict(
    id='g-5', dot='4', part='G1', nav='Metrics with Mimir', h1='Metrics in Grafana: PromQL in practice, protocols, storage and exemplars',
    meta=meta('Signals', 'Chapter 5', 'POC 20, 21'),
    learn=['How PromQL looks from Grafana’s Explore: builder, code, table view, query types', 'Two PromQL queries every engineer writes: success rate and p95 latency', 'Push and pull protocols: StatsD, OTLP, Prometheus, SNMP', 'Graphite, Prometheus and Mimir storage compared', 'Exemplars: from a metric point to a trace'],
    body=(
        h2('PromQL from Grafana')
        + p('The PromQL itself is covered in depth in the <a href="#m-3q">Prometheus track</a>. This chapter adds how it feels in Grafana. Explore has a <b>builder</b> and a <b>code</b> editor; switching the result to a <b>table</b> shows every series and label, and clicking a value adds it as a filter. A query of type <b>Range</b> draws a graph; <b>Instant</b> returns the latest value; a range vector like <code>x[5m]</code> on its own only works as an instant query.')
        + p('Use <code>$__rate_interval</code> in every <code>rate()</code>: Grafana picks a window at least four scrape intervals long for the current zoom. <i>Explain</i> walks through a query step by step, <i>Kick start your query</i> offers templates, and the <i>Query inspector</i> shows timings and raw data.')
        + h2('Two queries to know by heart')
        + code('# success rate per instance, so one failing pod isn’t hidden by healthy ones\nsum by (instance) (rate(app_frontend_requests_total{status=~"2.."}[5m]))\n/\nsum by (instance) (rate(app_frontend_requests_total[5m]))\n\n# p95 latency\nhistogram_quantile(0.95, sum by (le) (rate(http_server_duration_milliseconds_bucket[$__rate_interval])))')
        + note('Two slips in the chapter', 'The printed success-rate query divides by <code>app_frontend_requests</code> without the <code>_total</code> suffix, which would return nothing; and its first vector-matching example says 31 + 8 = 29 (it is 39). Small, but in an interview “the denominator returns nothing” is exactly the bug you should spot.')
        + p('Prefer percentiles to averages: a p95 of 300 ms means 95% of requests were at least that fast, while an average hides the slow tail that users notice.')
        + h2('Push and pull')
        + table(['Protocol', 'Model', 'Worth knowing'],
                [['StatsD / DogStatsD', 'Push, UDP 8125', 'Fast, no delivery guarantee, no authentication; expose it on localhost. The Prometheus statsd_exporter is a stepping stone to migrate'],
                 ['OTLP', 'Push, gRPC 4317 / HTTP 4318', 'Authentication, acknowledgements, server-side throttling, gzip. The collector accepts almost any input, so it suits a mixed estate'],
                 ['Prometheus', 'Pull, <code>/metrics</code>', 'The app needs no knowledge of who reads it; matches Kubernetes’ liveness and readiness pattern; rich service discovery'],
                 ['SNMP', 'Pull, plus traps that push', 'Since 1988, universal on network hardware; a large attack surface if misconfigured']])
        + h2('Where metrics are stored')
        + table(['', 'Graphite (Whisper)', 'Prometheus', 'Mimir'],
                [['Layout', 'One fixed-size file per series', 'Two-hour immutable blocks: chunks, index, meta.json; a head block with a WAL', 'The same blocks, in object storage'],
                 ['Scale', 'Searching reads every file: heavy disk I/O', 'One node reads and writes; no replication', 'Per-tenant TSDBs on many ingesters; queries split by time across queriers'],
                 ['Durability', 'No built-in redundancy', 'Local disk', 'Replicated writes; the compactor merges duplicates']])
        + p('Grafana Cloud still accepts Graphite data for teams that use it. The rest of the detail on blocks is in <a href="#m-3">the TSDB lesson</a>.')
        + h2('Exemplars')
        + p('An exemplar is a sample trace attached to a metric point. Configure exemplars at collection, turn on the <i>Exemplars</i> toggle in a panel’s options, and stars appear on the graph. Hovering one shows the trace’s span ID and attributes; <i>Query with Tempo</i> opens the trace. It is the quickest route from “p99 jumped” to “this request, in this service”.')),
    say='In Grafana I write PromQL with $__rate_interval, check series in the table view, and choose range or instant query types deliberately. I compute success rates per instance so one bad pod isn’t averaged away, and latency as a histogram percentile. Prometheus pulls, StatsD and OTLP push; Mimir keeps Prometheus’ block format but in object storage with replicated ingestion. Exemplars link a metric point to the trace behind it.',
    aws='Amazon Managed Grafana with an AMP data source gives the same Explore experience; enable SigV4. AMP stores exemplars sent by remote write, so exemplar stars work when your collector forwards them and the trace backend (X-Ray or Tempo) is configured as the exemplar link. CloudWatch metrics are queried at read time through the CloudWatch data source. POC 20 computes these queries by hand; POC 21 shows the block internals.',
    iq=[('Your error-rate panel shows 0.1% but users report many failures. What could be hiding the errors?',
         ['First, aggregation. If the panel sums across all instances, one failing pod among fifty is diluted to 2% of traffic, and if that pod only takes some routes, even less. Splitting by instance, route and status class usually reveals it, which is why the book’s success-rate query groups by instance.',
          'Second, what the metric counts. If errors are measured at the server and the failures happen before it (DNS, load balancer, TLS, timeouts at the client), the server never sees them. Load balancer metrics, client-side metrics or RUM catch those.',
          'Third, the query itself: a status regex that misses some codes, a missing <code>_total</code> so the denominator is wrong, or a <code>rate()</code> window shorter than two scrapes giving gaps. And retries: a client retrying until success makes the server count several attempts, hiding user-visible slowness.',
          'Then I’d align the SLI with the user journey: measure at the edge or the client where possible, and alert on burn rate per journey, not one global average.'])],
    quiz=[['Why use $__rate_interval in Grafana rather than a fixed [1m]?', ['It is faster', 'It always covers enough scrapes for the current zoom and scrape interval', 'It is required by Mimir', 'It disables extrapolation'], 1, 'A fixed window can contain fewer than two samples at some resolutions, producing gaps.'],
          ['What distinguishes Mimir’s storage from a single Prometheus?', ['A different data format', 'The same blocks, but in object storage with replicated, per-tenant ingestion and split queries', 'No index', 'It stores logs'], 1, 'Mimir keeps the TSDB format and scales it horizontally.']],
    turn='In Grafana (any instance), build the success-rate and p95 queries above for a service you have, switch the panel to table view and filter by clicking a label value. If your stack sends exemplars, turn them on and follow one to its trace.',
    take=['Use the table view, the right query type and $__rate_interval.', 'Success rate by instance; latency by histogram percentile.', 'Exemplars connect metrics to traces.']))

# ══════════════════════════════════════════════════════════════ 5 Tempo
L.append(dict(
    id='g-6', dot='5', part='G1', nav='Traces with Tempo', h1='Traces with Tempo and TraceQL, and how context propagates',
    meta=meta('Signals', 'Chapter 6', 'POC 27'),
    learn=['Tempo’s view of a trace, its search modes and the service graph', 'TraceQL: intrinsic and attribute fields, selection, structural operators, aggregates', 'Pivoting between traces, logs and metrics', 'OTLP, Zipkin and Jaeger; W3C traceparent, B3, Jaeger headers and baggage', 'Tempo’s architecture and the metrics generator'],
    body=(
        h2('The big picture')
        + p('Tempo stores traces in object storage and searches them with <b>TraceQL</b>, modelled like LogQL on PromQL. At the version the book covers (2.3), TraceQL selects spans and traces well but analysis is limited; that is changing fast.')
        + table(['Search mode', 'Use'],
                [['TraceQL', 'The default: precise queries'], ['Search (basic)', 'Drop-downs; deprecated from Grafana 10.3'], ['Loki search', 'Find log lines carrying trace IDs, then open the trace'],
                 ['JSON file', 'Import an exported trace, good for sharing and learning the data model'], ['Service graph', 'Services as nodes, calls as edges with rates and latency, errors in red, with RED panels above']])
        + h2('TraceQL')
        + table(['Field kind', 'Examples'],
                [['Intrinsic', '<code>status</code> (error, ok, unset), <code>statusMessage</code>, <code>duration</code>, <code>name</code>, <code>kind</code> (server, client, producer, consumer, internal), <code>traceDuration</code>, <code>rootName</code>, <code>rootServiceName</code>'],
                 ['Span attributes', '<code>span.http.method</code>, set by the application'], ['Resource attributes', '<code>resource.k8s.node.name</code>, describing what produced the span'],
                 ['Either', '<code>.http.method</code>: works, but say <code>span.</code> or <code>resource.</code> for efficiency']])
        + code('{ resource.service.name = "checkout" && status = error }          # spans\n{ .service.name = "frontend" } > { .service.name = "productcatalogservice" }   # direct child\n{ .service.name = "frontend" } >> { .service.name = "cartservice" }   # any descendant\n{ .service.name = "frontend" } ~ { .service.name = "frontend" }     # siblings\n{ status = error } | count() > 10                                   # aggregate per trace\n{ span.http.method = "GET" } | avg(duration) > 20ms')
        + h2('Pivoting')
        + p('From a span, <i>Logs for this span</i> opens Loki filtered by the span’s service name and namespace. In the other direction, services that write trace and span IDs into their logs let Loki link back to Tempo. From a metric, exemplars open a trace. That three-way movement is what makes the stack worth more than its parts.')
        + h2('Context propagation')
        + p('Spans reach the collector separately from each service; what ties them together is the context each service passes in request headers.')
        + table(['Format', 'Header', 'Status'],
                [['W3C Trace Context', '<code>traceparent: 00-{32 hex trace}-{16 hex parent}-{flags}</code> and <code>tracestate</code>', 'Standard since November 2021; flags currently only “sampled”'],
                 ['W3C Baggage', '<code>baggage: k=v,…</code>, percent-encoded, at most 64 members and 8,192 bytes', 'Carries context such as a tenant ID downstream; visible on the wire, so no secrets'],
                 ['Zipkin B3', '<code>X-B3-TraceId</code>, <code>-SpanId</code>, <code>-ParentSpanId</code>, <code>-Sampled</code>, <code>-Flags</code>, or single <code>b3</code>', 'Still common; OTel supports it'],
                 ['Jaeger', '<code>uber-trace-id: trace:span:parent:flags</code>, <code>uberctx-*</code>', 'Deprecated with the Jaeger SDKs']])
        + p('OTel SDKs speak W3C, B3 and Jaeger. AWS X-Ray’s header isn’t in the mainline distribution, which is why AWS ships its own distribution, ADOT. Baggage is the elegant part: a top-level service can pass <code>tenantId</code> so a downstream service can record it in telemetry without adding it to its own data model.')
        + deeper('architecture')
        + h2('Tempo’s architecture')
        + flow([('Distributor', 'routes spans to ingesters by trace ID', 'amber'), ('Ingester', 'groups spans into traces, batches into blocks, writes bloom filters and indexes, flushes', 'amber'), ('Object storage', 'S3, GCS, Azure', 'amber')],
               'Optional metrics generator: receives spans from the distributor and writes service-graph and span metrics to any Prometheus remote-write backend.')
        + p('Reads go through a query frontend that shards queries by block, and queriers that read flushed blocks from storage or recent ones from ingesters. A compactor optimises storage. Like Loki and Mimir, everything scales horizontally.')),
    say='Tempo stores traces in object storage and I search them with TraceQL: intrinsic fields like status and duration, span and resource attributes, and structural operators for parent, descendant and sibling relationships. Traces only work if context propagates, so I standardise on W3C traceparent, use baggage for things like tenant IDs, and link spans to logs and metrics to traces through exemplars. Tempo’s metrics generator turns spans into RED metrics and service graphs.',
    aws='X-Ray is AWS’s trace store, with Application Signals building service maps and SLOs on it; Tempo on EKS with S3 is the self-managed option, and Amazon Managed Grafana can query both. ADOT handles X-Ray’s <code>X-Amzn-Trace-Id</code> alongside W3C so traces survive ALB, API Gateway and Lambda hops; use an X-Ray-compatible trace ID generator when exporting to X-Ray. POC 27 converts headers, enforces baggage limits, evaluates TraceQL structural operators and builds span metrics and a service graph.',
    iq=[('Traces from your checkout flow show up as several disconnected traces. How do you find and fix the break?',
         ['Disconnected traces mean some hop isn’t passing context. I’d look at where the split happens: the first span of each fragment tells me which service started a new trace instead of continuing one.',
          'The usual causes: a service whose HTTP or gRPC client isn’t instrumented, so outgoing calls carry no <code>traceparent</code>; a message queue where context must be put into message attributes and extracted by the consumer; a thread pool or async boundary where the current context isn’t carried over; and mixed formats, such as one service expecting B3 and another sending W3C, or an AWS hop expecting X-Ray headers.',
          'Fixes: instrument the client or add the propagator explicitly; configure composite propagators (W3C plus B3, plus X-Ray on AWS) during a migration; for queues, inject and extract context per message, or use span links when one consumer processes many messages.',
          'Then I’d prevent regressions: a synthetic request in CI that asserts one trace ID across all expected services, and a TraceQL query on root spans from unexpected services as a dashboard panel.'])],
    quiz=[['What does the TraceQL operator >> mean?', ['Greater than', 'Any descendant of the left-hand spans', 'Direct child only', 'Sibling'], 1, '> is direct child, >> any descendant, ~ sibling.'],
          ['Why must baggage never carry secrets?', ['It is encrypted', 'It travels in plain request headers to every downstream service', 'It is limited to 8 bytes', 'Tempo indexes it'], 1, 'Anyone who can see the traffic, and every downstream service, can read it.']],
    turn='Run POC 27 and write the TraceQL for “payment spans with errors under a checkout server span” using <code>structural()</code>. Then generate a <code>traceparent</code>, convert it to B3 and X-Ray, and decide which of your services would need each.',
    take=['TraceQL: intrinsics, span and resource attributes, structural operators, aggregates.', 'Traces exist only through propagation: standardise on W3C, use baggage carefully.', 'Pivot freely: spans to logs, logs to traces, metrics to traces.']))

# ══════════════════════════════════════════════════════════════ 6 Kubernetes and clouds
L.append(dict(
    id='g-7', dot='6', part='G1', nav='Kubernetes and clouds', h1='Collecting from Kubernetes, AWS, GCP and Azure',
    meta=meta('Signals', 'Chapter 7', 'POC 28'),
    learn=['The OpenTelemetry components for Kubernetes and where each must run', 'Kubernetes attributes and how pod association works', 'The two ways to see AWS telemetry in Grafana: query in place or ingest', 'The GCP and Azure data sources and their query languages', 'Performance, cost, limits and security when integrating clouds'],
    body=(
        h2('Kubernetes')
        + table(['Component', 'Collects', 'Run as'],
                [['Kubernetes attributes processor', 'Adds namespace, pod name and UID, start time, deployment and node to every signal', 'Anywhere'],
                 ['Kubeletstats receiver', 'Node, pod, container (and volume) metrics from the kubelet on port 10250', 'DaemonSet'],
                 ['Filelog receiver', 'Container logs from <code>/var/log/pods</code>, with parsers for JSON, regex, CSV, key-value, URIs and syslog', 'DaemonSet'],
                 ['Kubernetes cluster receiver', 'Cluster metrics: pod phases, node conditions, allocatable resources', 'Exactly one instance'],
                 ['Kubernetes objects receiver', 'Any API object, by periodic <code>pull</code> or a <code>watch</code> stream (typically events)', 'Exactly one instance'],
                 ['Prometheus receiver', 'Anything with a scrape config', 'Careful: replicas scrape everything twice'],
                 ['Host metrics receiver', 'CPU, disk, load, filesystem, memory, network; paging and processes off by default', 'DaemonSet; preset scrapes every 10 s, consider 60 s']])
        + p('The Helm chart has presets that wire these up with RBAC: <code>kubernetesAttributes</code>, <code>logsCollection</code>, <code>kubernetesEvents</code>, <code>clusterMetrics</code>, <code>kubeletMetrics</code>, <code>hostMetrics</code>. The attributes processor associates incoming data with a pod by trying sources in order: a <code>k8s.pod.ip</code> resource attribute, then <code>k8s.pod.uid</code>, then the connection’s source IP. It can also copy pod and namespace labels and annotations into attributes, such as an owning team.')
        + h2('AWS: query in place or ingest')
        + table(['', 'CloudWatch data source', 'AWS integration'],
                [['Data lives', 'In AWS; Grafana queries at read time', 'Copied into Grafana Cloud: metrics in Mimir, logs in Loki'],
                 ['Query with', 'The CloudWatch metrics builder (namespace, metric, statistic) and Logs Insights query language', 'PromQL and LogQL'],
                 ['Setup', 'IAM permissions and credentials on the data source; X-Ray trace links; pre-built dashboards', 'Guided: CloudWatch metric scrape jobs (only resources with tags are discovered), logs through a Lambda or Firehose'],
                 ['Trade-off', 'No duplication, but every query is a remote API call (latency and cost)', 'Fast queries and one language; you pay to store a copy']])
        + h2('GCP and Azure')
        + table(['Cloud', 'Data source', 'Query options'],
                [['Google Cloud', 'Google Cloud Monitoring (JWT key or GCE default service account)', 'Metrics builder, Monitoring Query Language, SLO queries'],
                 ['Azure', 'Azure Monitor (client secret)', 'Metrics, Logs with KQL, Traces from Application Insights, Azure Resource Graph across subscriptions']])
        + deeper('choosing well')
        + h2('Four considerations')
        + table(['Concern', 'What to weigh'],
                [['Performance', 'Remote data sources add latency at query time; data in Loki, Mimir or Tempo is closer. Some data sources cache'],
                 ['Cost', 'Shipping and storing a copy, versus API charges per query on the provider’s side'],
                 ['Constraints', 'API rate limits and quotas, soft or hard; check your expected query volume against them'],
                 ['Security', 'Separate data sources and credentials per concern; Private Data Source Connect for data behind a private network']])),
    say='On Kubernetes I run node-scoped receivers (kubelet stats, host metrics, container logs) as a DaemonSet, cluster-scoped ones (cluster metrics, events) as a single instance, and add Kubernetes attributes to everything so signals correlate. For clouds I choose per data set between querying in place, which avoids copies but costs latency and API calls, and ingesting into the same stores as everything else for speed and one query language.',
    aws='On EKS the ADOT collector add-on or the OpenTelemetry Helm chart provides exactly these receivers; give the cluster-level collector a single replica and the node collector a DaemonSet with IRSA. For AWS services, Amazon Managed Grafana’s CloudWatch data source queries in place; when you want AWS service metrics alongside application metrics in AMP, scrape them with the CloudWatch exporter (YACE) or stream them out with CloudWatch metric streams. Container Insights (the CloudWatch Observability add-on) is AWS’s packaged version. POC 28 is the full architecture with a validator.',
    iq=[('You run the cluster receiver in the node DaemonSet and Kubernetes events appear five times each. Why, and what is the right layout?',
         ['The cluster receiver and the objects receiver read cluster-wide state from the API server. Every copy of them sees everything, so a DaemonSet on five nodes produces five copies of every event and cluster metric.',
          'The right layout splits collectors by scope. A DaemonSet for node-scoped data: kubelet stats, host metrics, container log files and OTLP from pods on that node. A single-replica Deployment for cluster-scoped data: the cluster and objects receivers. And usually a gateway Deployment behind a Service for processing, sampling and export, so credentials and fan-out live in one place.',
          'Two refinements. The single cluster collector is a single point of failure for events; Kubernetes restarts it, and a short gap is acceptable, but alert if it stops sending. And if the Prometheus receiver runs in a multi-replica collector, it has the same duplication problem, so shard it or use the operator’s target allocator.'])],
    quiz=[['Where should the kubeletstats receiver run?', ['As a single Deployment replica', 'As a DaemonSet', 'In the gateway', 'Anywhere'], 1, 'It reads the kubelet of the node it runs on.'],
          ['What is the main trade-off of the CloudWatch data source compared with ingesting AWS data?', ['It can’t show logs', 'No duplication, but every query is a remote API call with latency and cost', 'It needs Mimir', 'It only works in us-east-1'], 1, 'Querying in place avoids storing a copy but pays at read time.']],
    turn='Run POC 28 and break the configs on purpose: move <code>k8s_cluster</code> into the node agent, remove the filelog exclude, drop SigV4 from the AMP exporter. Read each error, then decide which AWS data you would query in place and which you would ingest, and why.',
    take=['Node-scoped receivers in a DaemonSet; cluster-scoped receivers in one instance.', 'Kubernetes attributes on every signal make correlation possible.', 'Query in place or ingest: weigh latency, cost, limits and security per data set.']))
