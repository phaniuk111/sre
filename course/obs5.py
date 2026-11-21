# Track 4: Observability with Grafana, chapters 8-15, plus cards, drills and the AWS table for tracks 3 and 4.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import h2, h3, note, deeper, code, ol
from obs1 import box, arrow
from obs4 import L, meta

# ══════════════════════════════════════════════════════════════ 7 Dashboards
_dash = (
    '<rect class="pn" x="20" y="20" width="720" height="300" rx="10"/>'
    + ''.join(f'<rect class="fc" x="{x}" y="40" width="160" height="70" rx="8" style="opacity:{o}"/><text x="{x + 80}" y="68" text-anchor="middle" class="b" style="fill:var(--bg)">{t}</text><text x="{x + 80}" y="92" text-anchor="middle" style="fill:var(--bg);font-size:12px">{s}</text>'
              for x, o, t, s in [(40, .95, 'Traffic', 'req/s + sparkline'), (215, .85, 'Errors', '% · red above budget'), (390, .75, 'Latency p95', 'vs SLO target'), (565, .65, 'Saturation', 'gauge')])
    + '<rect class="pn" x="40" y="125" width="685" height="80" rx="8"/><text x="382" y="170" text-anchor="middle" class="m">breakdown: requests by status, full width</text>'
    + ''.join(f'<rect class="pn" x="40" y="{y}" width="685" height="26" rx="6"/><text x="56" y="{y + 18}" class="b" style="font-size:13px">▸ {t}</text>' for y, t in [(220, 'Checkout team — checkout, cart  (collapsed: queries run only when opened)'), (254, 'Payments team — payment'), (288, 'Platform — ingress, DNS')]))
L.append(dict(
    id='g-8', dot='7', part='G2', nav='Dashboards', h1='Dashboards with a purpose',
    meta=meta('Running it', 'Chapter 8', 'POC 29'),
    learn=['Building and improving a first panel: rate, legend, title, description, query type', 'What every panel can configure: units, thresholds, overrides, value mappings', 'Three questions that give a dashboard its purpose, per persona', 'Layout and technical techniques that reduce cognitive load', 'Folders, tags and permissions; the Steven case study'],
    body=(
        h2('From a query to a useful panel')
        + p('The chapter’s first dashboard shows why the defaults aren’t enough. Adding <code>app_frontend_requests_total{target="/api/cart"}</code> from Explore gives an ever-rising line with an unreadable legend and a meaningless title. Four edits make it useful: wrap it in <code>rate(…[$__rate_interval])</code> (Grafana even suggests it), set the legend to <code>{{method}}</code>, give it a title that says it is a rate and a description that says what to look for, and set the query type to Range only so instant points don’t appear on a time series.')
        + h2('What a panel can configure')
        + table(['Option', 'Use'],
                [['Title and description', 'Say what it shows and what to do about it; the description appears behind an <i>i</i> icon'], ['Legend', 'Readable series names, and click to filter'],
                 ['Standard options', 'Unit, min and max, decimals, display name, colour scheme'], ['Thresholds', 'Colour by value: green, orange, red'],
                 ['Overrides', 'Per-series formatting'], ['Value mappings', 'Turn values, ranges or regex matches into text or colours: 0 → Down'],
                 ['Visualisation', 'Time series, Stat, Gauge, Bar chart, Table, Logs… <code>play.grafana.org</code> shows them all with real data']])
        + h2('Give the dashboard a purpose')
        + p('Three questions: <b>who</b> is the audience, <b>what</b> do they need, and <b>where</b> will they view it (a wall screen, a laptop, a phone, an emailed PDF)? The personas answer differently.')
        + table(['Persona', 'Needs', 'Where'],
                [['Diego Developer', 'Traffic through his services; deep detail on errors and bugs', 'Laptop'], ['Ophelia Operator', 'Problems as they happen, clear colours, readable at a glance', 'Wall screen, and laptop when investigating'],
                 ['Steven Service', 'The whole system, and who can fix a problem', 'Laptop'], ['Pelé Product', 'Usage by feature and device, exportable to a spreadsheet', 'Laptop'],
                 ['Masha Manager', 'Aggregated trends, recovery rates, capacity', 'Laptop, plus scheduled PDF reports']])
        + h2('Layout')
        + pic(760, 340, _dash, 'My sketch of the layout the chapter arrives at for Steven: key indicators first, left to right; a breakdown underneath; detail in collapsed rows, one per owning team, each opening with how to reach that team.',
              'Dashboard layout: four stat tiles for traffic, errors, latency and saturation; a full-width breakdown panel; three collapsed team rows.')
        + ul(['A short top title, and a description saying how to use the dashboard and who it is for.', 'Key indicators first, top left, as Stats with sparklines.', 'A grid that leads the eye; similar visualisations grouped together.',
              'Don’t cram: link to other dashboards instead. Transparent panels for breathing space.', 'Rows to group related panels; collapsed rows don’t run their queries until opened, which also makes the dashboard faster.'])
        + h3('Technical habits')
        + ul(['Save often, export JSON, and write meaningful change messages; versions can be compared when something breaks.', 'Use variables instead of hard-coded values, so the dashboard keeps working as systems are added.',
              'Default to a relative time range such as <code>now-15m</code>.', 'Transformations reshape data for display; annotations mark deployments and other events on every graph.'])
        + deeper('organising dashboards, and the case study')
        + h2('Folders, tags and permissions')
        + p('Folders group dashboards and are the boundary for permissions. Tags make related dashboards easy to find. Permissions can be given to users or teams, view-only for people who don’t need to edit, and folders can be hidden on a need-to-know basis.')
        + h2('Case study: a dashboard for Steven')
        + seq([('Requirement', '“An overall view that helps me see the wider picture, and who can solve a problem. On my computer.”'), ('Break it down', 'A top-level view, problem indicators, more detail on demand, help identifying who to call'),
               ('Research', 'The OpenTelemetry demo’s architecture diagram, conversations with Diego, and a scrapbook dashboard of interesting panels'),
               ('Choose metrics', 'The four golden signals: latency, traffic, errors, saturation (RED and USE are in the next lesson)'),
               ('First row', 'Stats with timelines, most important on the left; gauges for saturation; thresholds, overrides and mappings to draw the eye'),
               ('Detail', 'A collapsed row per team that starts with a text panel of contacts and how to engage them; tables with colour coding; links to support pages')])
        + p('It takes several iterations, and more than telemetry goes into it. That is the point: a dashboard is built for a person and a question.')),
    say='Before building a dashboard I ask who it’s for, what question it answers and where they’ll look at it. Then key indicators go first as Stats with sparklines, detail sits in collapsed rows, every panel has a unit and a description, values come from variables, rates use $__rate_interval, and deployments show as annotations. Dashboards live in team folders, as code.',
    aws='In Amazon Managed Grafana, sign-in comes from IAM Identity Center or SAML, and Grafana teams can be mapped from groups, so folder permissions follow your organisation. Manage dashboards as JSON in Git and publish them with the grafana Terraform provider. CloudWatch dashboards are the AWS-native alternative for AWS service metrics. POC 29 generates a golden-signals dashboard with collapsed team rows, lints it against this chapter’s rules, and publishes it to AMG with Terraform.',
    iq=[('A director asks for one dashboard that shows everything about the platform. How do you respond?',
         ['I’d start by asking what decisions it should support, because “everything” on one screen helps nobody. Usually the director wants to know whether customers are affected, whether things are getting better or worse, and where to invest.',
          'That suggests a top-level dashboard with a handful of indicators: SLO compliance and error budget remaining per critical user journey, incident count and time to restore over the quarter, and maybe cost per request. Each is a Stat with a trend, coloured by thresholds agreed with the teams.',
          'Behind it, links rather than more panels: each SLO tile links to the service’s own dashboard, which the owning team maintains; incident tiles link to the incident tool. Collapsed rows can hold a little more detail without loading by default.',
          'I’d also ask where it will be viewed. If it is a weekly review, a scheduled PDF report may serve better than a live screen. And I’d iterate: show a first version, ask which tiles they actually used, and remove the rest.'])],
    quiz=[['Why put detail panels in collapsed rows?', ['They look tidier only', 'Their queries don’t run until the row is opened, so the dashboard loads faster', 'Grafana requires it', 'To hide them from viewers'], 1, 'Collapsed rows defer their queries as well as reducing clutter.'],
          ['What are the three questions that give a dashboard a purpose?', ['What, when, how much', 'Who is the audience, what do they need, where will they view it', 'Which data source, which panel, which colour', 'Who owns it, who pays, who edits'], 1, 'Audience, requirements and viewing context.']],
    turn='Pick one of your dashboards and run it through POC 29’s <code>lint_dashboard()</code> (export its JSON). Fix the findings, then rewrite its description to say who it is for and what question it answers.',
    take=['Who, what and where come before any panel.', 'Indicators first, detail in collapsed rows, links instead of cramming.', 'Units, descriptions, variables, $__rate_interval and annotations everywhere.']))

# ══════════════════════════════════════════════════════════════ 8 Incidents and alerting
L.append(dict(
    id='g-9', dot='8', part='G2', nav='Incidents and alerting', h1='Incident management with Grafana Alerting, OnCall and Incident',
    meta=meta('Running it', 'Chapter 9', 'POC 23, 24'),
    learn=['Roles before an incident, and the gold–silver–bronze command structure', 'Cutting noise in telemetry and in communication', 'RED, USE, golden signals, Web Vitals, and white- versus black-box monitoring', 'Escalation, communication and blameless post-incident reviews', 'Grafana Alerting, OnCall and Incident in practice'],
    body=(
        h2('Being alerted versus being alarmed')
        + p('Bad incident management is genuinely harmful: stress, burnout, worse. The chapter organises good practice into before, during and after an incident, and draws on the UK government’s emergency response guidance, Atlassian’s incident handbook, ServiceNow’s guide and Google’s SRE books. Frameworks to borrow from include ITIL, Google SRE, NIST and SANS.')
        + h2('Before: roles and structure')
        + tiles([('Commander', 'Has authority, calls people in, signs off customer and leadership communication. Every other role reports to them.', 'cyan'),
                 ('Communications', 'Internal, third-party and customer communication, on a cadence.', 'cyan'), ('Technical lead', 'Directs the investigators and knows who is looking at what.', 'cyan')])
        + table(['Level', 'Who', 'Responsible for'],
                [['Gold · strategic', 'Senior leaders', 'Strategy, resources and specialists, media, legal, shareholders, approving silver’s plans, leading the debrief'],
                 ['Silver · tactical', 'Department managers', 'The tactical plan, documented procedures, customer-communication approach, tools, resourcing, keeping gold informed'],
                 ['Bronze · operational', 'Responders', 'Running the incident, informing silver, finding the cause, fixing it, communicating within the plan, post-incident reports']])
        + p('The gold–silver–bronze structure comes from UK emergency services. Most incident frameworks describe only bronze; agreeing silver and gold responsibilities in advance is what lets a serious incident escalate cleanly.')
        + h3('Cutting noise')
        + ul(['In telemetry: document each service’s critical SLIs, trace calls so service graphs exist, write clear log messages, and don’t flood logs when something fails. AIOps anomaly detection helps but doesn’t replace domain knowledge.',
              'In communication: a named group declares incidents and severities; declaring automatically updates a status page and an incident channel; protected channels between bronze, silver and gold; pre-written status messages.'])
        + h2('During: knowing something is wrong')
        + table(['Method', 'Signals', 'Fits'],
                [['RED', 'Rate, Errors, Duration', 'Request-driven services such as web servers'], ['USE', 'Utilisation, Saturation, Errors (of resources: CPU, memory, I/O, threads)', 'Things that provide resources: storage, a Kubernetes cluster'],
                 ['Golden signals', 'Latency, traffic, errors, saturation; latency distinguishes slow successes from fast errors', 'Either'],
                 ['Core Web Vitals', 'LCP, FID (now INP), CLS from real browsers', 'The user’s experience of a web app']])
        + p('That is <b>white-box</b> monitoring, from inside. <b>Black-box</b> monitoring checks from outside as a user would: synthetic probes (the Prometheus blackbox exporter for HTTP, DNS, TCP, ICMP and gRPC; a third-party service to prove SLA compliance) and real user monitoring. Black-box checks also cover things you don’t control, such as ISPs and DNS, so expect some false positives. Runbooks and a strong post-incident process move an organisation away from a <b>hero culture</b>, where a few people hold everything together at the expense of their health.')
        + h3('Escalation and communication')
        + p('An escalation policy answers: who is paged first (in hours, out of hours, by severity)? Who is next if they don’t answer? Who takes over, and when (duration, severity, time of day)? How is it handed over? What if two incidents run at once? Leadership must make sure juniors know it is fine to escalate, and audit rotas for overload.')
        + p('Communication has three strands: the incident team (one paging channel, the bridge link in every alert, an expected response time, and a recorded timeline); internal stakeholders (a regular cadence, even “still investigating” beats silence); and customers (status page, email, social, SMS, the support portal, with pre-approved messages, including one for “we’re investigating a possible issue”).')
        + h2('After: blameless reviews')
        + p('Blame leads to heavy process, less innovation and people hiding mistakes. A blameless review assumes good intent and keeps accountability without fear of reprimand: open communication, honesty about failure, a detailed timeline from chat and system records, and decisions on improvements.')
        + h2('SLIs, SLOs and SLAs')
        + p('Three to five SLIs per service; RED, USE, golden signals and Web Vitals are good candidates. With an agreed SLI (“errors in a 15-minute period”) and SLO (“no more than 3% of requests in 10 minutes”), writing an alert is just translating the sentence into PromQL or LogQL. SLAs are contractual and built from SLIs and SLOs; keep the SLOs tighter so the SLA is rarely at risk. The <a href="#m-13">Prometheus track</a> covers burn-rate alerting properly.')
        + deeper('Grafana Alerting, OnCall and Incident')
        + h2('Grafana Alerting')
        + p('An alert rule is a query, a <b>reduce</b> step (last, max…), and a <b>threshold</b>. The book’s rule is the percentage of 5xx responses over ten minutes with a threshold of 3, the SLO. States are normal, pending and firing; an <b>evaluation group</b> runs its rules in sequence every minute here, with a five-minute pending period.')
        + note('Don’t evaluate every 10 seconds', 'Every minute is 1,440 queries a day per rule; every 10 seconds is 8,640, six times the load for little benefit. And keep the query window at least as long as the evaluation interval, or minutes go unchecked and intermittent errors hide.')
        + p('Annotations carry a readable summary, a description, a runbook URL and a dashboard link. Labels drive routing. <b>Contact points</b> are named sets of integrations (chat, email, webhooks, Kafka…) with optional notification templates. <b>Notification policies</b> are a tree, like Alertmanager’s, that can match on labels straight from the telemetry, such as <code>service_name</code>, continue to a central team, and apply mute timings. <b>Silences</b> cover maintenance. The admin page exports the Alertmanager configuration as JSON.')
        + h2('Grafana OnCall')
        + p('OnCall adds alert ingestion from 20+ systems and any webhook, <b>alert groups</b> (firing, acknowledged, silenced, resolved) that responders can merge or escalate, Jinja2 templates that parse each source’s payload (grouping ID, auto-resolve), routes to <b>escalation chains</b>, schedules with overrides, a mobile app, and outbound ChatOps and webhooks to ServiceNow, Jira or Zendesk.')
        + table(['Escalation step', 'Effect'],
                [['Wait', 'Pause before the next step'], ['Notify users / from on-call schedule / round robin', 'Page people according to their personal notification rules'], ['Notify Slack channel or user group', 'Broadcast'],
                 ['Trigger outgoing webhook', 'Automation'], ['Continue if time in range / if more than X alerts in Y minutes', 'Conditional escalation'], ['Resolve automatically; repeat (up to 5 times)', 'Finish or loop']])
        + h2('Grafana Incident')
        + p('Declare an incident from Slack and Incident opens a video bridge, updates a status page, records GitHub and Jira context, assigns a commander and investigators, tracks tasks, and builds a timeline of chat, queries, alerts and panels for the review. Its Insights page summarises 90 days of incidents and is meant for silver to review with gold. The machine-learning features include Suggestbot (suggests dashboards from the conversation), OpenAI-written summaries, forecasting, outlier detection, and Sift, which looks for error-log patterns, crashing pods, noisy nodes, throttled containers, recent deployments and slow traces.')),
    say='I prepare for incidents before they happen: clear roles (commander, communications, technical lead), an escalation policy, protected channels and pre-written status messages, with gold, silver and bronze levels agreed for serious incidents. I detect with RED for request-driven services, USE for resources, and black-box probes for the user’s view, alert on a few SLIs per service, and finish with a blameless review built from a recorded timeline.',
    aws='On AWS, AWS Systems Manager Incident Manager provides on-call schedules, escalation plans, engagement by SMS, voice and chat, response plans with runbooks, and a timeline; it is triggered from CloudWatch alarms or EventBridge. AMP’s Alertmanager pages through SNS. Amazon Managed Grafana includes Grafana alerting with contact points such as SNS. CloudWatch Synthetics canaries are the black-box probes, CloudWatch RUM the user’s view. Grafana OnCall and Incident are available in Grafana Cloud.',
    iq=[('How would you run the first 30 minutes of a major customer-facing incident?',
         ['First minutes: acknowledge the page, confirm user impact from SLO dashboards or synthetic checks, and declare an incident with a severity. Declaring early is cheap; it starts the machinery: an incident channel, a bridge, a status-page entry.',
          'Assign roles straight away: a commander who coordinates and decides but doesn’t debug, a technical lead who directs investigators, and a communications lead who owns updates to stakeholders and customers on a fixed cadence. In a small team one person may hold two roles, but say so.',
          'Mitigate before diagnosing: the commander asks “what changed?” (deployment annotations, recent config pushes) and pushes for generic mitigations such as rollback, failover or shedding load, while the technical lead runs parallel hypotheses.',
          'Escalate by policy, not by heroics: if it isn’t mitigated within the agreed time, page the next level and inform silver leadership. Customer communication goes out from pre-approved templates, even if it only says we are investigating.',
          'Throughout, the timeline is recorded automatically from the channel, so the blameless review afterwards has facts rather than memories.'])],
    quiz=[['Which method suits a storage system or a Kubernetes cluster best?', ['RED', 'USE', 'Core Web Vitals', 'DORA'], 1, 'USE describes resources: utilisation, saturation and errors.'],
          ['In the gold–silver–bronze structure, who leads the post-incident debrief?', ['Bronze', 'Silver', 'Gold', 'The customer'], 2, 'The book gives the debrief to the strategic, gold level; bronze completes the post-incident reports.']],
    turn='Write a one-page incident policy for your team: the three roles, your escalation steps with times, the channels and the three pre-written customer messages. Then compare your paging route with POC 23’s Alertmanager config and POC 24’s page/ticket split.',
    take=['Roles, escalation and communication are decided before the incident.', 'RED for requests, USE for resources, black-box for the user’s view.', 'Blameless reviews from a recorded timeline; Grafana Alerting, OnCall and Incident cover detection to review.']))

# ══════════════════════════════════════════════════════════════ 9 IaC
L.append(dict(
    id='g-10', dot='9', part='G2', nav='Automation as code', h1='Automating the observability platform with Helm, Ansible and Terraform',
    meta=meta('Running it', 'Chapter 10', 'POC 28, 29'),
    learn=['Why automate, and the four systems of an observability platform', 'The OpenTelemetry Collector Helm chart: modes, presets, pipelines, connectors, values files', 'The OpenTelemetry and Grafana Agent operators, and Ansible on VMs', 'The Grafana Cloud API and the Grafana API, through Terraform and Ansible', 'Dashboards and alert rules as code'],
    body=(
        h2('Why automate')
        + ul(['Fewer risks from manual steps.', 'Domain experts encode the data architecture, the system architecture and visualisation practice once, and developers use them correctly without becoming experts.',
              'Self-service frees the experts for harder work; a <b>golden path</b> makes adoption quick.', 'Practices scale as the organisation grows, and costs stay attributable.'])
        + table(['System', 'Owned by', 'Automated with'],
                [['Data production', 'Each application team', 'The app’s own tests; schemas validated with JSON Schema'], ['Data collection', 'Platform, observability or SRE team', 'IaC and static analysis'],
                 ['Data storage', 'A vendor, or the collection team', 'IaC for self-hosted; IaC configuration for SaaS'], ['Data visualisation', 'Shared: platform runs Grafana, teams own their dashboards', 'IaC, with tooling given to teams']])
        + h2('The collector’s Helm chart')
        + table(['Mode', 'Runs', 'Presets that belong here'],
                [['<code>daemonset</code>', 'One per node', '<code>logsCollection</code> (with <code>includeCollectorLogs: false</code> to avoid reading its own output), <code>kubeletMetrics</code>, <code>hostMetrics</code>'],
                 ['<code>deployment</code>', 'A fixed number of replicas', '<code>kubernetesEvents</code>, <code>clusterMetrics</code> (single replica)'], ['<code>statefulset</code>', 'Stable identities', 'The same, when you need them'],
                 ['any', '', '<code>kubernetesAttributes</code>']])
        + p('The config block holds receivers, processors, exporters and <b>connectors</b>, which act as an exporter for one pipeline and a receiver for another. The book’s pipeline uses <code>spanmetrics</code> (RED metrics from spans, with dimensions such as HTTP method and status) and <code>servicegraph</code> (metrics describing calls between services) to feed the metrics pipeline from the traces pipeline. Extensions like <code>health_check</code> sit outside pipelines.')
        + code('metrics:\n  receivers: [otlp, spanmetrics, servicegraph]\n  processors: [memory_limiter, filter/ottl, transform, batch]   # name/instance for a second copy\n  exporters: [prometheusremotewrite, logging]')
        + p('A useful Helm habit: split values across files, such as one for the pipeline and one for credentials, and pass several <code>--values</code> flags. The last file wins on conflicts and lists are replaced rather than merged, so arrange them carefully.')
        + h2('Operators and VMs')
        + p('Running <code>helm upgrade</code> for every change means a central system with credentials for every cluster. The <b>OpenTelemetry Operator</b> instead defines collectors as Kubernetes resources, which CI can validate and GitOps can pull from Git into each cluster, handles some upgrades, and above all injects <b>auto-instrumentation</b> into pods through an annotation. Grafana has an Agent chart and an Agent Operator with resources for metrics and logs. On VMs, the collector ships as .deb, .rpm and .apk packages with its config at <code>/etc/otelcol/config.yaml</code>; Grafana maintains an Ansible collection with a <code>grafana_agent</code> role.')
        + deeper('the APIs, Terraform and Ansible')
        + h2('Two APIs')
        + table(['API', 'Manages', 'Key resources'],
                [['Grafana Cloud API', 'The SaaS account', 'Access policies and tokens (keys are deprecated), stacks, plugins, regions'],
                 ['Grafana API', 'Any Grafana, cloud or self-hosted', 'Dashboards and folders (UIDs are global, IDs local), permissions (1 view, 2 edit, 4 admin), search, teams, the whole alerting model']])
        + p('Applications should use <b>service accounts</b>. The Terraform provider covers both APIs: a cloud stack data source, an access policy scoped to a stack with <code>logs:write</code>, <code>metrics:write</code> and <code>traces:write</code>, a token for collectors (best written straight into a secrets manager), and in the instance, folders, dashboards and rule groups.')
        + code('resource "grafana_dashboard" "team" {\n  for_each    = fileset("${path.module}/dashboards", "*.json")\n  config_json = file("${path.module}/dashboards/${each.value}")\n  overwrite   = true\n}')
        + p('Ansible’s Grafana collection manages stacks and dashboards (iterate with <code>with_fileglob</code>), but at the time of writing it didn’t support the new alerting model; Terraform’s <code>grafana_rule_group</code> does. Keep dashboard deployment, owned by teams, separate from infrastructure tooling, owned by the platform team.')),
    say='I treat the observability platform as four systems: production owned by app teams, collection and storage by the platform team, visualisation shared. Collectors deploy through Helm or the OpenTelemetry Operator with node-scoped presets in a DaemonSet and cluster-scoped ones in a single replica; connectors like spanmetrics and servicegraph derive metrics from traces. Grafana itself, access policies, folders, dashboards and alert rules are all Terraform, with dashboards owned by teams in their own folders.',
    aws='Terraform manages the AWS side (AMP workspaces, rule groups namespaces, Alertmanager definitions, the Amazon Managed Grafana workspace and its IAM role) and the grafana provider manages what is inside the workspace. On EKS, the ADOT add-on installs the OpenTelemetry Operator, which can inject auto-instrumentation into pods by annotation. Store collector tokens and Grafana service-account tokens in AWS Secrets Manager. POC 28 has the collector configs; POC 29 has the AMG Terraform with dashboards, folder permissions and an alert rule group.',
    iq=[('How would you let 30 product teams manage their own dashboards and alerts without the platform team becoming a bottleneck or the instance becoming a mess?',
         ['Give each team a folder they own, with edit rights there and view rights everywhere else, managed in Terraform and synced from identity groups. That bounds what they can break.',
          'Give them a paved road: a repository template with dashboards as JSON (or generated from a small library), alert rules as code, and a pipeline that lints dashboards (units, descriptions, variables, rate windows), checks rules with promtool or Pint, and applies with Terraform using a team-scoped service account.',
          'Provide building blocks rather than reviews: a golden-signals dashboard generator, SLO rule generators, and mixins for shared infrastructure, so most teams only fill in parameters.',
          'The platform team owns the Grafana instance, data sources, access policies, contact points and the default notification policy tree, and watches usage dashboards to spot problems. Changes to shared pieces go through the platform repo; changes inside a team folder don’t need us at all.'])],
    quiz=[['What is a collector connector?', ['A database driver', 'A component that exports from one pipeline and receives into another', 'An authentication extension', 'A Helm preset'], 1, 'spanmetrics and servicegraph turn trace pipelines into metric pipelines this way.'],
          ['Why run logsCollection only in daemonset mode?', ['It needs root', 'Each node’s pod logs are only readable on that node', 'It is faster', 'Helm requires it'], 1, 'The filelog receiver reads files on the local node.']],
    turn='In POC 29, add a second team folder and dashboard to <code>terraform/amg.tf</code>, generate its JSON with <code>golden_signals_dashboard()</code>, and run the tests. Then sketch the CI pipeline a team would use to change it.',
    take=['Four systems, different owners: automate each where it lives.', 'Collector modes and presets must match scope; connectors derive metrics from traces.', 'Grafana Cloud and Grafana APIs through Terraform; teams own dashboards in their folders.']))

# ══════════════════════════════════════════════════════════════ 10 Architecture
_patterns = (
    '<text x="20" y="26" class="b">Agentless</text>' + box(20, 40, 150, 46, 'App + SDK', '') + box(260, 40, 130, 46, 'Backends', 'logs · metrics · traces') + arrow(172, 63, 258, 63)
    + '<text x="20" y="126" class="b">Local agent</text>' + box(20, 140, 150, 46, 'App + SDK', '') + box(200, 140, 120, 46, 'Agent', 'same host') + box(350, 140, 130, 46, 'Backends', '') + arrow(172, 163, 198, 163) + arrow(322, 163, 348, 163)
    + '<text x="20" y="226" class="b">Gateway</text>' + box(20, 240, 120, 46, 'Agents', 'many') + box(170, 240, 120, 46, 'Load balancer', '') + box(320, 240, 120, 46, 'Gateways', 'autoscaled') + box(470, 240, 130, 46, 'Backends', '')
    + arrow(142, 263, 168, 263) + arrow(292, 263, 318, 263) + arrow(442, 263, 468, 263)
    + '<text x="130" y="26" class="m" style="font-size:12px">every app knows every backend</text><text x="130" y="126" class="m" style="font-size:12px">apps decoupled from backends</text><text x="130" y="226" class="m" style="font-size:12px">fewer connections, central processing, SNMP</text>')
L.append(dict(
    id='g-11', dot='10', part='G2', nav='Platform architecture', h1='Architecting an observability platform',
    meta=meta('Running it', 'Chapter 11', 'POC 28'),
    learn=['Starting from the problem, and agreeing a data architecture with the organisation', 'Which signal suits which data, and testing organisation-specific fields', 'Data production standards and collection patterns: agentless, agent, gateway, Kubernetes', 'Deployment modes for Loki, Mimir and Tempo, and planning for failure', 'Proofs of concept, RBAC, and sharing telemetry with SIEM and BI'],
    body=(
        h2('Start with the problem')
        + p('The most undervalued step is articulating what the organisation is trying to solve, with leadership: customer-affecting incidents (a compliance, operational and reputational risk), visibility of KPIs, how customers use the product, and the cost to serve them (COGS and OPEX). The answers decide what data you need.')
        + h2('Data architecture')
        + p('Observability systems are data systems, and their data is most valuable when it joins up with the rest of the organisation. Find whoever owns the organisation’s data model. The author’s cautionary tale: months spent arguing whether <code>tenantID</code> and <code>customerID</code> were the same thing, then months of rework in two systems and the logging platform, all avoidable with an owner and early requirements.')
        + p('Translate external requirements into an observability requirements document, in MoSCoW form (must, should, could, won’t). Finance needing cost centres, for example, could be met by putting it on every signal, by requiring an <code>organization.costcenter</code> label on every service, or by a service-to-cost-centre lookup table. Pick one and write it down.')
        + table(['Store', 'Best for'],
                [['Loki log fields', 'String state (error, warn), business fields (service, customer, user), low- to medium-cardinality indexed fields and high-cardinality <b>unindexed</b> ones; links to traces'],
                 ['Prometheus / Mimir', 'Numeric state (records processed), service and host labels, low- to medium-cardinality dimensions such as HTTP method'],
                 ['Tempo spans', 'System state, high-cardinality fields, business attributes such as customer ID, cross-system context'],
                 ['Kubernetes labels and cloud tags', 'Ownership and cost allocation, attached to every signal at collection']])
        + p('Libraries are well tested; your organisation-specific fields, like customer ID, are not, and executives may make decisions on them. Test them like any other output; the book recommends Martin Fowler’s article on domain-oriented observability.')
        + h2('System architecture')
        + p('The standard the book proposes for applications: OpenTelemetry SDK; logs to stdout and stderr; metrics both on a Prometheus endpoint and over OTLP; traces over OTLP to <code>localhost:4317</code> or <code>4318</code>. The Prometheus endpoint is there so the Kubernetes HPA, through the Prometheus adapter, can scale on request rate rather than only CPU, which is the steam-engine governor again: a system that corrects itself.')
        + pic(620, 300, _patterns, 'My summary of the book’s reference architectures. Agentless suits demos; a local agent decouples apps from backends; gateways concentrate connections and processing behind a load balancer.',
              'Three collection patterns: agentless, local agent, and gateway behind a load balancer.')
        + p('For Kubernetes the book combines them: a node agent on every node (OTLP, kubelet, host metrics), a gateway for processing, and a single <b>cluster agent</b> for the Kubernetes API, because any more would duplicate data. State which protocols are preferred and which accepted, set end-of-life dates for the ones you want gone, and keep default ports.')
        + h3('Storage and visualisation')
        + p('The first question is who is responsible: an internal team, or a vendor with a contract (helpful when something goes wrong). If you run it yourself, Loki, Mimir and Tempo each have modes:')
        + table(['Mode', 'Shape', 'Production?'],
                [['Monolithic', 'Everything in one process, scaled by adding copies; read and write can’t scale independently', 'No'], ['Microservices', 'Each component deployed and scaled separately', 'Yes, for Mimir and Tempo'],
                 ['Simple scalable (Loki only)', 'Separate write, read and backend targets', 'Yes, for Loki']])
        + h3('Failure')
        + p('An agent that fails can only be restarted. A pipeline that fails can buffer: in memory with the batch processor, on disk with the file storage extension. Size the buffer from how long an outage you must tolerate and your throughput, and publish that tolerance as an SLI of the collection layer.')
        + deeper('proofs of concept, access and other consumers')
        + h2('Proving a design')
        + p('Production is the real test, so build the path to production early. Before that, use local clusters (k3d, KinD, MicroK8s, minikube; the authors like KinD), Vagrant for VMs, demo applications (the OpenTelemetry demo, AWS’s One Observability Workshop, the simpler mythical-creatures app), and replayed data with k6, Locust, Postman, Insomnia or ghz for gRPC, recorded with Wireshark or Fiddler.')
        + h2('Access')
        + p('Grafana Cloud has organisation roles for billing, stacks, members and support. Inside a Grafana instance there are basic roles (Admin, Editor, Viewer, None for service accounts, and a server-wide Grafana Admin), fixed roles that add specific permissions, and custom roles created through the API or Terraform. Permissions also apply per data source, team, dashboard and folder. In Grafana Cloud, separate parts of the organisation with stacks rather than organisations.')
        + table(['Persona', 'Access'], [['Diego', 'Read everything; edit dashboards and alerts only in his service’s folder'], ['Steven', 'View dashboards; manage on-call schedules and silences'], ['Pelé', 'View dashboards and incident history, plus a limited service account to feed business metrics to BI']])
        + p('Audit powerful provisioning service accounts; let a senior team member manage their own team’s limited account.')
        + h2('Other consumers')
        + p('Logs often feed a SIEM and aggregates a BI platform. Either fork data in the collection pipeline (agree needs to avoid paying to store everything twice) or query Grafana on a schedule, ideally from recording rules that precompute the business metric, such as daily unique logins.')),
    say='I start an observability platform from the business problems and the organisation’s data model, decide which signal carries which field, and publish a production standard: OpenTelemetry SDKs, logs to stdout, metrics on a Prometheus endpoint and OTLP, traces over OTLP. Collection uses node agents, a gateway and a single cluster agent on Kubernetes, with buffers sized from the outage I need to survive; storage runs in microservices or simple scalable mode, or with a vendor; access is least privilege by folder and team.',
    aws='A typical AWS reference: ADOT node agents and a gateway on EKS; metrics to AMP, traces to X-Ray or Tempo, logs to CloudWatch Logs or Loki on S3; Amazon Managed Grafana with IAM Identity Center groups mapped to Grafana teams and folders; cost allocation through EKS pod labels and AWS cost allocation tags; security logs forked to Security Lake or a SIEM in the collector; business aggregates exported from recording rules to S3 for Athena or QuickSight. Separate AMP workspaces or AMG data sources for load-test and CI environments.',
    iq=[('Design the observability architecture for a company moving 200 services onto EKS.',
         ['I’d start with the questions it must answer: customer-impacting incidents, SLOs per user journey, cost per team. That gives the data requirements: every signal carries service, namespace, team and cost centre, from Kubernetes labels at collection, and the organisation’s customer ID on spans and logs, not on metrics.',
          'Production standard for the 200 services: OpenTelemetry SDKs or auto-instrumentation via the operator, logs as JSON to stdout, metrics on a Prometheus endpoint (for HPA) and OTLP, traces over OTLP with W3C propagation and parent-based sampling.',
          'Collection per cluster: ADOT node agents as a DaemonSet (OTLP, kubelet, host, container logs with Kubernetes attributes), one cluster agent for events and cluster metrics, and an autoscaled gateway for tail sampling, span metrics, filtering and export with IRSA credentials, routing spans by trace ID so tail sampling sees whole traces. Disk buffers sized for 30 minutes of backend outage.',
          'Storage: AMP for metrics, X-Ray or Tempo on S3 for traces, CloudWatch Logs or Loki on S3 for logs; Amazon Managed Grafana on top with folder-per-team permissions. Load-test and CI telemetry go to separate workspaces.',
          'Operating it: everything in Terraform and Helm through GitOps; SLO rules generated per service; a platform SLO for the collection layer itself; and usage and cardinality dashboards so we see cost growth before the bill does.'])],
    quiz=[['Why does the book run exactly one cluster agent on Kubernetes?', ['To save licences', 'So data from the Kubernetes API isn’t collected once per node', 'Because DaemonSets can’t reach the API', 'For tail sampling'], 1, 'Cluster-scoped receivers would duplicate every event and metric in each copy.'],
          ['Which deployment mode does the book recommend for Loki in production?', ['Monolithic', 'Simple scalable', 'Microservices', 'Single binary'], 1, 'Simple scalable separates write, read and backend targets; microservices is recommended for Mimir and Tempo.']],
    turn='Write a one-page MoSCoW requirements document for your organisation’s observability data: which fields must appear on every signal, which should, and where each type of field lives. Then check POC 28’s configs against it.',
    take=['Start from the business problem and the organisation’s data model.', 'Put each field in the signal that suits it; test your organisation-specific fields.', 'Agent, gateway and a single cluster agent; buffers sized for failure; least-privilege access.']))

# ══════════════════════════════════════════════════════════════ 11 RUM, profiling, k6
L.append(dict(
    id='g-12', dot='11', part='G2', nav='Frontend, profiles, load', h1='Real user monitoring, continuous profiling and load testing',
    meta=meta('Running it', 'Chapters 12–13', 'POC 30'),
    learn=['What Faro collects and how Frontend Observability is set up', 'Web Vitals and their targets', 'Pivoting from a user session to backend traces and logs', 'Continuous profiling with Pyroscope: top table, flame graphs, eBPF versus SDKs', 'The six kinds of load test, and k6 checks, thresholds, options and life cycle'],
    body=(
        h2('Real user monitoring')
        + p('RUM measures what real users experience in their browsers, all the way through to the backend. Grafana’s version is the open-source <b>Faro Web SDK</b> in your web app, a hosted collector (or your own agent), and a Frontend Observability app with Overview, Errors and Sessions tabs. By default Faro sends Web Vitals, unhandled exceptions, browser details, page URL changes, a session ID and activity traces; it uses opentelemetry-js for tracing. Logs go to Loki and traces to Tempo; the metrics are generated from logs with LogQL.')
        + p('Setting up an app asks for a name, the allowed CORS origins, extra Loki labels and an acknowledgement of the cost, then offers NPM, CDN-with-tracing or CDN-without-tracing snippets.')
        + table(['Web Vital', 'Measures', 'Good'],
                [['LCP · Largest Contentful Paint', 'When the largest visible element has rendered', '≤ 2.5 s'], ['FID · First Input Delay', 'From first interaction to the browser handling it', '≤ 100 ms (replaced by INP, March 2024)'],
                 ['CLS · Cumulative Layout Shift', 'How much visible content moves', '≤ 0.1'], ['TTFB · Time to First Byte', 'Request to first response byte', '≤ 0.8 s'],
                 ['FCP · First Contentful Paint', 'Page start to anything visible', '≤ 1.8 s'], ['INP · Interaction to Next Paint', 'Worst interaction latency over the visit, ignoring outliers', '≤ 200 ms']])
        + p('From the Sessions tab, a session ID opens its own vitals, exceptions and, if the backend is traced, links into the traces and on to backend logs: one user’s experience reconstructed end to end. A session starts when Faro initialises and ends when the visitor leaves (the end event isn’t sent by default). Enhancements, each with configuration effort and some browser overhead: frontend tracing, custom errors, measurements, logs, and events (stored in Loki with <code>kind=event</code>).')
        + h2('Continuous profiling')
        + p('Profiles are the fourth signal: which functions use CPU and memory, sampled continuously (every 15 seconds by default in Pyroscope, with a few percent overhead), so code behaviour can be tied to what users were doing. Pyroscope (founded 2020, acquired 2023, merged with Grafana’s Phlare) uses the same horizontally scalable, object-storage architecture as Loki, Mimir and Tempo. Its query is selection only: a profile type and tags.')
        + tiles([('Top table', '<b>Self</b>: time spent in the function itself. <b>Total</b>: time including everything it calls. High self time is a hot function; high total, low self is a hot path.', 'cyan'),
                 ('Flame graph', 'Depth is the call stack; width is the share of samples. The x-axis is not time. Wide boxes are candidates, but only domain knowledge says whether they are a problem.', 'cyan')])
        + table(['Client', 'Strengths', 'Weaknesses'],
                [['eBPF', 'Whole-node profiles, any language, Kubernetes metadata for free', 'Linux kernel constraints, weak tagging of user code, memory profiles expensive, awkward locally'],
                 ['Language SDKs (Go, Java, .NET, Python, Ruby, Rust, Node.js)', 'Flexible tags, detailed, memory profiles, easy locally', 'Hard across many languages; infrastructure tags by hand. Only Go supports pull'],
                 ['AWS Lambda extension', 'Profiles inside functions: why is it slow, costly or failing?', 'Lambda only']])
        + deeper('load testing with k6')
        + h2('Load testing')
        + table(['Test', 'Load', 'Duration', 'Answers'],
                [['Smoke', 'Minimal', 'Minutes', 'Does it work at all? Run after every deploy'], ['Average load', 'Typical', 'Short', 'How does it behave normally?'],
                 ['Stress', 'Above-average peak', 'Under a day', 'Can it sustain a peak?'], ['Spike', 'Sudden, huge', 'Short', 'What does a surge or attack do?'],
                 ['Breakpoint', 'Ramping up', 'Long', 'Where does it break?'], ['Soak', 'Average', 'Long, e.g. 48 h', 'Leaks and slow degradation']])
        + p('Keep load-test telemetry away from production stacks: it is high volume and low value. Running your own storage in the test environment, with the same dashboards, is an advantage of open-source tooling.')
        + p('k6 came from Grafana’s acquisition of LoadImpact. Tests are JavaScript (without Node modules) run from a CLI that can pause, resume and scale tests, locally, on Kubernetes through an operator, or in Grafana Cloud. A browser module tests real pages.')
        + code("import http from 'k6/http';\nimport { check } from 'k6';\nexport const options = {\n  vus: 100, duration: '30m',\n  thresholds: { http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<200'] },\n};\nexport default function () {\n  const res = http.get('http://www.acme.com');\n  check(res, { 'is status 200': (r) => r.status === 200 });\n}")
        + p('<b>Checks</b> record pass or fail without failing the test; <b>thresholds</b> fail the run, and the book suggests deriving them from your SLOs. The life cycle is init code (once per virtual user), <code>setup()</code> once, the default function per iteration, and <code>teardown()</code> once, skipped if setup failed. From the CLI: <code>k6 run -u 10 -i 20 test.js</code>, or stages such as <code>-s 20s:50 -s 60s:50 -s 10s:0</code>; replace <code>run</code> with <code>cloud</code> to use cloud runners.')),
    say='I measure the user’s side with RUM, judging Web Vitals such as LCP, INP and CLS at the 75th percentile and following a bad session into backend traces. I use continuous profiling to explain why code is slow or expensive: self time for hot functions, total time for hot paths. And I load test with thresholds taken from our SLOs, using smoke tests after every deploy and stress, spike, breakpoint and soak tests before big events, with their telemetry kept out of production.',
    aws='CloudWatch RUM collects Web Vitals, JavaScript errors and sessions and links to X-Ray traces; CloudWatch Synthetics runs scripted canaries. For load tests, k6 on EKS with the k6 operator, Grafana Cloud k6, or the Distributed Load Testing on AWS solution; send their telemetry to a separate AMP workspace. For profiling, run Pyroscope on EKS with the eBPF DaemonSet or language SDKs. POC 30 turns SLOs into k6 thresholds, scores Web Vitals at p75 and computes a top table and flame-graph widths.',
    iq=[('Checkout conversion dropped 5% after a release, but every backend metric looks normal. How do you investigate?',
         ['Normal backend metrics with a drop in conversion points at the client side, so I’d go to real user monitoring first. Compare Web Vitals before and after the release by page and browser: a rise in LCP or INP on the checkout page, or in CLS (a button moving as users tap it), would explain lost conversions without any server error.',
          'Then errors: Faro or CloudWatch RUM shows unhandled JavaScript exceptions by page, browser and version. A new exception in a payment widget on one browser is a classic cause, and invisible to backend metrics because the request is never sent.',
          'Then sessions: follow a few sessions that reached checkout and didn’t complete. Where tracing is on, the session links to backend traces, so I can see whether calls were slow, retried or never made.',
          'If I find a regression, I roll back or fix forward, and add a guard: a Web Vitals threshold in the release pipeline’s synthetic test, and a RUM-based SLO for the checkout journey, so the next one pages instead of showing up in a business report.'])],
    quiz=[['In a flame graph, what does the width of a box represent?', ['Time of day', 'The share of samples spent in that function and its children', 'Memory address', 'Number of calls'], 1, 'Width is proportion of samples; the x-axis is not time.'],
          ['What is the difference between a k6 check and a threshold?', ['None', 'Checks record pass/fail; thresholds fail the whole test run', 'Thresholds are per request', 'Checks only work in the cloud'], 1, 'Thresholds turn SLO-style criteria into a pass or fail result.']],
    turn='Run POC 30. Feed <code>rate_vital()</code> the LCP and INP values from your own site’s RUM (or from a Lighthouse run), and generate a k6 script for a spike test with <code>k6_script(kind="spike")</code>. Which threshold would fail first?',
    take=['RUM measures the user’s experience; Web Vitals are judged at p75.', 'Profiles explain cost and slowness: self time versus total time.', 'Six load test shapes; thresholds from SLOs; keep test telemetry separate.']))

# ══════════════════════════════════════════════════════════════ 12 DevOps + troubleshooting
L.append(dict(
    id='g-14', dot='12', part='G2', nav='DevOps and troubleshooting', h1='Observability across the DevOps life cycle, troubleshooting, and what’s next',
    meta=meta('Running it', 'Chapters 14–15', 'POC 30'),
    learn=['From Agile to DevOps to platform engineering, and why the life cycle is only a tool', 'What Grafana contributes at each phase: code, test, release, deploy, operate, monitor, plan', 'Monitoring third-party platforms: observability, CI, CD, resource and security platforms', 'Preparing data collection and the Grafana stack, and a checklist for debugging each', 'Pitfalls to avoid, and the trends to watch'],
    body=(
        h2('The life cycle, with a caution')
        + p('Iterative methods (RAD, Scrum, XP, FDD) predate the 2001 Agile Manifesto, which values individuals and interactions, working software, customer collaboration and responding to change. DevOps (the first DevOps Days was 2009) brought developers, testers and operators together; Werner Vogels’ 2006 “you build it, you run it” became its slogan. <i>Team Topologies</i> warns of the anti-patterns and cognitive load that follow when that is applied badly. The DevOps life cycle is a useful frame, but it is a tool: don’t value it above the people.')
        + table(['Phase', 'What Grafana and observability contribute'],
                [['Code', 'Instrument (libraries, SDKs, injection at deploy; decide who owns it), plan custom fields so they can be tested, and run a local Grafana stack for instant feedback'],
                 ['Test', 'Monitor the CI platform; k6 end-to-end tests that can rerun at deploy time. Beware Rube Goldberg pipelines of custom CI metrics'],
                 ['Release', 'Show the new version meets its SLOs, ideally under k6 load; release dashboards linking test reports and tickets'],
                 ['Deploy', 'Watch the rollout on dashboards; black-box checks through OnCall; <b>deployment annotations</b> via the API; let the CD job query Loki, Mimir and Tempo and roll back automatically; deploy dashboard changes with Terraform in the same window'],
                 ['Operate', 'SLOs, errors, incidents (integrated with ServiceNow and the like); support teams reconstruct sessions from RUM and traces'],
                 ['Monitor', 'Understand to improve: RUM for usage, metrics plus logs plus traces for slow functions, profiles for why, SLOs for behaviour, infrastructure data for scaling, metrics for long-term trends'],
                 ['Plan', 'How many customers does this affect? How much capacity headroom is left? (k6 spike, stress and breakpoint tests)']])
        + p('The difference between operate and monitor is the aim: operate keeps the system working for customers now; monitor documents how it works so the next plan improves it.')
        + h2('Automated deployment verification')
        + p('Watching a dashboard during a deploy works when deploys are rare. When they are frequent, write it into the pipeline: query the error ratio from logs, confirm logins succeed (tied to a smoke test), check calls to downstream services, and roll back automatically if any check fails. That cuts the time to recover from bad releases and frees engineers during deploys. POC 30 implements the gate.')
        + h2('Monitoring platforms you didn’t build')
        + table(['Platform', 'What to do'],
                [['Observability platform', 'Eat your own dog food: SLIs, SLOs, dashboards, incident process. Use the community OpenTelemetry Collector dashboards. Plan for the SaaS being down: be able to spin up Prometheus or a full stack per cluster (the authors learned this painfully). Control noisy sources: compartmentalise, revoke keys, filter, switch off'],
                 ['CI (GitHub Actions, GitLab, Jenkins, Azure DevOps…)', '“Why did my build fail?”: runner failures and noisy neighbours need platform data. Logs and metrics, no traces needed. DORA metrics need agreed definitions. A separate Grafana stack for CI'],
                 ['CD: push (Jenkins, Actions) and pull (Argo CD, Flux)', 'Annotate every deployment. Pull tools expose Prometheus metrics and events. Push tools that both consume third-party code and hold production credentials are a supply-chain risk worth monitoring closely'],
                 ['Resource platforms (databases, caches, queues, web servers)', 'OpenTelemetry contrib receivers or Prometheus exporters, plus public dashboards. Monitoring a database is not the same as using it as a Grafana data source'],
                 ['Security tools (Falco, OPA, kube-bench, Trivy)', 'Many expose metrics. Share one log pipeline with the security team, and watch it closely']])
        + deeper('chapter 15: troubleshooting and the future')
        + h2('Prepare before you collect')
        + p('The authors repeatedly find agents deployed without thought, sending everything: undefined telemetry and big bills. Plan for what is, not what might be; adding later is easier than removing. Questions first: who the customers are, which log formats exist, where data comes from, which metrics serve SLOs, whether tracing helps, what dashboards need.')
        + table(['Signal', 'Decisions'],
                [['Logs', 'An extensible format; Loki labels chosen for cardinality (extract the rest at query time); which metrics come from logs'],
                 ['Metrics', 'Drop what you don’t need, or just its worst labels; read each protocol’s definitions; protect verbose protocols (limit histogram buckets); add exemplars'],
                 ['Traces', 'Validate span accuracy; sampling, filtering and retention'], ['Libraries and collector', 'Maintained libraries; prove the collector works in your environment, including permissions on the path to production; know its support model']])
        + h2('Debugging checklists')
        + table(['Telemetry missing', 'Grafana misbehaving'],
                [['Collector logs for errors', 'Send test data with curl or Postman straight to the API'], ['Rejections: sample too old, trace too large, rate limited', 'Break big queries down: short ranges, strong filters'],
                 ['Credentials: expiry and scopes', 'Function order matters, as in maths'], ['Ports and protocols on ingest', 'Count data points; cap max data points; raise the minimum interval; group to shrink results'],
                 ['Sampling or redaction changing data', 'Usage Insights: top dashboards, data sources and users with errors'], ['Exporters and the next hop', 'Billing/Usage dashboard for limit rejections; cardinality dashboards'],
                 ['Network: firewalls, network policies', 'Query history to compare attempts']])
        + h2('Pitfalls and trends')
        + ul(['Treat the platform as a product that evolves; requirements from many customers; a 6- and 12-month roadmap.', 'Watch cost at collection, where it is cheapest to fix; fix cardinality early with standards and governance.',
              'Isolate high-load, low-value environments such as performance tests in cheaper, short-lived stacks.', 'Monitor your platform’s usage and your collector estate.'])
        + p('The trends the authors point to: cost reduction (usage dashboards, Adaptive Metrics, Log Volume Explorer), AI (generated panel titles, incident summaries, root-cause analysis after Grafana’s acquisition of Asserts.ai), better developer tooling (a VS Code extension for dashboards), OpenTelemetry maturing into the standard, fleet management for collectors (OpAMP; Grafana Agent Flow, now Grafana Alloy), and platform engineering making observability the default.')),
    say='I use observability at every phase: a local stack while coding, SLO evidence under load at release, deployment annotations and automated verification with rollback at deploy, SLOs and incidents in operate, and usage, profiles and trends in monitor to feed planning. I treat the observability platform itself as a product with SLOs and a disaster plan, and I control cost at collection: plan what you need, drop what you don’t, fix cardinality early, and isolate noisy environments.',
    aws='Automated verification on AWS: CodeDeploy deployment groups with CloudWatch alarms for automatic rollback, or Argo Rollouts analysis runs querying AMP. Post Grafana annotations from CodePipeline or GitHub Actions. Monitor the observability platform itself: AMP and AMG publish usage metrics to CloudWatch, and collectors expose their own metrics. For a SaaS outage, keep a minimal in-cluster Prometheus or a CloudWatch fallback dashboard. Track cost with AMP and CloudWatch usage metrics and cost allocation tags per team.',
    iq=[('Your observability bill doubled in six months while traffic grew 20%. What do you do?',
         ['Find where the growth is before cutting anything. Usage dashboards (Grafana Cloud’s Billing/Usage, or AMP and CloudWatch usage metrics) split it by signal; then by team or service using the labels and cost-allocation tags we require on every signal.',
          'Metrics growth is almost always cardinality: a new label with unbounded values, more histogram buckets, or a new exporter scraping everything. Cardinality dashboards and TSDB status find the label; drop it at the collector, set limits, and fix the instrumentation with the team.',
          'Logs growth is usually debug logs left on, a chatty dependency, or a noisy environment such as load tests sharing the production stack. Log volume by app finds it; drop at the collector and move load tests to their own cheap stack.',
          'Traces: check sampling. Moving from head sampling of everything to tail sampling that keeps errors and slow traces plus a small baseline cuts volume a lot without losing the useful traces.',
          'Then prevent recurrence: governance at collection (limits, required labels, end-of-life for old protocols), cost per team visible on a dashboard, and a review in the platform roadmap. Plan for what is, not what might be.'])],
    quiz=[['What is the main difference between the operate and monitor phases in the book?', ['Different tools', 'Operate keeps the system working for customers now; monitor documents how it works to improve the next plan', 'Monitor is only for managers', 'There is none'], 1, 'Same tools, different aim.'],
          ['What should the observability platform team have for a SaaS outage?', ['Nothing; SaaS has an SLA', 'A tested plan, such as spinning up Prometheus or a full stack in each cluster', 'Daily exports to S3', 'A second vendor contract'], 1, 'The authors advise a simple, tested disaster plan, learned the hard way.']],
    turn='Use POC 30’s <code>verify_deployment()</code> with three checks that matter for one of your services. Then write the disaster plan for your observability backend being down for four hours: what still alerts, who notices, and what you spin up.',
    take=['Observability helps at every phase, not just operate.', 'Automate deployment verification; annotate every deploy.', 'Treat the observability platform as a product: SLOs, a disaster plan, and cost control at collection.']))

# ══════════════════════════════════════════════════════════════ flashcards, drills, AWS table
CARDS = [
    ['Prometheus: what is a series?', 'A metric name plus one unique set of label values, and all its samples. Every new label value is a new series.'],
    ['Prometheus: head block', 'The most recent ~2 hours of samples in memory, with full chunks memory-mapped and every sample also written to the WAL.'],
    ['Prometheus: what is in a block directory?', 'chunks/, index, meta.json and tombstones. Each two-hour block is an immutable, self-contained database.'],
    ['Prometheus: compaction ranges', '2h blocks merged in steps of three (6h, 18h, 54h…) up to 31 days or 10% of retention.'],
    ['Why does scrape jitter cost disk?', 'Delta-of-delta timestamps cost 1 bit when intervals are exact and 16+ bits when they aren’t. Default tolerance 2 ms, up to 1% of the interval.'],
    ['rate vs irate', 'rate: whole window, reset-aware, extrapolated; for alerts. irate: last two samples only; for volatile graphs.'],
    ['group_left', 'Many-to-one matching: many series on the left match one on the right; listed labels are copied from the right, e.g. from an _info metric.'],
    ['and / or / unless', 'and: left with a match on the right. or: left plus unmatched right. unless: left without a match on the right; great for alert suppression.'],
    ['relabel_configs vs metric_relabel_configs vs write_relabel_configs', 'Targets before the scrape; series after the scrape before storage; series before remote write.'],
    ['hashmod relabeling', 'md5 of joined source labels, last 8 bytes mod N, into a label; keep where it equals the shard number.'],
    ['HTTP SD requirements', 'HTTP 200, Content-Type application/json, UTF-8, a list of {targets, labels}.'],
    ['Alertmanager: continue: true', 'After a matching route, keep evaluating its siblings, so one alert reaches several receivers.'],
    ['group_wait / group_interval / repeat_interval defaults', '30s before the first notification; 5m between updates; 4h before re-sending an unchanged group (author prefers 24h).'],
    ['What do Alertmanagers gossip?', 'Silences and the notification log, not alerts. Every Prometheus must send to every Alertmanager; no load balancer.'],
    ['Why last_over_time in an alert?', 'One failed scrape makes the raw selector return nothing and resets the for timer.'],
    ['Federation rule of thumb', 'Only small, aggregated subsets; if it has an instance label, don’t federate it. Use honor_labels: true.'],
    ['HA Prometheus pair', 'Identical replicas differing only in a replica external label; drop it in alert_relabel_configs; dedup in Thanos Query or remote storage.'],
    ['Scrape limits', 'sample_limit, label_limit, label_value_length_limit, label_name_length_limit; checked after metric relabeling; a breach fails the whole scrape.'],
    ['Recording rule naming', 'level:metric:operations, operations newest first, drop _total after rate: job:http_requests:rate5m.'],
    ['GOGC and GOMEMLIMIT', 'GOGC=50 for big servers (less memory, more CPU); GOMEMLIMIT ≈ 90% of available memory to avoid GC-driven OOMs.'],
    ['Node Exporter: memory pressure signal', 'node_pressure_memory_stalled_seconds_total (PSI), not load average or MemFree.'],
    ['Textfile collector safety', 'Alert on node_textfile_mtime_seconds age, or a dead job looks healthy forever.'],
    ['Remote write queue sizing', 'min_shards ≈ samples/s ÷ capacity; capacity ≥ 3 × max_samples_per_send; defaults capacity 2500, batch 500, max_shards 200.'],
    ['Agent mode', '--enable-feature=agent: scrape and remote-write only; no queries, rules or local blocks; WAL keeps ~2h.'],
    ['VictoriaMetrics vs Mimir storage', 'VictoriaMetrics: local/block disks, very efficient. Mimir: object storage, multi-tenant, more resources.'],
    ['Mimir HA dedup', 'HA tracker elects one replica via Consul or etcd; fails over after 30 s of silence, losing that gap.'],
    ['Thanos downsampling', '5m after 40h, 1h after 10 days. Speeds long queries; storage grows because indexes don’t shrink.'],
    ['Thanos Receive hashring', 'Use Ketama consistent hashing; replication factor 3 needs 2 successful writes.'],
    ['Monitoring mixin fields', 'prometheusAlerts, prometheusRules, grafanaDashboards and a hidden _config to override.'],
    ['Pint vs promtool', 'promtool checks syntax and runs unit tests; Pint lints against live Prometheus (missing series, annotations, would-have-fired).'],
    ['Burn-rate pairs', '14.4× on 5m+1h and 6× on 30m+6h page; 3× on 2h+1d and 1× on 6h+3d ticket.'],
    ['Request- vs window-based SLO', 'Request: good/total requests, for steady traffic. Window: good/total windows via bool + subquery, for low traffic.'],
    ['OpenTelemetry’s parts', 'API, SDKs, semantic conventions, and the separate OTLP protocol spec; the collector runs receivers → processors → exporters.'],
    ['Loki stream', 'A unique label set; its lines are batched, compressed into chunks. Labels are the only index.'],
    ['Good and bad Loki labels', 'Good: namespace, cluster, job, app, instance, filename. Bad: user ID, trace ID, path, status code, date.'],
    ['LogQL query anatomy', 'Stream selector, then pipeline: line filters → parsers → typed label filters → formatting.'],
    ['LogQL unwrap', 'Turns a label into a sample: quantile_over_time(0.99, {…} | json | unwrap duration_seconds(latency) [5m]).'],
    ['TraceQL structural operators', '> direct child, >> any descendant, ~ sibling.'],
    ['W3C traceparent', '00-{32 hex trace ID}-{16 hex parent span ID}-{flags, 01 = sampled}.'],
    ['W3C baggage limits', 'At most 64 members and 8,192 bytes, percent-encoded; never secrets.'],
    ['RED vs USE', 'RED (rate, errors, duration) for request-driven services; USE (utilisation, saturation, errors) for resources.'],
    ['Gold, silver, bronze', 'Strategic leaders, tactical managers, operational responders.'],
    ['Dashboard purpose', 'Who is the audience, what do they need, where will they view it.'],
    ['Collector placement on Kubernetes', 'Node-scoped receivers in a DaemonSet; cluster receivers in one instance; processing in a gateway.'],
    ['Collector connectors', 'Export from one pipeline and receive into another: spanmetrics, servicegraph, forward.'],
    ['Loki, Mimir, Tempo deployment modes', 'Monolithic (not prod), microservices (prod for Mimir, Tempo), simple scalable (prod for Loki).'],
    ['Core Web Vitals targets', 'LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, judged at p75.'],
    ['Flame graph width', 'Share of samples in a function and its children; the x-axis is not time.'],
    ['k6 checks vs thresholds', 'Checks record pass/fail; thresholds fail the run. Take thresholds from SLOs.'],
    ['Six load test types', 'Smoke, average, stress, spike, breakpoint, soak.'],
]

DRILLS = [
    ['Explain how a Prometheus query finds data on disk.', ['The selector’s matchers are looked up in each block’s inverted index: one sorted postings list of series IDs per label pair. Prometheus intersects them, starting with the shortest, to get the matching series, then reads only their chunks for the time range, from the head block for recent data and from the blocks overlapping the range for older data.', 'That is why a selective label makes queries fast and a high-cardinality one makes them slow: postings lists become huge and every series means more chunks to decode.']],
    ['How would you make alerting resilient to a Prometheus server failing?', ['Run identical replicas in different zones with a replica external label, both evaluating the same rules and both sending to every Alertmanager. Drop the replica label in alert_relabel_configs so Alertmanager deduplicates.', 'Run Alertmanager as a cluster of two or three in different zones with peering, never behind a load balancer. Add a dead man’s switch: an always-firing alert routed to an external service that pages if it stops arriving.']],
    ['When would you choose Thanos, Mimir, VictoriaMetrics or AMP?', ['Thanos when clusters must stay independent and you want to add components gradually with blocks in object storage. Mimir for central ingestion, multi-tenancy and full PromQL on object storage. VictoriaMetrics for the lowest resource use on local disks. AMP on AWS when you want the Mimir-style model without operating it.']],
    ['Design log collection on EKS.', ['A DaemonSet collector (Fluent Bit or the OpenTelemetry filelog receiver) reads /var/log/pods, excludes its own logs, adds Kubernetes attributes, parses JSON, and sends to a gateway or directly to Loki or CloudWatch Logs with a disk buffer.', 'Loki labels stay low-cardinality (cluster, namespace, app); trace IDs stay in the line with a derived field linking to traces. Debug logs are dropped at collection; retention is set per stream.']],
    ['A trace shows a 2 s gap between two spans. How do you find out what happened?', ['Look at what runs between them: a queue, a thread pool, a lock or an uninstrumented call. Check the parent span’s attributes and events, and the service’s logs for that trace ID in that window.', 'If it recurs, profile the service with Pyroscope around those requests, or add a span around the suspected step. Span metrics by operation will show whether it is a general latency shift or an outlier.']],
    ['How do you stop a high-cardinality metric from taking down Prometheus?', ['Prevent: sample and label limits on every scrape job, review of new metrics in CI, and instrumentation guidance that keeps IDs out of labels.', 'Detect: alerts on head series growth and on scrape failures, and TSDB status for the culprit. Fix: drop the label or metric with metric relabeling, then fix the instrumentation with the owning team.']],
    ['Explain burn-rate alerting to a product manager.', ['We promise that, say, 99.9% of checkouts succeed each month, which allows about 43 minutes’ worth of failures. Instead of alerting on any error, we watch how fast we are using that allowance. If we would use it up in two days, someone is paged; if in ten days, a ticket is opened. Short blips don’t wake anyone, and slow leaks still get fixed.']],
    ['What would you put on a service’s main dashboard?', ['Golden signals first, as Stats with sparklines: traffic, error ratio coloured against the SLO, p95 latency against its target, saturation. A breakdown by status or route underneath. Collapsed rows for dependencies and owning teams with contacts. Variables for environment and namespace, deployment annotations, a description, and a link to the runbook.']],
    ['How do you roll out tail sampling safely?', ['Put it in a gateway tier, after span metrics and service-graph connectors so RED metrics still see 100% of spans. Route spans to gateway replicas by trace ID with the load-balancing exporter so each trace is decided whole.', 'Start with policies that keep all errors and slow traces plus a small baseline, and monitor the collector’s memory and decision latency.']],
    ['How do you make observability self-service for many teams?', ['A paved road: SDK and collector defaults, generated dashboards and SLO rules, mixins for shared infrastructure, team folders and service accounts in Terraform, and CI that lints dashboards and rules. Guard rails rather than reviews: scrape limits, required labels, cardinality and cost dashboards per team.']],
]
DRILLS = [[q, ''.join(f'<p>{a}</p>' for a in ans)] for q, ans in DRILLS]

AWS_ROWS = [
    ['Prometheus storage and query', 'Remote-write to a managed, Cortex-based store; PromQL unchanged', 'Amazon Managed Service for Prometheus', '<a href="#m-9">M9</a>, POC 25'],
    ['Scraping on EKS', 'Prometheus agent, ADOT collector, or the agentless AMP managed collector', 'AMP managed collector, ADOT add-on', '<a href="#m-1">M2</a>, POC 28'],
    ['Discovery of EC2', 'ec2_sd_configs with IAM DescribeInstances; tags to labels with labelmap', 'EC2, IAM (IRSA)', '<a href="#m-4">M4</a>, POC 22'],
    ['Rules and alert routing', 'Rule groups namespaces; managed Alertmanager with SNS receivers', 'AMP, SNS, Incident Manager', '<a href="#m-5">M5</a>, POC 23'],
    ['SLO burn-rate alerts', 'Generated recording and alerting rules; page vs ticket by label', 'AMP rule groups, SNS; CloudWatch Application Signals SLOs', '<a href="#m-13">M13</a>, POC 24'],
    ['Long-term retention', 'AMP storage, or Thanos with S3 and lifecycle rules', 'AMP, S3', '<a href="#m-10">M10</a>, POC 25'],
    ['Dashboards and Grafana alerting', 'Managed Grafana with SigV4 data sources, folders per team, Terraform', 'Amazon Managed Grafana, IAM Identity Center', '<a href="#g-8">G8</a>, POC 29'],
    ['Logs', 'Loki on EKS with S3, or CloudWatch Logs and Logs Insights', 'CloudWatch Logs, S3', '<a href="#g-4">G4</a>, POC 26'],
    ['Traces', 'ADOT to X-Ray, or OTLP to Tempo on S3; X-Ray header alongside W3C', 'AWS X-Ray, ADOT', '<a href="#g-6">G6</a>, POC 27'],
    ['Collector architecture', 'Node DaemonSet, single cluster agent, gateway; SigV4 exporters', 'ADOT, IRSA / Pod Identity', '<a href="#g-11">G11</a>, POC 28'],
    ['Real user monitoring and synthetics', 'Web Vitals at p75, sessions linked to traces; scripted canaries', 'CloudWatch RUM, CloudWatch Synthetics', '<a href="#g-12">G12</a>, POC 30'],
    ['Load testing', 'k6 with SLO thresholds; separate telemetry stack', 'k6 on EKS, Distributed Load Testing on AWS', '<a href="#g-12">G13</a>, POC 30'],
    ['Deployment verification', 'Query telemetry after deploy; automatic rollback; annotations', 'CodeDeploy alarms, Argo Rollouts with AMP', '<a href="#g-14">G14</a>, POC 30'],
    ['Incident response', 'On-call schedules, escalation, timelines', 'AWS Systems Manager Incident Manager', '<a href="#g-9">G9</a>'],
]
