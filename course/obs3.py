# Track 3: Mastering Prometheus, chapters 11-15.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import h2, h3, note, deeper, code, ol
from obs1 import L, meta, box, arrow

# ══════════════════════════════════════════════════════════════ 11 Jsonnet and mixins
L.append(dict(
    id='m-11', dot='11', part='M2', nav='Jsonnet and mixins', h1='Jsonnet and monitoring mixins: configuration you can reuse and override',
    meta=meta('Scaling', 'Chapter 11', 'POC 29'),
    learn=['Why templating YAML goes wrong and what Jsonnet does instead', 'The Jsonnet features you need: locals, hidden fields, self, super and $, imports and +:, comprehensions, functions, errors and asserts', 'Rendering YAML and multiple files', 'What a monitoring mixin is and how to consume one with jsonnet-bundler'],
    body=(
        h2('The big picture')
        + p('Prometheus configuration is YAML, and lots of it: thousands of lines of scrape config and rules files full of repeated label matchers and annotations. Templating YAML with Jinja or Go templates is fragile because whitespace is syntax. <b>Jsonnet</b>, released by Google in 2014 from its internal configuration language, is the Prometheus community’s answer. It is a superset of JSON (any JSON file is valid Jsonnet) with variables, functions, imports and inheritance, and it outputs JSON or YAML.')
        + h2('The language in one table')
        + table(['Feature', 'Syntax', 'Why it matters'],
                [['Variables', '<code>local m = \'env="prod"\';</code>', 'One label matcher, used in every rule'],
                 ['String formatting', '<code>\'%(m)s\' % _config</code>, <code>|||</code> blocks', 'Readable multi-line PromQL with substitutions'],
                 ['Hidden fields', '<code>_config:: {...}</code>', 'Configuration that isn’t emitted; the heart of mixins'],
                 ['References', '<code>self</code>, <code>super</code>, <code>$</code>', 'This object, the object being extended, the outermost object'],
                 ['Inheritance', '<code>base + { ... }</code>', 'Extend an object, overriding fields'],
                 ['Merge override', '<code>field+: [...]</code>, <code>field+:: {...}</code>', 'Add to an inherited field instead of replacing it'],
                 ['Imports', '<code>import \'x.libsonnet\'</code>', 'Libraries by convention end in .libsonnet'],
                 ['Comprehensions', '<code>[r.name for r in rules if r.page]</code>', 'Generate lists and objects; computed keys in brackets'],
                 ['Functions', '<code>local f(x) = ...;</code>', 'Python-style arguments and defaults'],
                 ['Errors and asserts', '<code>name: error \'set me\'</code>, <code>assert std.length(self.rules) > 0 : \'...\'</code>', 'Force overrides; validate inputs']])
        + code("local rules = (import 'base-rules.libsonnet') {\n  _config+:: { selector: 'job=\"checkout\"' },          // override one config value\n  groups+: [{ name: 'extra', rules: [] }],            // append, don't replace\n};\nstd.manifestYamlDoc(rules)                              // render as YAML (use jsonnet -S)")
        + p('Two quirks to remember: output keys come out in alphabetical order, and <code>for</code> must be quoted because it is a keyword. Render files with <code>-o</code> (and <code>-c</code> to create directories), YAML with <code>std.manifestYamlDoc</code> and <code>-S</code>, and many files at once by making the top-level object a map of file names and running with <code>-m</code>. Use <code>jsonnetfmt</code> and <code>jsonnet-lint</code> once a team shares code, and leave real validation to <code>promtool</code>: Jsonnet is not a validation language (look at CUE or Nickel if you need one).')
        + h2('Monitoring mixins')
        + p('Started in 2018 by Tom Wilkie and Frederic Branczyk, the Monitoring Mixins project defines a minimal standard for packaging Prometheus alerts, recording rules and Grafana dashboards together, so that the people who write a piece of software can ship the monitoring for it.')
        + table(['Field', 'Contents'],
                [['<code>prometheusAlerts</code>', 'Alerting rule groups'], ['<code>prometheusRules</code>', 'Recording rule groups'], ['<code>grafanaDashboards</code>', 'A map of file name to dashboard JSON'], ['<code>_config</code>', 'Selectors and thresholds you override']])
        + p('Most users already run one without knowing: kube-prometheus-stack ships the kubernetes-mixin. The author’s complaint is exactly that ignorance, because unknown mixins with wrong selectors give you dashboards and alerts that silently don’t work.')
        + seq([('jb init', 'create jsonnetfile.json'), ('jb install github.com/thanos-io/thanos/mixin@main', 'vendor the mixin and its dependencies, with a lock file'),
               ('thanos.jsonnet', 'import mixin.libsonnet; override selectors; set unused components (store, receive, rule…) to null'),
               ('jsonnet -J vendor -Sm out thanos.jsonnet', 'render alerts, rules and one file per dashboard')])
        + p('The payoff: alerts such as Thanos Query’s gRPC error-rate alert, written by people who know which gRPC codes matter, without you becoming a gRPC expert. That removes some of the unknown unknowns of running other people’s software. Grafana’s jsonnet-libs repository is a good catalogue.')),
    say='Jsonnet is JSON with variables, functions, imports and inheritance, which makes large Prometheus and Grafana configs DRY and reviewable. A monitoring mixin packages alerts, recording rules and dashboards with a hidden _config you override; I vendor mixins with jsonnet-bundler, override selectors and disable what I don’t run, render them myself, and validate the output with promtool in CI.',
    aws='Rendered mixin output goes wherever rules and dashboards go on AWS: alert and recording groups into AMP rule groups namespaces (<code>aws_prometheus_rule_group_namespace</code>), dashboards into Amazon Managed Grafana through the grafana Terraform provider. Run the render in CodeBuild or GitHub Actions and commit the output, so reviewers see the generated YAML diff. POC 29 shows the override pattern in Python and the Terraform that publishes dashboards.',
    iq=[('Your team runs twenty services, each with hand-written, slightly different alert rules. How would you standardise them?',
         ['I’d separate the pattern from the parameters. Most service alerts are the same handful: error-budget burn, latency SLO burn, saturation, and “is it scraping”. Those become one library, as a Jsonnet mixin or a generator, with a <code>_config</code> per service for selectors, SLO targets and owning team.',
          'Each service’s repo or folder then holds only its overrides. Rendering produces plain YAML that goes through <code>promtool check rules</code>, unit tests and Pint in CI, then into the rules backend.',
          'I’d keep an escape hatch: a service can add its own rules alongside the generated ones, but can’t edit the generated ones by hand. Changes to the shared library get reviewed once and roll out to everyone, which is the shift-down idea from the platform book applied to monitoring.',
          'For third-party software I’d use upstream mixins (Kubernetes, Thanos, Redis…) rather than writing alerts from scratch, checking their selectors match how we label things.'])],
    quiz=[['In a mixin, where do selectors and thresholds live?', ['In prometheusAlerts', 'In the hidden _config field', 'In jsonnetfile.json', 'In Grafana'], 1, 'Hidden fields (::) aren’t emitted; consumers override _config to adapt the mixin.'],
          ['What does field+: do in Jsonnet?', ['Deletes the field', 'Merges with the inherited value instead of replacing it', 'Makes it hidden', 'Asserts it exists'], 1, 'For a list it appends, for an object it merges.']],
    turn='In POC 29, use <code>merge()</code> to override the latency SLO and add a team, then generate the dashboard and run the linter. If you have Jsonnet installed, vendor the kubernetes-mixin with <code>jb</code> and render only its alerts.',
    take=['Jsonnet makes config reusable; render it and validate with promtool.', 'A mixin is alerts, rules and dashboards plus a _config you override.', 'Know which mixins you already run, and check their selectors.']))

# ══════════════════════════════════════════════════════════════ 12 CI
L.append(dict(
    id='m-12', dot='12', part='M2', nav='CI pipelines', h1='CI for Prometheus: promtool, amtool and Pint',
    meta=meta('Scaling', 'Chapter 12', 'POC 23'),
    learn=['GitHub Actions vocabulary and running workflows locally with act', 'Validating Prometheus config and rules, and running rule unit tests', 'Validating Alertmanager config and regression-testing routes', 'Linting rules against a live server with Pint, and Pint in pull requests'],
    body=(
        h2('The big picture')
        + p('Prometheus and Alertmanager configuration lives in Git, and code review alone misses things: a typo in a rule, a route added at the bottom that never matches, an alert on a metric that doesn’t exist. CI takes the human error out. The chapter uses GitHub Actions, run locally with <code>act</code>, but the commands are the same in any CI system.')
        + table(['Term', 'Meaning'], [['Workflow', 'Jobs triggered by an event such as a pull request'], ['Job', 'Steps on one runner; jobs run in parallel unless one <code>needs</code> another'], ['Step', 'A shell command or a reusable action'], ['Runner', 'The machine (or container) that executes a job']])
        + h2('Three layers of checks')
        + table(['Check', 'Command', 'Catches'],
                [['Prometheus config', '<code>promtool check config prometheus.yml</code>', 'Invalid YAML and settings'],
                 ['Rule syntax', '<code>promtool check rules rules/&#42;.yaml</code>', 'Bad PromQL, missing fields'],
                 ['Rule behaviour', '<code>promtool test rules tests/&#42;.yaml</code>', 'Alerts that fire at the wrong time or with the wrong labels'],
                 ['Alertmanager config', '<code>amtool check-config alertmanager.yml</code>', 'Invalid routing or receivers'],
                 ['Routing', '<code>amtool config routes test --verify.receivers=pagerduty-devops team=devops environment=production</code>', 'A new route that never matches because an earlier one catches the alert'],
                 ['Rules against reality', '<code>pint lint</code>', 'Metrics that don’t exist, label mismatches, bad annotations, alerts that would have fired constantly']])
        + p('Run the Prometheus and Alertmanager checks inside the official container images so the tool versions match production. The author’s advice applies even if you are the only person changing the files: these steps have saved him repeatedly.')
        + h2('Pint')
        + p('Pint comes from Cloudflare, which runs Prometheus at very large scale and didn’t want its monitoring team to be a bottleneck for every other team’s rules. Its key difference from promtool is that it <b>queries live Prometheus servers</b> while it lints, so it can say “this alert’s metric has had no series for a week”.')
        + ul(['Required labels and annotations, with regexes (anchored, as in Prometheus)', 'A comparison operator in every alert', 'Would this new alert have fired too often recently?', 'External labels used in templates actually exist; no conflicts with alert labels',
              'Template syntax in labels and annotations', 'Aggregations keep the labels routing needs', 'Links in annotations work', 'Range selectors longer than the server’s retention'])
        + code('rule {\n  match { kind = "alerting" }\n  label "severity" {\n    severity = "bug"\n    value    = "(critical|warning|info)"\n    required = true\n  }\n  annotation "summary" {\n    severity = "bug"\n    required = true\n    value    = "[A-Z][^{.]+.\\\\."       # one sentence, no templates\n  }\n}')
        + p('Pint is configured in HCL (<code>.pint.hcl</code>), can be silenced per rule with comments such as <code># pint disable promql/series(probe_success)</code>, and in CI it checks only the files a pull request changes and comments on the exact lines. The mixin conventions it enforces are a severity of critical, warning or info, a one-sentence <code>summary</code>, and a <code>description</code> with templated detail.')),
    say='I put Prometheus config in Git and gate every pull request on promtool check config, check rules and test rules, amtool check-config plus a set of amtool routes tests that pin which receiver each label set reaches, and Pint linting against a live server so rules on non-existent metrics or with missing annotations never merge. That lets teams who aren’t Prometheus experts change alerting safely.',
    aws='Run the same commands in CodeBuild or GitHub Actions using the official Prometheus and Alertmanager images. For Pint against AMP, put a SigV4 proxy (such as aws-sigv4-proxy) in front of the workspace query endpoint. Deploy rules after the checks pass with <code>aws amp put-rule-groups-namespace</code> or Terraform, and the Alertmanager definition with <code>aws amp put-alert-manager-definition</code>. POC 23 contains the workflow, a Pint config, rules, unit tests and an Alertmanager config with SNS receivers.',
    iq=[('What would you put in a CI pipeline for alerting rules, and why each step?',
         ['Syntax first: <code>promtool check rules</code> fails fast on invalid PromQL or YAML. It is cheap and catches typos.',
          'Behaviour next: <code>promtool test rules</code> with input series that model the failure, a gap from a missed scrape, and recovery, asserting the alert fires at the right evaluation time with the right labels and annotations. That protects against someone “tidying” a <code>for</code> duration or a matcher later.',
          'Reality: Pint against a live server, which catches metrics that don’t exist (renamed by an exporter upgrade), label mismatches in vector matching, alerts that would have fired dozens of times last week, and missing <code>severity</code>, <code>summary</code> or <code>runbook_url</code>.',
          'Routing: <code>amtool check-config</code> and route tests that assert which receiver a given label set reaches, so a new route can’t silently swallow alerts meant for another team.',
          'Finally deployment through the pipeline only, so production always matches Git. Each step catches a different class of mistake, and together they let any team contribute.'])],
    quiz=[['What can Pint check that promtool can’t?', ['YAML syntax', 'Whether the queried metrics exist on a live server', 'Alertmanager receivers', 'Go templates'], 1, 'Pint queries real Prometheus servers while linting.'],
          ['What does amtool config routes test --verify.receivers catch?', ['Invalid YAML', 'A label set routing to an unexpected receiver', 'Unreachable SMTP servers', 'Slow notifications'], 1, 'It asserts which receiver a given label set reaches, a regression test for the routing tree.']],
    turn='Copy POC 23’s <code>ci/observability-ci.yml</code> into a repository of your own Prometheus config. Add two more <code>amtool config routes test</code> lines for your most important routes, and one <code>promtool</code> test for your most important alert that includes a missed scrape (<code>_</code>).',
    take=['promtool for config, rule syntax and rule behaviour; amtool for config and routes.', 'Pint lints against live data and comments on pull requests.', 'CI is what makes self-service alerting safe.']))

# ══════════════════════════════════════════════════════════════ 13 SLOs
_burn = (
    '<line class="ln" x1="60" y1="270" x2="720" y2="270"/><line class="ln" x1="60" y1="270" x2="60" y2="30"/>'
    '<text x="720" y="26" text-anchor="end" class="m">under each bar: time to exhaust a 30-day budget</text><text x="70" y="26" class="m">burn rate</text>'
    + ''.join(f'<rect class="fc" x="{x}" y="{270 - h}" width="110" height="{h}" rx="6" style="opacity:{o}"/><text x="{x + 55}" y="{262 - h}" text-anchor="middle" class="b">{lab}</text>'
              f'<text x="{x + 55}" y="290" text-anchor="middle" class="m" style="font-size:12px">{t}</text><text x="{x + 55}" y="{270 - h / 2 + 5}" text-anchor="middle" class="b" style="fill:var(--bg);font-size:12px">{w}</text>'
              for x, h, o, lab, t, w in [(100, 210, .9, '14.4× · page', '~2 days', '5m + 1h'), (250, 120, .75, '6× · page', '5 days', '30m + 6h'), (400, 70, .55, '3× · ticket', '10 days', '2h + 1d'), (550, 30, .4, '1× · ticket', '30 days', '6h + 3d')]))
L.append(dict(
    id='m-13', dot='13', part='M2', nav='SLOs and burn rates', h1='SLOs with Prometheus: recording rules, burn-rate alerts, Sloth and Pyrra',
    meta=meta('Scaling', 'Chapter 13', 'POC 24'),
    learn=['SLIs, SLOs, SLAs, error budgets, and who should set SLOs', 'Request-based and window-based SLOs, with PromQL for both', 'Recording rules for SLOs and the 30-day ratio', 'Multiwindow, multi-burn-rate alerts', 'Sloth and Pyrra, and how their outputs differ'],
    body=(
        h2('The big picture')
        + p('An <b>SLI</b> is a measurement (good events over valid events), an <b>SLO</b> a target for it over a window, and an <b>SLA</b> an SLO with a contract and penalties. The error budget is one minus the objective, and the burn rate is how fast you are spending it. The SRE lessons covered the theory (<a href="#ch-8">SRE chapter 8</a>); this chapter is the Prometheus implementation.')
        + p('Two points of emphasis from the author. SLOs work best set bottom-up by the team that runs the service, signed off by leadership, because missing them must be allowed to redirect work to reliability. And they should be realistic, not aspirational: some teams even schedule outages when they over-achieve, so users don’t come to depend on more than was promised.')
        + h2('Two kinds of SLO')
        + table(['', 'Request-based', 'Window-based'],
                [['Measures', 'Good requests ÷ all requests', 'Good time windows ÷ all windows'],
                 ['Suits', 'Steady traffic; requests that are revenue (payments)', 'Low traffic; “how long were we down” (Prometheus itself)'],
                 ['Weakness', 'Ten requests a minute: one failure is 10%', 'Resolution is the window size; a bad window counts the same however bad'],
                 ['Book’s example', 'A 500 req/s spike in one window among 20 req/min windows needs almost 16 days of normal traffic to get back to 50%', 'The same spike is one bad window: 15 good windows (3.75 h) restore 95%']])
        + code('# request-based latency SLI: share of requests answered within 100 ms\nclamp_min(sum without (pod, instance) (increase(prometheus_http_request_duration_seconds_bucket{le="0.1"}[5m])), 1)\n/ ignoring (le)\nclamp_min(sum without (pod, instance) (increase(prometheus_http_request_duration_seconds_bucket{le="+Inf"}[5m])), 1)\n\n# window-based: each 5-minute window is good (1) or bad (0), averaged over 30 days\navg_over_time((slo:sli_success:ratio5m >= bool 0.999)[30d:5m])')
        + p('<code>clamp_min(…, 1)</code> stops endpoints with no traffic from producing missing results; the book admits the edge case where a single slow request still scores 100%. The window-based version leans on <code>bool</code>, which turns a comparison into 0 or 1, and a subquery.')
        + h2('Recording rules first')
        + p('Use one series name per kind of value and labels to tell SLOs apart, for example <code>slo:sli_error:ratio_rate5m{service="checkout", slo="availability"}</code>. The 30-day value is <code>sum_over_time(…5m[30d]) / count_over_time(…5m[30d])</code>, deliberately the same formula Sloth and Pyrra use.')
        + h2('Alerting on burn rate')
        + pic(760, 300, _burn, 'My chart of the Site Reliability Workbook table the book reproduces. Each bar is a burn-rate threshold, its short and long windows, and how quickly it would exhaust a 30-day budget.',
              'Four burn-rate thresholds: 14.4x with 5m and 1h windows pages, 6x with 30m and 6h pages, 3x with 2h and 1d tickets, 1x with 6h and 3d tickets.')
        + p('Alerting when the SLO is already broken is too late. Alert on burn rate instead, and require <b>both</b> a long and a short window to exceed it: the long window makes the alert significant, the short one makes it stop soon after the problem does.')
        + note('A correction to the book', 'The printed example compares <code>slo:sli_success:ratio5m</code> with <code>14.4 * 0.001</code>. A success ratio sits around 0.999, so that alert would always fire. Burn-rate alerts compare the <b>error</b> ratio with burn × (1 − objective), which is what Sloth generates and what POC 24 emits and tests.')
        + deeper('Sloth and Pyrra')
        + h2('Generating it all')
        + table(['', 'Sloth', 'Pyrra'],
                [['Model', 'CLI that writes rule files; the maintainer considers it finished', 'Long-running service beside each Prometheus with a web UI; also has <code>generate</code>'],
                 ['Spec', '<code>error_query</code> and <code>total_query</code> with <code>{{.window}}</code>; <code>raw.error_ratio_query</code> for window-based', 'Kubernetes-style <code>ServiceLevelObjective</code>; native latency indicator with <code>success</code> and <code>total</code> metrics and a <code>grouping</code>'],
                 ['Output', '17 rules in 3 groups, including the objective as a series; windows 5m, 30m, 1h, 2h, 6h, 1d, 3d, 30d', 'Over a dozen rules; only plain selectors allowed, so no <code>clamp_min</code> or <code>without</code>'],
                 ['Gotcha', 'Page vs ticket naming takes explaining', 'Burn windows assume a 28-day period: 32m, 1h4m, 2h9m, 6h26m, 1d1h43m, 4d6h51m']])
        + p('The book counts more than 80% fewer lines with Pyrra than writing the rules by hand. Either tool is a good choice; the point is that every team gets the same reviewed rules.')),
    say='I define SLIs as good over valid events in recording rules with consistent names and labels, compute the 30-day ratio from the 5-minute one, and alert on burn rate with paired windows: 14.4× over five minutes and an hour, and 6× over thirty minutes and six hours, page; 3× and 1× open tickets. Window-based SLOs, with bool and a subquery, suit low-traffic services. In practice I generate it all with Sloth or Pyrra so every team gets the same rules.',
    aws='Load generated SLO rules into an AMP rule groups namespace and route <code>severity=page</code> and ticket alerts to different SNS topics through the AMP Alertmanager; show budget remaining in Amazon Managed Grafana. For services instrumented with CloudWatch Application Signals, CloudWatch SLOs offer burn-rate alarms natively. POC 24 generates the rules, simulates outages and slow burns, and has Terraform for the AMP namespace and alert routing.',
    iq=[('Why multiwindow, multi-burn-rate alerts rather than “error rate above 0.1% for five minutes”?',
         ['A fixed threshold on a short window has two problems. It pages on brief blips that barely touch the budget, so people learn to ignore it, and it can miss a slow, steady burn that exhausts the budget in a week without ever crossing the threshold for long.',
          'Burn rate normalises errors against the budget. A 14.4× burn spends 2% of a 30-day budget in an hour, worth waking someone; a 1× burn spends it exactly over the month, worth a ticket.',
          'Using two windows per condition solves the other half. The long window (one hour) says the problem is significant, the short one (five minutes) says it is still happening, so the page stops within minutes of recovery instead of an hour later.',
          'Two page conditions catch fast and medium burns, two ticket conditions catch slow ones. In POC 24’s simulation, a full outage pages within a couple of minutes, three minutes of 10% errors pages nobody, and a steady 4× burn opens a ticket but never pages.'])],
    quiz=[['In a 14.4× burn-rate alert with 5m and 1h windows, what is the short window for?', ['Detection speed', 'Making the alert stop soon after the problem ends', 'Reducing cost', 'Counting requests'], 1, 'The long window gives significance; the short one confirms the burn is still happening, so it resets quickly.'],
          ['Which SLO type suits a service that gets ten requests a minute?', ['Request-based', 'Window-based', 'Neither', 'Latency only'], 1, 'One failed request out of ten is a 10% error rate; windows weight time instead of requests.']],
    turn='Add a third SLO to POC 24’s <code>slo.yml</code> for a low-traffic admin API, regenerate, and write a window-based rule for it with <code>window_based_rule()</code>. Then explain to yourself why the test <code>test_a_brief_blip_pages_nobody</code> passes.',
    take=['SLI in recording rules, 30-day ratio from the 5-minute one.', 'Page on fast burn confirmed by two windows; ticket on slow burn.', 'Generate rules with Sloth or Pyrra; compare error ratios, never success ratios.']))

# ══════════════════════════════════════════════════════════════ 14 OpenTelemetry and beyond
L.append(dict(
    id='m-14', dot='14', part='M2', nav='OpenTelemetry and beyond', h1='OpenTelemetry, and the signals Prometheus doesn’t cover',
    meta=meta('Scaling', 'Chapters 14–15', 'POC 27, 28'),
    learn=['What OpenTelemetry is: specification, API, SDKs, semantic conventions and OTLP', 'The collector’s receivers, processors and exporters, core and contrib', 'Scraping Prometheus metrics with the collector, and pushing OTLP into Prometheus', 'Logs, traces and exemplars: where metrics stop being enough'],
    body=(
        h2('OpenTelemetry in one picture')
        + p('OpenTelemetry (OTel) is not a program you run; it is a <b>specification</b>. It came from a rare event: two competing projects, Google’s OpenCensus (2017) and the CNCF’s OpenTracing (2016), merged in 2019 instead of becoming the fifteenth competing standard in the xkcd strip the book reprints.')
        + table(['Part', 'For'],
                [['API', 'People writing OTel SDKs'], ['SDKs', 'Application developers instrumenting code'],
                 ['Semantic conventions', 'Everyone: standard names for metrics, spans and attributes, so <code>http.server.request.duration</code> means the same thing in every service. The author’s favourite part'],
                 ['OTLP', 'A separate protocol spec for sending all three signals over gRPC (preferred) or HTTP']])
        + p('Many teams still use Prometheus client libraries for metrics, partly because OTel’s model differs: an OTel “counter” need not be monotonic. In the collector a Prometheus counter becomes a <b>Sum</b>, a gauge a <b>Gauge</b>, and labels become <b>data point attributes</b>.')
        + h2('The collector')
        + flow([('Receivers', 'push (OTLP) or pull (prometheus receiver)', 'ember'), ('Processors', 'filter, transform, enrich, batch; optional', 'ember'), ('Exporters', 'Prometheus remote write, OTLP, vendors', 'ember')],
               'One pipeline per signal. Core releases are minimal; contrib has dozens of components; the builder makes a custom binary with only what you need.')
        + p('The <code>prometheus</code> receiver accepts a normal <code>scrape_configs</code> block, service discovery included. The collector exposes its own metrics on port 8888.')
        + h2('OTLP into Prometheus')
        + p('From 2.47, Prometheus can receive OTLP with <code>--enable-feature=otlp-write-receiver</code>; the collector’s <code>otlphttp</code> exporter points at <code>http://prometheus:9090/api/v1/otlp</code> and adds <code>/v1/metrics</code> itself. The author’s caution: the <code>up</code> series you see then comes from the collector’s own scrape, not from Prometheus, so it says nothing about whether delivery works. Have Prometheus scrape the collector and watch <code>otelcol_exporter_send_failed_metric_points_total</code>, and ask whether mixing push and pull is worth it; Prometheus is still pull-first.')
        + deeper('chapter 15: beyond Prometheus')
        + h2('What metrics can’t do')
        + p('Observability is about unknown unknowns. Metrics must be defined before you need them, so some questions will always lack a metric. Logs and traces fill the gap.')
        + tiles([('Logs', 'The oldest and most accessible signal and the worst signal-to-noise. Mostly unstructured; JSON is hard to read; logfmt (key=value, used by Prometheus itself) is the compromise. Don’t derive metrics by parsing logs: formats change and the parsing breaks silently. Emit the metric.', 'ember'),
                 ('Traces', 'The newest core signal and the best signal-to-noise, once sampled: keep 1% of normal requests, half of slow ones and all errors. Because they are sampled they can’t replace metrics’ complete view; they add the detail.', 'rust'),
                 ('Exemplars', 'With <code>--enable-feature=exemplar-storage</code>, a sample can carry the trace ID of a request it counted, so Grafana can jump from a latency spike straight to an example trace.')])
        + p('The glue is consistent metadata: if metrics say <code>app="servicex"</code>, logs must not say <code>app="service-x"</code>. Grafana’s Loki (“like Prometheus, but for logs”: labels, a WAL, LogQL, object storage, a single-binary mode) and Tempo (TraceQL) were built to share Prometheus’ label model; with Mimir and Grafana they form the LGTM stack. The author runs Loki at several hundred thousand lines a second. The Grafana track of this course covers that stack in depth.')),
    say='OpenTelemetry is a vendor-neutral specification: APIs, SDKs, semantic conventions and the OTLP protocol, with a collector that receives, processes and exports all three signals. I scrape Prometheus metrics with the collector’s prometheus receiver or remote-write from it, and I’m careful with OTLP push into Prometheus because the up series no longer tells you delivery works. Metrics can’t answer every question, so I add logs and sampled traces with shared labels, and exemplars to jump from a metric to a trace.',
    aws='AWS Distro for OpenTelemetry (ADOT) is AWS’s supported collector and SDKs: OTLP in, Prometheus remote write with SigV4 to AMP, <code>awsxray</code> to X-Ray, <code>awscloudwatchlogs</code> to CloudWatch Logs, installed on EKS as an add-on. X-Ray propagates its own header, which ADOT’s SDKs handle alongside W3C. CloudWatch Application Signals builds service maps and SLOs on top. POC 28 is a full ADOT architecture for EKS with a validator; POC 27 covers propagation, sampling and TraceQL.',
    iq=[('An application team wants to switch from the Prometheus client library to the OpenTelemetry SDK for metrics. What would you tell them?',
         ['It is a reasonable direction because the SDK gives one API for metrics, traces and logs, semantic-convention names, and exemplars linking metrics to traces. But I’d point out the practical differences before they start.',
          'Collection changes from pull to push unless they keep a Prometheus exporter in the SDK. With OTLP push they lose the free <code>up</code> series, so we need another way to know a service stopped reporting: alert on the absence of its metrics, and monitor the collector’s send failures.',
          'Names and types change. OTel names use dots and units (<code>http.server.request.duration</code> in seconds); converted to Prometheus they gain suffixes such as <code>_seconds</code> and <code>_total</code>. Every dashboard, recording rule and alert that uses the old names needs migrating, and histograms may become exponential histograms, which the backend must support.',
          'So I’d suggest running both for a while, renaming in dashboards and rules through a mixin or generator, and agreeing semantic conventions across teams first, since consistency is the real win.'])],
    quiz=[['Which part of OpenTelemetry standardises attribute and metric names?', ['OTLP', 'Semantic conventions', 'The collector', 'The API'], 1, 'Semantic conventions define names and meanings so every service reports the same way.'],
          ['When the collector pushes OTLP into Prometheus, why is the up series misleading?', ['It is always 0', 'It comes from the collector’s own scrape of its targets, not from delivery to Prometheus', 'Prometheus doesn’t create it', 'It counts traces'], 1, 'It says the collector scraped; it doesn’t say the push to Prometheus succeeded.']],
    turn='Read POC 28’s <code>gateway.yaml</code> and trace one span from the node agent to X-Ray and the span metrics it produces to AMP. Then run POC 27 and convert a W3C <code>traceparent</code> into an X-Ray header with <code>to_xray()</code>.',
    take=['OTel is a specification; semantic conventions and OTLP are its most useful parts.', 'The collector is receivers, processors and exporters; scraping Prometheus is a receiver like any other.', 'Logs and traces cover what metrics can’t; shared labels and exemplars connect them.']))
