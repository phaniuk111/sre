# Track 3: Mastering Prometheus, chapters 5-10.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import h2, h3, note, deeper, code, ol
from obs1 import L, meta, box, arrow

# ══════════════════════════════════════════════════════════════ 5 Alerting
_tree = (
    box(270, 16, 200, 46, 'route: fallthrough', 'matches everything')
    + box(60, 120, 230, 52, 'slack-devops', 'team = devops · continue')
    + box(450, 120, 260, 52, 'default', 'env=production, team=~devops|sre…')
    + box(60, 230, 230, 52, 'pagerduty-devops', 'environment = production')
    + arrow(330, 62, 200, 118) + arrow(410, 62, 560, 118) + arrow(175, 172, 175, 228)
    + '<text x="380" y="215" class="m" style="font-size:13px">continue: true → also try siblings</text>'
    + '<path class="dash" d="M290 146 L448 146" marker-end="url(#ah)"/>'
    + '<text x="460" y="250" class="b" style="font-size:13px">{production, devops} → pagerduty-devops + default</text>'
    + '<text x="460" y="272" class="b" style="font-size:13px">{testing, devops} → slack-devops</text>'
    + '<text x="460" y="294" class="b" style="font-size:13px">{production, sre} → default</text>')
L.append(dict(
    id='m-5', dot='5', part='M1', nav='Alerting', h1='Alertmanager, and alerts that don’t wake people for nothing',
    meta=meta('Fundamentals', 'Chapter 5', 'POC 23'),
    learn=['Routing trees, matchers, continue, and how to test routes', 'group_by, group_wait, group_interval and repeat_interval, on a timeline', 'Time intervals, receivers, send_resolved and inhibition', 'Alertmanager high availability: what it gossips and what it doesn’t', 'Robust rules: set operators, for durations, _over_time, unit tests'],
    body=(
        h2('The big picture')
        + p('A common misunderstanding is that Prometheus sends notifications. It doesn’t. Prometheus evaluates alerting rules, and when an expression has been true for the rule’s <code>for</code> duration it sends the alert to <b>every</b> Alertmanager it knows, re-sending while it fires. Alertmanager owns everything after that: routing, grouping, inhibition, silencing and delivery.')
        + h2('Routing')
        + p('The only mandatory parts of an Alertmanager config are a top-level <b>route</b> and a <b>receiver</b>. The top route matches every alert and can’t have matchers; everything else is a tree of sub-routes underneath it. Matchers look like PromQL: <code>=</code>, <code>!=</code>, <code>=~</code>, <code>!~</code>. Quoting the value with double quotes is optional; single quotes become part of the value, a gotcha the book calls out.')
        + pic(720, 310, _tree, 'My drawing of the chapter’s routing example. The most specific matching route wins; a parent is used when none of its children match; continue makes evaluation carry on to the next sibling.',
              'Routing tree: fallthrough at the top, slack-devops with continue and a pagerduty-devops child, and a default sibling; three example alerts and where they go.')
        + p('Without <code>continue</code>, the first matching child wins and evaluation stops. With it, the alert also tries the following siblings, which is how you send the same alert to Slack and to PagerDuty.')
        + note('A correction to the book', 'In the chapter’s second routing table, <code>{environment="production", team="sre"}</code> is listed under <code>fallthrough</code>. With the configuration as printed it goes to <code>default</code>: every matcher on that route holds, because a missing <code>namespace</code> is not <code>default</code> and a missing <code>service</code> doesn’t match <code>^(api.+)</code>. POC 23 checks this, and <code>amtool config routes test</code> would show the same. In an interview, the lesson is that missing labels count as empty strings.')
        + h2('Grouping, on a timeline')
        + table(['Setting', 'Default', 'Means'],
                [['<code>group_by</code>', 'per route, inherited', 'Alerts with the same values for these labels form one group and one notification'],
                 ['<code>group_wait</code>', '30s', 'After the first alert of a new group, wait this long for more before sending'],
                 ['<code>group_interval</code>', '5m', 'After a notification, wait at least this long before sending an update about changes to the group'],
                 ['<code>repeat_interval</code>', '4h', 'Re-send an unchanged, still-firing group this often. The author sets 24h to fight fatigue']])
        + seq([('10:00:00', 'First HighAPIErrorRate alert (api1) creates the group; group_wait starts'), ('10:00:17', 'api2 joins the group'), ('10:00:30', 'One notification with both alerts'),
               ('10:00:35', 'api3 joins; it has missed the first send'), ('10:05:30', 'Next flush, group_interval after the last one: api3 is announced')])
        + p('The book’s table puts the third notification at 10:05:00, five minutes after the first alert. In Alertmanager the group timer restarts when it fires, so the update goes out at 10:05:30. The difference is small, but explaining it shows you understand the mechanism.')
        + h2('Time intervals, receivers and inhibition')
        + p('<code>active_time_intervals</code> and <code>mute_time_intervals</code> (added in 2022) reference named intervals built from weekdays, days of month (negative numbers count from the end), months, years, times and an IANA time zone. Routing still happens outside the interval; only the notification is held back. That catches people out: an incident fixed at 17:05 never gets its “resolved” message if warnings only notify in business hours.')
        + p('A receiver has a name and one or more integrations (Slack, PagerDuty, email, webhooks, SNS and others). Every integration supports <code>send_resolved</code>; turn it off for event-like alerts such as an OOM kill, where “resolved” means nothing.')
        + p('<b>Inhibition</b> mutes an incoming alert (the target) while another alert (the source) is firing with equal values for chosen labels. The standard rule mutes warnings and infos when a critical with the same <code>namespace</code> and <code>alertname</code> fires, which lets you keep a 90% disk warning and a 98% disk critical without double pages. An alert can’t inhibit itself, and inhibition is applied at notification time, so arrival order doesn’t matter.')
        + h2('High availability')
        + p('Unlike Prometheus, Alertmanager clusters natively. Instances gossip <b>silences</b> and the <b>notification log</b> (which group was sent where), so only one of them notifies. They do <b>not</b> gossip alerts. Every Prometheus must therefore send to every Alertmanager, and you must never put a load balancer between them. There is no quorum, so two or three instances spread across availability zones is enough.')
        + deeper('writing rules that don’t flap, and testing them')
        + h2('Robust rules')
        + ul(['<b>Combine signals.</b> High memory alone is noise; high memory <code>and</code> a high rate of major page faults is memory pressure. <code>unless</code> suppresses known conditions.',
              '<b>Choose for durations deliberately.</b> The author’s rule of thumb: warnings wait at least 15 minutes, criticals fire within 15. Never make <code>for</code> shorter than the evaluation interval.',
              '<b>Wrap selectors in _over_time.</b> One failed scrape makes <code>probe_success != 1</code> return nothing, which resets a pending alert. <code>last_over_time(probe_success[5m]) != 1</code> doesn’t.',
              '<b>Alert on symptoms.</b> The chapter points to Rob Ewaschuk’s <i>My Philosophy on Alerting</i>; lesson 13 turns that into burn-rate alerts. For anomaly detection with z-scores and seasonality, see GitLab’s write-up.'])
        + h2('Unit tests')
        + p('<code>promtool check rules</code> checks syntax. <code>promtool test rules</code> runs real tests: input series written in expanding notation (<code>1 1 1 1 0+0x12</code> means four ones then thirteen zeros; <code>_</code> is a missing sample), evaluation times, and the exact labels and annotations you expect.')
        + code("tests:\n  - interval: 1m\n    input_series:\n      - series: 'probe_success{instance=\"server1\", job=\"blackbox_ssh\"}'\n        values: '1 1 1 1 0+0x12'\n    alert_rule_test:\n      - alertname: SSHDown\n        eval_time: 15m\n        exp_alerts:\n          - exp_labels: {severity: critical, instance: server1, job: blackbox_ssh}")
        + p('The book expects the alert at 14 minutes. That is true in Prometheus 2.x; Prometheus 3 made range selectors left-open, so <code>max_over_time(...[5m])</code> turns true a minute earlier. Testing at 15 minutes passes on both, which is the kind of robustness a test suite should have.')),
    say='Prometheus decides that an alert is firing; Alertmanager routes it through a tree where the most specific match wins unless continue is set, groups alerts by labels with group_wait, group_interval and repeat_interval, mutes warnings while a related critical fires, and holds notifications outside active time intervals. In HA, Alertmanagers gossip silences and the notification log, so every Prometheus must send to every Alertmanager directly.',
    aws='AMP’s managed Alertmanager accepts a standard Alertmanager config, but its receivers are SNS topics: fan out from SNS to email, chat through Amazon Q Developer in chat applications, PagerDuty, Lambda or AWS Systems Manager Incident Manager. Load rules into an AMP rule groups namespace unchanged. In Amazon Managed Grafana, Grafana alerting’s notification policies follow the same routing model. POC 23 has an Alertmanager config with SNS receivers and a CI workflow.',
    iq=[('Your on-call engineers get forty pages when one availability zone fails. How would you fix that in Alertmanager and in the rules?',
         ['Forty pages for one cause means the alerts are causes rather than symptoms and Alertmanager isn’t collapsing them. I’d work on both sides.',
          'In Alertmanager, first look at <code>group_by</code>. If it includes <code>instance</code> or <code>pod</code>, every host gets its own page. Grouping by <code>alertname</code>, <code>service</code> and <code>environment</code>, or by <code>zone</code>, turns forty into a handful. Then add inhibition: an <code>AvailabilityZoneDown</code> or network alert as a source that mutes host-level alerts with the same <code>zone</code> label. Check <code>group_wait</code> is long enough for related alerts to arrive together.',
          'In the rules, page on user-facing symptoms, such as error-budget burn for each service, and make host-level alerts warnings that go to a ticket queue. A zone failure that a service survives shouldn’t page at all; that is the point of running in three zones.',
          'Finally I’d write regression tests: <code>amtool config routes test</code> for the routing, and a <code>promtool</code> test or a game day that kills a zone in staging, counting pages. The target is one page per incident with the context to act.'])],
    quiz=[['Why must every Prometheus send alerts to every Alertmanager?', ['Alertmanagers don’t gossip alerts, only silences and the notification log', 'Alertmanager has no clustering', 'For load balancing', 'Because of group_wait'], 0, 'Each Alertmanager only knows about alerts sent to it directly; gossip stops duplicate notifications.'],
          ['Why wrap probe_success in last_over_time in an alert?', ['It makes the query faster', 'A failed scrape would otherwise make the expression return nothing and reset the for timer', 'It converts the value to a counter', 'Alertmanager requires it'], 1, 'A missing result resets a pending alert; _over_time functions bridge single missing samples.']],
    turn='Run POC 23. Add a route for <code>team="payments"</code> that pages only in business hours, write the <code>amtool config routes test</code> command that proves it, and extend <code>test_grouping_timeline</code> with a fourth alert at 10:06:00. When does it go out?',
    take=['Most specific route wins; continue tries the siblings; missing labels are empty strings.', 'group_wait, group_interval, repeat_interval shape the noise; inhibition and time intervals cut it further.', 'Robust rules combine signals, use sensible for durations and _over_time, and are unit-tested.']))

# ══════════════════════════════════════════════════════════════ 6 Sharding, federation, HA
_ha = (
    box(20, 30, 170, 54, 'Prometheus A', 'replica="a", shard 0') + box(20, 110, 170, 54, 'Prometheus B', 'replica="b", shard 0')
    + box(20, 200, 170, 54, 'Prometheus C', 'replica="a", shard 1') + box(20, 280, 170, 54, 'Prometheus D', 'replica="b", shard 1')
    + box(290, 140, 190, 70, 'Thanos Query', 'dedup on replica')
    + box(290, 30, 190, 54, 'Alertmanager ×3', 'replica label dropped')
    + box(560, 140, 150, 70, 'Grafana', 'one data source')
    + arrow(192, 57, 288, 57) + arrow(192, 137, 288, 160) + arrow(192, 227, 288, 185) + arrow(192, 307, 288, 200)
    + arrow(482, 175, 558, 175)
    + '<text x="200" y="350" class="m" style="font-size:12px">targets split between shards by hashmod; each shard scraped twice for HA</text>')
L.append(dict(
    id='m-6', dot='6', part='M2', nav='Sharding, federation, HA', h1='When one Prometheus isn’t enough: sharding, federation and high availability',
    meta=meta('Scaling', 'Chapter 6', 'POC 22, 25'),
    learn=['The two limits that end single-server setups: cardinality and long-term storage', 'Sharding by service versus sharding with hashmod', 'What federation is for, and why it is usually the wrong answer', 'HA replicas, external labels, alert deduplication, and how to query a pair'],
    body=(
        h2('The big picture')
        + p('A single Prometheus eventually shows the same symptoms: memory creeps up, queries slow down, restarts take longer because of WAL replay. The book names two root causes. <b>Cardinality</b>: too many series, and the query engine is single-threaded, so more hardware only helps so far. <b>Long-term storage</b>: blocks max out at 31 days, so years of data means dozens of large independent databases on one disk.')
        + table(['Label', 'Cardinality'], [['<code>method</code> (GET, POST, PUT, DELETE…)', 'Good: a few fixed values'], ['<code>status_class</code> (2xx…5xx)', 'Good'], ['<code>ip</code>, <code>user_id</code>, <code>request_id</code>, full URL path', 'Unbounded: never a metric label']])
        + p('The book’s rule of thumb: most labels should have fewer than ten values, and almost none more than a hundred.')
        + h2('Sharding')
        + p('Prometheus servers don’t coordinate, so sharding means splitting <b>scrape jobs</b>, not data. There are two ways.')
        + table(['', 'By service', 'By hashmod'],
                [['How', 'Each server scrapes a set of teams, or a type of infrastructure', 'Every server sees all targets; relabeling keeps those where <code>md5(address) mod N</code> equals its shard number'],
                 ['Good', 'Predictable: people know where their metrics are', 'Even-ish load, automatic, no ownership decisions'],
                 ['Bad', 'Uneven load; reshuffles when teams change', 'Nobody knows which shard holds a series; uneven with few targets (the book saw 8 vs 16); changing N reshuffles most targets']])
        + code('relabel_configs:\n  - source_labels: [__address__]\n    modulus: 2\n    target_label: __tmp_hash\n    action: hashmod\n  - source_labels: [__tmp_hash]\n    regex: "1"            # this server is shard 1 of 2\n    action: keep')
        + p('With the Operator this is one field, <code>shards: 2</code> on the Prometheus resource, which adds those two rules to every job. Run by hand, you must add them to every job yourself.')
        + h2('Federation')
        + p('A higher-level Prometheus can scrape <code>/federate?match[]=…</code> on lower ones. It needs <code>honor_labels: true</code> so incoming labels aren’t overwritten, and distinct external labels per source so you can tell them apart.')
        + note('The book’s verdict', 'Federate only small, preferably aggregated subsets: if a series has an <code>instance</code> label, don’t federate it. Federating everything recreates the oversized server you sharded to escape. In the author’s experience it is a stop-gap nine times out of ten; go to Thanos or remote storage instead.')
        + h2('High availability')
        + pic(720, 360, _ha, 'My drawing of HA plus sharding: two shards, each scraped by two identical replicas that differ only in a replica external label. Alertmanager deduplicates alerts once the replica label is dropped; Thanos Query deduplicates series for Grafana.',
              'Four Prometheus servers in two shards of two replicas each, sending alerts to an Alertmanager cluster and queried through Thanos Query, which feeds Grafana.')
        + p('Prometheus has no built-in HA, so you run identical copies that scrape the same targets and evaluate the same rules, and differ only in one external label, for example <code>prometheus_replica</code>. Put them in different availability zones and have them monitor each other; for the last few percent, a SaaS check that watches the watchers.')
        + p('Two consequences. Alerts from the two replicas differ in the replica label, so Alertmanager would page twice; <code>alert_relabel_configs</code> with <code>labeldrop</code> on the replica label fixes that (the Operator adds it). And users now have two endpoints. The options for one view are federation with <code>max</code> or <code>min</code> over the replica label, a load balancer with sticky sessions (which shows different gaps after rolling restarts), remote storage, or the author’s favourite, Thanos Sidecar plus Thanos Query, which deduplicates on the replica label and fills one replica’s gaps from the other.')),
    say='One Prometheus runs out of road on cardinality and on long-term storage. I shard scrape jobs by service when ownership is clear, or with hashmod relabeling when I need balance, and I run every shard as two identical replicas in different zones that differ only in a replica external label. Alertmanager drops that label to deduplicate alerts, and Thanos Query or remote storage gives users one deduplicated view. Federation I keep for small aggregated subsets.',
    aws='Most AWS teams skip hand-built sharding and HA queries by remote-writing every replica to Amazon Managed Service for Prometheus: AMP deduplicates HA pairs that share a <code>cluster</code> label and differ in <code>__replica__</code>, scales storage and queries itself, and gives Grafana a single endpoint. Keep replicas in different AZs, or use the AMP managed collector, which runs scraping for you. POC 25 has the kube-prometheus-stack values and Terraform.',
    iq=[('Design Prometheus for 40 EKS clusters with one place to query and alert. What do you build?',
         ['I’d separate collection from storage. In each cluster, collection stays local and simple: a Prometheus in agent mode (or the ADOT collector, or the AMP managed collector) scraping that cluster, with an external label <code>cluster</code> and, if I run two replicas, a replica label.',
          'Storage and querying are central. On AWS I’d remote-write every cluster to Amazon Managed Service for Prometheus, one workspace per environment or per tenant boundary, with IRSA roles that allow only <code>aps:RemoteWrite</code>. AMP deduplicates HA pairs and serves PromQL, and Amazon Managed Grafana gets one data source per workspace.',
          'If I couldn’t use a managed service, I’d choose between Thanos (sidecars uploading blocks to S3, with Query, Store and Compactor centrally) when I want clusters to keep working if the centre fails, and Mimir when I want central ingestion and multi-tenancy.',
          'Rules and alerts: cluster-local alerts evaluate centrally on the <code>cluster</code> label, and SLO rules live in AMP rule groups. Alertmanager is AMP’s, routing by <code>cluster</code> and team to SNS.',
          'Guard rails: per-cluster <code>sample_limit</code> and write-relabel drops, cardinality dashboards per cluster, and a meta-monitoring alert when a cluster stops sending, since agents have no local query to tell you.'])],
    quiz=[['What does sharding with hashmod actually split?', ['The TSDB blocks', 'The scrape targets', 'The PromQL queries', 'The alerts'], 1, 'Each server keeps only targets whose hashed address modulo N equals its shard number.'],
          ['What must you do so two HA replicas don’t page twice?', ['Use different rules', 'Drop the replica label with alert_relabel_configs', 'Put a load balancer before Alertmanager', 'Lower group_wait'], 1, 'Identical alerts then share a label set and Alertmanager deduplicates them.']],
    turn='In POC 22 run <code>test_small_target_counts_are_uneven_and_resharding_moves_most_targets</code>, then change the shard count from 2 to 4 and measure how many targets move. In POC 25 read <code>dedup_thanos()</code> and <code>dedup_mimir()</code> and explain the difference to someone in two sentences.',
    take=['Cardinality and long-term storage are what break a single server.', 'Shard by service for predictability or hashmod for balance; federate only aggregates.', 'HA is identical replicas plus a replica label, deduplicated by Alertmanager and by Thanos or remote storage.']))

# ══════════════════════════════════════════════════════════════ 7 Optimizing and debugging
L.append(dict(
    id='m-7', dot='7', part='M2', nav='Optimizing and debugging', h1='Keeping Prometheus fast: cardinality, recording rules, jitter, profiling and GC',
    meta=meta('Scaling', 'Chapter 7', 'POC 21'),
    learn=['Reading /tsdb-status and finding the label that causes the damage', 'Dropping series safely and setting scrape limits', 'Recording rule naming and the cost of too many rules', 'Scrape jitter, pprof and promtool debug, query logs and limits', 'GOGC and GOMEMLIMIT'],
    body=(
        h2('Finding cardinality')
        + p('<i>Status → TSDB Status</i> lists the top ten in four tables. <b>Label names by value count</b> is the important one; ignore <code>__name__</code>, which is always first. <b>Series count by metric name</b> shows which metrics are expensive to query (the book’s top metric was four times slower than <code>up</code>). <b>Label names with high memory use</b> factors in value length. <b>Series count by label pair</b> mostly finds labels that are the same everywhere, such as <code>env="production"</code>, which belong in external labels.')
        + code('# which metrics carry the high-cardinality "name" label, and how many values each\nsort_desc(count by (__name__) ({name!=""}))')
        + h2('Fixing it')
        + p('Drop what you don’t need in <code>metric_relabel_configs</code> (or <code>metricRelabelings</code> on a ServiceMonitor): whole metrics with <code>action: drop</code> on <code>__name__</code>, or individual histogram buckets by matching <code>__name__</code> and <code>le</code> together, as the chart already does for API server latency buckets. <code>labeldrop</code> works too, but the remaining series must still be unique or the scrape is rejected.')
        + p('Then prevent the next one with <b>limits</b>, set globally or per job: <code>sample_limit</code>, <code>label_limit</code>, <code>label_value_length_limit</code> and <code>label_name_length_limit</code>. They are checked after metric relabeling, and any breach fails the <b>whole</b> scrape, so pair them with an alert on <code>up == 0</code>. Limits are what let you give teams self-service onboarding without fearing one bad deploy.')
        + h2('Recording rules')
        + p('A recording rule evaluates PromQL on a schedule and stores the result as a new series, so dashboards read one cheap series instead of recomputing an expensive query on every refresh.')
        + table(['Convention', 'Example'],
                [['<code>level:metric:operations</code>', '<code>job:http_requests:rate5m</code>'], ['Operations newest first', '<code>:sum_rate5m</code> is a sum of a 5-minute rate'], ['Drop <code>_total</code> after rate', '<code>http_requests_total</code> → <code>http_requests:rate5m</code>'], ['With <code>without</code>, list only the key labels in the level', '<code>node_namespace_pod_container:…</code>']])
        + p('The cost is constant background querying: the author has seen the rule manager use a quarter of a server’s memory. Rules in a group run in order, so a rule that reads another rule’s output must come after it; better still, don’t chain them.')
        + h2('Scrape jitter')
        + p('Delta-of-delta encoding only costs one bit when scrapes are exactly evenly spaced. If they are off by a few milliseconds, every timestamp costs 16 bits or more, and the book calls this the most common cause of oversized blocks. Prometheus snaps timestamps within 2 ms by default; <code>--scrape.timestamp-tolerance</code> raises that, up to 1% of the scrape interval.')
        + seq([('Measure', '<code>oy-scrape-jitter</code> reported 2 aligned and 22 unaligned targets, worst 30 ms'), ('Tune', 'set <code>scrape.timestamp-tolerance</code> to 30ms (allowed: up to 300 ms for a 30 s interval)'), ('Check', '23 aligned, 1 unaligned. Don’t chase the last one; recheck when disk usage grows')])
        + deeper('profiling, query control and garbage collection')
        + h2('pprof and promtool debug')
        + p('Prometheus exposes Go’s profiler at <code>/debug/pprof</code>. <code>go tool pprof http://…/debug/pprof/heap</code> then <code>top</code> or <code>web</code> shows what holds memory; in the book it was label building and the scrape cache. Heap isn’t total memory, so don’t expect the numbers to match the process size.')
        + p('Without Go installed, <code>promtool debug pprof</code> collects every profile into a tarball and <code>promtool debug all</code> adds the server’s own metrics. The author’s team runs <code>debug all</code> before restarting a misbehaving server, so the evidence survives the restart.')
        + h2('Query logs and limits')
        + p('<code>query_log_file</code> writes every completed query as JSON with its source (for example, which rule file) and timings. In-flight queries are always tracked in <code>queries.active</code> in the data directory and logged after a crash. <code>--query.max-concurrency</code> (default 20, low for big setups) and <code>--query.max-samples</code> (default 50 million samples <i>loaded</i>, not returned) stop runaway queries.')
        + h2('GOGC and GOMEMLIMIT')
        + table(['Setting', 'Effect', 'Book’s advice'],
                [['<code>GOGC=100</code> (default)', 'Collect when the heap has grown 100% over the live heap after the last collection', 'Fine for small servers'],
                 ['<code>GOGC=50</code>', 'Collect at 50% growth: less memory, more CPU', 'Start here above a few million head series'],
                 ['<code>GOMEMLIMIT</code>', 'A soft absolute limit; the collector works harder as memory approaches it', 'About 90% of the memory Prometheus has, e.g. 28 GiB on 32 GiB']])
        + p('The failure GOMEMLIMIT prevents: a WAL compaction and a few heavy queries spike memory, the next GC target lands above physical memory, and the kernel’s OOM killer gets there first.')),
    say='I find cardinality on the TSDB status page, look for label names with the most values, drop what nobody uses with metric relabeling, and put sample and label limits on scrape jobs so a bad deploy fails one scrape instead of the server. I precompute dashboard queries with recording rules named level:metric:operations, check scrape jitter when disk usage grows, and on big servers set GOGC to 50 and GOMEMLIMIT to about 90% of memory.',
    aws='On AMP you don’t tune GC or TSDB flags, but cardinality still matters because you pay per sample ingested and per active series: drop at the scraper (Prometheus agent, ADOT, or the AMP managed collector all accept relabeling) and watch AMP’s CloudWatch usage metrics against your quotas. Recording rules run in AMP rule groups namespaces. If you self-manage on EKS, set memory requests from head-series counts, set <code>GOMEMLIMIT</code> through an environment variable, and keep <code>promtool debug all</code> output in S3 before restarts.',
    iq=[('Prometheus memory doubled overnight and it was OOM-killed twice. Walk me through your investigation.',
         ['First stabilise: raise the memory limit or move it to a bigger node so it stays up long enough to investigate, and capture <code>promtool debug all</code> before any further restart.',
          'Then find what changed. <code>prometheus_tsdb_head_series</code> over the last two days tells me whether series count jumped; if it did, cardinality is the cause. TSDB Status shows the top metrics and label names by value count, and comparing with yesterday points at the new one. <code>count by (__name__)</code> over a new label, and the scrape job’s <code>scrape_samples_scraped</code>, find the target.',
          'If series didn’t change, look at queries: the query log or <code>queries.active</code> for a new dashboard or rule hitting tens of millions of samples, and <code>prometheus_rule_group_last_duration_seconds</code> for a slow recording rule.',
          'Fix: drop the offending label or metric with metric relabeling, add <code>sample_limit</code> to that job, and talk to the owning team about putting that dimension in logs or traces. If it was a query, add a recording rule or tighten <code>--query.max-samples</code>.',
          'Prevent: an alert on head-series growth rate, <code>GOMEMLIMIT</code> at about 90% of the limit so GC works harder before the OOM killer acts, and scrape limits on every job by default.'])],
    quiz=[['What happens when a scrape exceeds sample_limit?', ['Extra samples are dropped', 'The whole scrape fails and nothing from it is stored', 'Prometheus restarts', 'The limit doubles'], 1, 'Limits apply after metric relabeling, and a breach fails the entire scrape; up becomes 0.'],
          ['What is the most likely cause of unexpectedly large TSDB blocks, according to the book?', ['Too many recording rules', 'Scrape jitter defeating delta-of-delta encoding', 'High retention', 'Remote write'], 1, 'Irregular intervals make each timestamp cost 16 bits or more instead of one.']],
    turn='Run POC 21’s <code>cardinality_report()</code> on the <code>/metrics</code> of three exporters you run. Write the <code>metric_relabel_configs</code> that would drop the worst label, then set limits that would have caught it, and check with <code>apply_limits()</code>.',
    take=['TSDB Status finds the label; metric relabeling removes it; limits stop it returning.', 'Recording rules make dashboards cheap but cost the server constantly.', 'Jitter inflates disk; GOMEMLIMIT prevents GC-driven OOMs.']))

# ══════════════════════════════════════════════════════════════ 8 Node Exporter
L.append(dict(
    id='m-8', dot='8', part='M2', nav='Node Exporter', h1='The Node Exporter, and what any exporter is made of',
    meta=meta('Scaling', 'Chapter 8', 'POC 21'),
    learn=['The parts of an exporter: descriptors, collector, registry, handler', 'The collectors that matter most and the queries that go with them', 'Why load average misleads and pressure stall information doesn’t', 'The textfile collector and how to keep it honest', 'Troubleshooting slow scrapes per collector'],
    body=(
        h2('What an exporter is')
        + p('An exporter is a separate program that reads some other system and exposes what it finds as Prometheus metrics. Its anatomy is small: metric <b>descriptors</b> (name, help, labels), a <b>collector</b> with <code>Describe</code> and <code>Collect</code> methods, a <b>registry</b>, and an HTTP handler on <code>/metrics</code> that runs every collector on each scrape. The client library adds Go runtime and HTTP metrics for free.')
        + p('The Node Exporter is one of the few exporters maintained by the Prometheus project itself, alongside the Blackbox and SNMP exporters. Its motto in the book: if it is in <code>/proc</code>, the Node Exporter can get it. It has 49 collectors on by default on Linux, each running in its own goroutine, so turning collectors off doesn’t make scrapes faster. On Windows, use windows_exporter.')
        + h2('The collectors you will query')
        + table(['Collector', 'Key metrics', 'Use'],
                [['cpu', '<code>node_cpu_seconds_total{mode}</code>', 'Utilisation is the rate of non-idle seconds'],
                 ['meminfo', '<code>MemTotal</code>, <code>MemAvailable</code>, <code>MemFree</code>', 'Use Available (free plus reclaimable cache), not Free'],
                 ['filesystem', '<code>node_filesystem_size_bytes</code>, <code>_free_bytes</code>', 'Disk full forecasts with <code>predict_linear</code>'],
                 ['diskstats', '<code>node_disk_io_time_seconds_total</code>, read and written bytes', 'I/O saturation'],
                 ['netdev', 'transmit and receive bytes and drops', 'Throughput and drops'],
                 ['conntrack', '<code>node_nf_conntrack_entries</code> vs <code>_limit</code>', 'A full table silently drops connections'],
                 ['pressure', '<code>node_pressure_{memory,io}_stalled_seconds_total</code>', 'Real contention (kernel 4.20+)'],
                 ['timex', '<code>node_timex_offset_seconds</code>', 'Clock drift']])
        + code('# CPU used, in cores, and normalised by a recording rule that counts cores\nsum without (cpu, mode) (rate(node_cpu_seconds_total{mode!="idle"}[5m]))\n/ count without (cpu, mode) (node_cpu_seconds_total{mode="idle"})')
        + h2('Pressure, not load average')
        + p('The author begs you not to alert on load average; the kernel source itself calls it a silly number. <b>Pressure stall information</b> measures time lost waiting for CPU, memory or I/O. For memory and I/O it has two levels: <i>waiting</i> (some tasks blocked but the CPU found other work) and <i>stalled</i> (everything blocked, CPU cycles wasted). CPU has only waiting. Alert on memory and I/O stalled time; it can replace naïve “95% memory used” alerts, which fire on healthy caches.')
        + deeper('the textfile collector and troubleshooting')
        + h2('The textfile collector')
        + p('Point <code>--collector.textfile.directory</code> at a directory (globs allowed) and the Node Exporter includes every <code>*.prom</code> file in it, in the text exposition format. It is the right tool for facts about the machine produced by short-lived jobs: when the last backup ran, whether the last configuration-management run succeeded.')
        + code('# HELP backup_last_success_timestamp_seconds Last successful nightly backup.\n# TYPE backup_last_success_timestamp_seconds gauge\nbackup_last_success_timestamp_seconds 1714052400')
        + p('The trap is silent staleness: if the job stops running, the file keeps saying all is well. Alert on <code>time() - node_textfile_mtime_seconds</code> exceeding the expected interval. Service-level batch metrics belong in the Pushgateway, not here. The community keeps a collection of ready-made textfile scripts.')
        + h2('When scrapes get slow')
        + p('<code>node_scrape_collector_duration_seconds</code> per collector usually shows one culprit. In the author’s story it was the non-default <code>processes</code> collector, contending for a kernel lock with the application and intermittently exceeding the scrape timeout, which left gaps in every node graph. Don’t alert on <code>node_scrape_collector_success == 0</code> blindly: some default collectors (InfiniBand, Fibre Channel) always fail on hosts without that hardware.')),
    say='An exporter is a small program with descriptors, a collector and a registry behind a /metrics handler. From the Node Exporter I rely on cpu, meminfo with MemAvailable, filesystem, diskstats, netdev, conntrack and especially pressure stall information, which shows real contention where load average misleads. For machine facts from batch jobs I use the textfile collector with an alert on file age so it can’t go stale silently.',
    aws='On EC2, run node_exporter as a systemd service from the AMI or install it with SSM Run Command, and discover it with <code>ec2_sd_configs</code>. On EKS, it runs as a DaemonSet from kube-prometheus-stack, or use the ADOT collector’s <code>hostmetrics</code> receiver instead. The CloudWatch agent covers similar host metrics for CloudWatch-native setups, but doesn’t expose pressure stall information by default. For Windows instances, windows_exporter.',
    iq=[('How would you alert on memory problems on Linux hosts without paging on healthy page cache?',
         ['Linux uses spare memory for cache, so “memory used above 90%” fires on perfectly healthy machines. The first improvement is to use <code>node_memory_MemAvailable_bytes</code>, which counts reclaimable cache as available, rather than MemFree.',
          'The better signal is the cost of the shortage, not the level. Pressure stall information gives <code>node_pressure_memory_stalled_seconds_total</code>: the share of time every task was blocked on memory. A rate of that above a few percent for ten or fifteen minutes means the host is genuinely thrashing. Combining low MemAvailable <code>and</code> a high rate of major page faults is the book’s alternative for older kernels.',
          'Then decide severity. A single host under pressure in an autoscaled group is a ticket or nothing at all if the service’s SLO is fine; it pages only through the service’s burn-rate alert. I’d also alert on OOM kills from <code>node_vmstat_oom_kill</code> as an event, with send_resolved off.'])],
    quiz=[['Why does the book discourage alerting on load average?', ['It isn’t exposed by Node Exporter', 'High load doesn’t reliably mean impactful contention; pressure stall information does', 'It is a counter', 'It needs root'], 1, 'Load average mixes runnable and uninterruptible tasks and doesn’t correlate well with impact.'],
          ['What protects against a stale textfile metric?', ['Pushgateway', 'An alert on node_textfile_mtime_seconds age', 'sample_limit', 'Recording rules'], 1, 'The file keeps its last values forever; its modification time tells you the writer stopped.']],
    turn='Write a textfile-collector script for your own nightly job that writes a success timestamp, plus the alerting rule on file age and on the timestamp itself. Add it to POC 23’s <code>config/rules.yml</code> and run the linter.',
    take=['An exporter is descriptors, a collector, a registry and a handler.', 'Use MemAvailable and pressure stall information; avoid load average.', 'The textfile collector needs an age alert; per-collector durations find slow scrapes.']))

# ══════════════════════════════════════════════════════════════ 9 Remote storage
L.append(dict(
    id='m-9', dot='9', part='M2', nav='Remote storage', h1='Remote write and remote read: VictoriaMetrics and Mimir',
    meta=meta('Scaling', 'Chapter 9', 'POC 25'),
    learn=['Remote read and remote write, and why write won', 'Agent mode: scraping with no local queries', 'Tuning remote write: relabeling, queues, shards, capacity, backoff', 'VictoriaMetrics against Mimir: storage, efficiency, compatibility, HA dedup'],
    body=(
        h2('Two APIs')
        + p('Prometheus keeps its storage local and unreplicated on purpose. To go further it offers two HTTP APIs using protocol buffers and Snappy compression. <b>Remote read</b> lets Prometheus query another store alongside its own; few people use it, partly because a broken remote store can break alert queries. Thanos uses it the other way round, to read <i>from</i> Prometheus. <b>Remote write</b> streams every sample to another system and is how you feed AMP, Mimir, Cortex or VictoriaMetrics. With <code>--web.enable-remote-write-receiver</code>, Prometheus can also accept writes, which is how Loki’s ruler sends metrics it derives from logs.')
        + h2('Agent mode')
        + p('<code>--enable-feature=agent</code> (2.32) turns Prometheus into a scraper only: no queries, no rules, no local blocks. The WAL is kept just long enough to send, up to about two hours. You keep pull’s advantages, such as the <code>up</code> series, and gain push’s: stateless edge collectors and one central store. The book still called it experimental; it is how many teams run collection today.')
        + h2('Tuning remote write')
        + p('Remote write sends <b>everything</b> unless you say otherwise, the opposite of federation. Start by sending less with <code>write_relabel_configs</code>, which run after ingestion and see all labels, for example only one team’s series or only production. Don’t micro-optimise; the config becomes unreadable.')
        + p('Then size the queue. Each destination gets an in-memory queue divided into shards that send in parallel. If a shard fills, Prometheus stops reading the WAL; nothing is lost unless the backlog outlives WAL truncation, which happens every two hours.')
        + table(['Setting', 'Default', 'Advice'],
                [['<code>min_shards</code>', '1', 'About samples per second ÷ capacity, so startup doesn’t lag. Get the rate from <code>rate(prometheus_tsdb_head_samples_appended_total[5m])</code>'],
                 ['<code>max_shards</code>', '200', 'Leave it; lower it if you raise the two below, to cap memory'],
                 ['<code>capacity</code>', '2500', 'Samples each shard buffers; keep at least 3 × max_samples_per_send'],
                 ['<code>max_samples_per_send</code>', '500', 'Batch size; raise for high throughput'],
                 ['<code>batch_send_deadline</code>', '5s', 'Send a partial batch after this long'],
                 ['<code>min_backoff</code> / <code>max_backoff</code>', '30ms / 5s', 'Retry delay doubles up to the max, then repeats']])
        + h2('VictoriaMetrics or Mimir')
        + table(['', 'VictoriaMetrics', 'Grafana Mimir'],
                [['Storage', 'Local or block storage (EBS)', 'Object storage (S3); monolithic local disk only for evaluation'],
                 ['Efficiency', 'Very frugal: a 2020 benchmark claims ~0.3 vs 2.1 bytes per sample and ~5× less RAM than Prometheus', 'About Prometheus-level; built for scale, not thrift'],
                 ['Query language', 'MetricsQL, a superset of PromQL; 72.78% on the compliance suite because some results differ on purpose', 'Full PromQL'],
                 ['Deployment', 'Single node scales a long way (1.5M+ samples/s per the docs); cluster for multi-tenancy', 'Microservices for production; Helm chart'],
                 ['HA pairs', 'Replicas must have identical external labels; dedup per scrape interval', 'HA tracker elects a leader replica via Consul or etcd; fails over after 30 s, losing that gap'],
                 ['Licence and model', 'Open-core: downsampling, full multi-tenancy, mTLS in enterprise', 'AGPLv3; Cortex is the Apache-licensed sibling'],
                 ['Multi-tenancy', 'Enterprise', '<code>X-Scope-OrgID</code> header on writes and on the Grafana data source']])
        + note('A detail interviewers like', 'MetricsQL’s <code>rate()</code> includes the last sample before the window, while PromQL uses only samples inside it, so the same query can return slightly different numbers on the two systems. Neither is a bug; they are different definitions.')
        + p('The author’s summary: VictoriaMetrics if efficiency matters most and local disks are fine; Mimir if you want cheap object storage, long retention and native multi-tenancy, and accept higher resource use.')),
    say='Remote write streams every sample to a central store; I filter with write_relabel_configs, size min_shards from the ingestion rate divided by capacity, and keep capacity at three times the batch size. For collection I like Prometheus in agent mode: pull semantics at the edge, no local state. Between backends, VictoriaMetrics wins on efficiency with local disks, Mimir on object storage, multi-tenancy and strict PromQL, and on AWS AMP gives me the Mimir-style model as a managed service.',
    aws='Amazon Managed Service for Prometheus is the AWS answer to this chapter: a Cortex-based remote-write target on object storage with SigV4 auth, multi-AZ durability and HA-pair dedup on <code>cluster</code> and <code>__replica__</code>. Point any Prometheus, agent, ADOT collector or the AMP managed collector at its remote-write URL with an IRSA role that has <code>aps:RemoteWrite</code>. POC 25 has Terraform for the workspace and role, and kube-prometheus-stack values with tuned queues.',
    iq=[('Remote write to your central store is falling behind during traffic peaks. How do you diagnose and fix it?',
         ['I’d look at Prometheus’ own remote-write metrics. <code>prometheus_remote_storage_highest_timestamp_in_seconds</code> minus <code>prometheus_remote_storage_queue_highest_sent_timestamp_seconds</code> is the lag. <code>prometheus_remote_storage_shards</code> against <code>shards_max</code> shows whether it has scaled out fully, and failed or retried sample counters show whether the backend is rejecting or throttling.',
          'If shards are at the max and the backend is healthy, the queue is too small for the rate: raise <code>max_samples_per_send</code> and <code>capacity</code> together (capacity at least three times the batch), set <code>min_shards</code> near the ingestion rate divided by capacity so it starts warm, and lower <code>max_shards</code> if memory is tight.',
          'If the backend is throttling, retries back off to <code>max_backoff</code>; the fix is on the backend side, such as raising an AMP ingestion quota or scaling Mimir distributors and ingesters.',
          'In every case I’d send less: <code>write_relabel_configs</code> dropping high-cardinality histograms nobody queries centrally. And I’d alert on the lag, because if it exceeds the two-hour WAL window, data is lost.'])],
    quiz=[['Unlike federation, what does remote write send by default?', ['Only aggregated series', 'Every series and sample', 'Only alerts', 'Nothing until configured with match[]'], 1, 'Remote write forwards everything unless write_relabel_configs filters it.'],
          ['How does Mimir deduplicate an HA Prometheus pair?', ['Identical external labels', 'An HA tracker elects one replica and drops samples from the other', 'Query-time merging', 'It doesn’t'], 1, 'Leader election via Consul or etcd; failover after a configurable silence, with a small gap.']],
    turn='Use POC 25’s <code>remote_write_plan()</code> on your own ingestion rate (from <code>rate(prometheus_tsdb_head_samples_appended_total[5m])</code>) and turn the result into the <code>queueConfig</code> block in <code>config/prometheus-remote-write.yml</code>.',
    take=['Remote write won; agent mode makes collectors stateless.', 'Filter first, then size shards from samples per second ÷ capacity.', 'VictoriaMetrics for thrift on local disks, Mimir for object storage and tenants, AMP when you want it managed.']))

# ══════════════════════════════════════════════════════════════ 10 Thanos
_thanos = (
    box(20, 30, 150, 50, 'Prometheus + Sidecar', '') + box(20, 110, 150, 50, 'Prometheus + Sidecar', '')
    + box(20, 210, 150, 50, 'Thanos Receive', 'remote write in') + box(20, 290, 150, 50, 'Thanos Ruler', 'global rules')
    + box(290, 140, 150, 60, 'Thanos Query', 'fan-out, dedup')
    + box(530, 60, 190, 54, 'Query Frontend', 'split, cache')
    + box(290, 290, 150, 50, 'Thanos Store', 'gateway to S3')
    + box(530, 210, 190, 54, 'Object storage', 'S3 blocks')
    + box(530, 300, 190, 50, 'Compactor', 'compact, downsample')
    + arrow(172, 55, 288, 155) + arrow(172, 135, 288, 165) + arrow(172, 235, 288, 185) + arrow(172, 315, 288, 195)
    + arrow(442, 160, 528, 95, 'StoreAPI', dx=-6) + arrow(365, 288, 365, 202)
    + arrow(442, 315, 528, 245) + arrow(170, 45, 528, 225, dash=True) + arrow(625, 298, 625, 266))
L.append(dict(
    id='m-10', dot='10', part='M2', nav='Thanos', h1='Thanos: a global view and unlimited retention, one component at a time',
    meta=meta('Scaling', 'Chapter 10', 'POC 25'),
    learn=['The three goals of Thanos and the StoreAPI that ties it together', 'Sidecar, Compactor, Query, Query Frontend, Store, Ruler and Receive', 'Vertical compaction and downsampling, and what each really buys', 'Scaling the read path: the distributed engine, splitting, sharding, caching, partitioning'],
    body=(
        h2('The big picture')
        + p('Thanos began at Improbable, written by Bartłomiej Płotka and Fabian Reinartz, and is a CNCF incubating project. Its goals are a global query view, unlimited retention and highly available components. Unlike Mimir or VictoriaMetrics it is not one system but a set of small components, all subcommands of one <code>thanos</code> binary, that you add as you need them. The author recommends it as the first step beyond plain Prometheus, and notes almost nobody runs every component.')
        + pic(740, 360, _thanos, 'My drawing of the components. Everything that serves data speaks the gRPC StoreAPI to Thanos Query. Sidecars and Receive upload two-hour blocks to object storage; Store serves them back; Compactor compacts and downsamples them.',
              'Thanos components: Prometheus with sidecars, Receive and Ruler feed Thanos Query; Query Frontend sits in front; Store reads object storage; Compactor maintains it.')
        + h2('The components')
        + table(['Component', 'Job', 'Worth knowing'],
                [['Sidecar', 'Serves Prometheus data over StoreAPI (via remote read) and uploads each 2h block to object storage', 'Needs local compaction off: min and max block duration both 2h (the Operator does this). Also reloads Prometheus on config or rule changes, with env-var substitution'],
                 ['Query', 'PromQL across every StoreAPI endpoint, deduplicating on the replica label', '100% PromQL compatible; can point at other Queries. Discovers endpoints statically, by <code>dns+</code> or <code>dnssrv+</code>'],
                 ['Query Frontend', 'Splits long range queries (24h by default), shards some by labels, caches results', 'Cache only for range queries; Memcached or Redis for more than one replica'],
                 ['Store', 'Serves blocks from object storage', 'Queried even when the sidecar has the same data: set <code>--max-time=-7d</code> to avoid overlap. Partition by time or by external labels; cache index and chunks'],
                 ['Compactor', 'Compacts and downsamples blocks in the bucket', 'One per bucket. Optional vertical compaction merges replica blocks; risky'],
                 ['Ruler', 'Evaluates rules across many Prometheus servers through Query', 'Additive only: local rules almost never fail, global ones depend on Query and every sidecar. Stateless mode writes results by remote write'],
                 ['Receive', 'A remote-write receiver that keeps a local TSDB (15 days) and uploads blocks', 'Hashring with Ketama consistent hashing, replication factor with write quorum, multi-tenancy; no built-in dedup']])
        + h2('Compaction and downsampling')
        + p('The Compactor compacts as Prometheus would. <b>Vertical compaction</b> also merges overlapping blocks from HA replicas to save storage; it needs three flags precisely because a mistake can destroy history, and the book says not to turn it on after reading one chapter.')
        + p('<b>Downsampling</b> is widely misunderstood. It doesn’t save space: it adds a 5-minute version of raw data older than 40 hours and a 1-hour version of 5-minute data older than 10 days, each storing count, sum, min, max and a counter value. Because the index barely shrinks, expect storage to double or triple. What you gain is fast queries over months. Keep the three per-resolution retentions equal, or old data becomes reachable only at a coarse step.')
        + deeper('scaling the read path')
        + h2('Making Query fast')
        + p('The default engine is Prometheus’ own: single-threaded, and it pulls every matching series to the querier before aggregating. It can’t push an <code>avg</code> down to the leaves, because the average of averages isn’t the average. Thanos’ own engine (<code>--query.promql-engine=thanos</code>) is multi-threaded and can run distributed: a top querier delegates <code>sum(x)</code> to sub-queriers, each of which sums its own Prometheus servers, and only adds their results.')
        + p('In front of that, Query Frontend splits a week into seven one-day queries spread over queriers, which also stops one huge query from OOM-ing a querier, and caches results so a dashboard opened by ten people runs once. In the book, a week-long p99 went from about 30 s to 20 s with the frontend, and to 15 s with a second querier.')
        + h2('Receive in more detail')
        + p('Receive spreads incoming series over a hashring defined in JSON. Plain hashmod reshuffles most series when you add a node; the Ketama consistent hashing algorithm (<code>--receive.hashrings-algorithm=ketama</code>) moves far fewer, which POC 25 measures. With a replication factor of 3, a write succeeds when two receivers accept it.')),
    say='Thanos is a toolbox around Prometheus. Sidecars expose each server over the StoreAPI and upload two-hour blocks to S3; Query fans out across them and deduplicates HA replicas on the replica label; Store serves the bucket; the Compactor compacts and downsamples, which speeds long queries rather than saving space. I add Query Frontend for splitting and caching, Ruler only for global rules, and Receive when clusters must push rather than be queried.',
    aws='On AWS, Thanos uses S3 for blocks with an IRSA role per component, and S3 lifecycle rules move old blocks to Standard-IA. Query, Store, Compactor and Frontend run on EKS; ElastiCache for Memcached or Redis backs the frontend and store caches. The managed alternative is AMP, which gives the same global view and long retention without operating components, at the cost of central ingestion. POC 25 includes the S3 objstore config, the bucket Terraform and simulations of dedup, downsampling, splitting and hashrings.',
    iq=[('When would you choose Thanos over remote write to a central store such as Mimir or AMP?',
         ['The core difference is where data lives. With Thanos sidecars, each Prometheus keeps recent data locally and uploads blocks; queries fan out at read time. With remote write, every sample is pushed to a central system that becomes the source of truth.',
          'Thanos fits when clusters must stay independent: if the central query layer fails, every Prometheus still has its data and still alerts locally. It also fits when network egress or central ingestion cost is a concern, since only finished blocks are uploaded, and when you want to start small and add components.',
          'Remote write to Mimir or AMP fits when you want one place where all data lands quickly, strong multi-tenancy, simpler query paths, and stateless collectors in agent mode, especially for many small or short-lived clusters.',
          'On AWS I’d default to AMP for most teams because it removes the operational load, and pick Thanos where data residency, cost at very high volume, or independence from a central service is the deciding factor. Either way, the HA-pair and external-label design is the same.'])],
    quiz=[['What does Thanos downsampling primarily improve?', ['Storage cost', 'Query speed over long ranges', 'Ingestion rate', 'Alert latency'], 1, 'It adds coarser blocks; storage grows because the index stays large, but long queries read far fewer samples.'],
          ['Why should Prometheus’ local compaction be disabled when the Sidecar uploads blocks?', ['To save CPU', 'The Sidecar only uploads uncompacted level-1 blocks', 'Thanos can’t read compacted blocks', 'It isn’t necessary'], 1, 'It ignores blocks with compaction level above 1, so local compaction would stop uploads.']],
    turn='Run POC 25’s tests, then change <code>test_ketama_moves_far_fewer_series_than_hashmod_when_adding_a_receiver</code> to go from 4 to 6 receivers. Then sketch, for your own setup, which Thanos components you would run and which you would skip, and why.',
    take=['Every Thanos component speaks the StoreAPI; add them one at a time.', 'Sidecar + Query gives a global, deduplicated view; Store + Compactor give retention.', 'Downsampling speeds long queries and costs storage; the Thanos engine and Query Frontend scale reads.']))
