# Interview drills: five questions an SRE interviewer asks, each with a short answer, the working
# for the whiteboard, the follow-ups, and a hands-on task (hands.py) that proves you have done it.
from extras import table
from extras2 import p, ul
from pe import h2, note
from slo_track import cb

L = []


def meta(n, asked):
    return f'<span class="chip">Interview drill</span>Drill {n} of 5 · asked as: “{asked}”'


# ══════════════════════════════════════════════════════════════ 1 why 14.4
L.append(dict(
    id='k-1', dot='1', part='K1', nav='Why 14.4? Burn-rate alerts', h1='“Why do you page at a burn rate of 14.4?”', practical=True,
    meta=meta(1, 'How would you alert on an SLO?'),
    learn=['Derive 14.4, 6 and 1 from a budget share and a window', 'Say what each of the two windows on a rule is for', 'Turn a burn rate into the error rate that pages for any SLO', 'Name the three cases where the standard numbers are wrong'],
    body=(
        h2('The working, for the whiteboard')
        + p('Burn rate is how fast you are spending the error budget, compared with the pace that would use it up exactly at the end of the SLO window. Pick how much budget is worth waking someone for, and how quickly you want to know:')
        + cb('burn rate', 'burn rate = share of budget x SLO window / alert window\n\n2% in 1 hour   ->  0.02 x 720 h / 1 h  = 14.4     page\n5% in 6 hours  ->  0.05 x 720 h / 6 h  = 6        page\n10% in 3 days  ->  0.10 x 720 h / 72 h = 1        ticket')
        + p('14.4 is a pace, so it is the same for every SLO. The error rate it stands for is not: multiply by the budget. For 99.9% that is 14.4 × 0.1% = 1.44% of requests failing; for 99% it is 14.4%.')
        + h2('Two windows on every rule')
        + table(['Window', 'Its job', 'Without it'],
                [['Long (1 h)', 'Proves the budget spent is real. A 30-second blip can’t spend 2% of a month.', 'You page on noise.'],
                 ['Short (5 m), about 1/12 of the long one', 'Proves it is still happening, and clears the page soon after the fix.', 'The page keeps firing for up to an hour after recovery.']])
        + p('Two paging rules, because they catch different failures. A full outage on three nines is a burn rate of 1,000 and trips the 1-hour rule in under a minute. A steady 0.8% error rate is a burn rate of 8: it never reaches 14.4, yet it would empty the budget in under four days, and the 6× rule catches it.')
        + cb('alert, 99.9% SLO', '(slo:errors:ratio_rate1h > 14.4 * 0.001 and slo:errors:ratio_rate5m  > 14.4 * 0.001)\nor\n(slo:errors:ratio_rate6h > 6 * 0.001    and slo:errors:ratio_rate30m > 6 * 0.001)')
        + note('Where the standard numbers are wrong', '<b>A different SLO window.</b> 28 days gives 13.44; 7 days gives 3.36. <b>A loose SLO.</b> The highest possible burn rate is 1 ÷ budget, so below about 93% the 14.4 rule can never fire. <b>Low traffic.</b> One failure in a 5-minute window can look like a huge burn: see drill 3.')),
    say='I alert on burn rate with two windows. 14.4 is the pace that spends 2% of a 30-day budget in one hour: 0.02 times 720. I pair the 1-hour window with a 5-minute one so the page proves it’s still happening and clears after the fix, and I add a 6× rule over 6 hours and 30 minutes for slower leaks. For a 99.9% SLO, 14.4× means 1.44% of requests failing.',
    aws='Amazon Managed Service for Prometheus runs the same recording and alerting rules and sends pages through SNS to Incident Manager. In CloudWatch, Application Signals SLOs have burn-rate alarms built in; otherwise use metric math for the two ratios and a composite alarm for the AND.',
    iq=[('Does 14.4 come from having a 99% SLO?',
         ['No. 14.4 comes from two choices that have nothing to do with the target: page when 2% of the budget goes in one hour, and a 30-day window, which is 720 hours. 0.02 × 720 = 14.4 for any SLO.',
          'The target only matters when I turn the burn rate into an error rate. With a 99% SLO the budget is 1%, so 14.4× happens to be a 14.4% error rate, which is where the confusion comes from. With 99.9% it is 1.44%.']),
        ('Why not just alert when the error rate is above the SLO threshold?',
         ['Because that pages on things that don’t matter and misses things that do. Ten seconds at 0.2% errors is above a 0.1% threshold and spends almost nothing. A week at 0.09% is below it and nearly uses the budget.',
          'Burn rate ties the alert to the thing I promised: how much of the month’s budget is going, and how fast. The long window gives precision, the short one gives a fast reset, and the size of the burn decides page or ticket.']),
        ('Your fast-burn alert fired and resolved three times last night. What do you change?',
         ['First I’d look at traffic. If the service is quiet at night, a handful of failures in the 5-minute window swing the ratio. I’d add a minimum request count, or a confidence bound on the ratio, or lean on synthetic probes for the quiet hours.',
          'If traffic is fine, the service really is flapping around the threshold and the alert is telling the truth: I’d group the notifications and fix the cause. I wouldn’t lengthen the windows first, because that slows every real page.'])],
    quiz=[['A 99.95% SLO over 30 days. What error rate trips the 14.4× rule?', ['0.72%', '1.44%', '14.4%'], 0, '14.4 × 0.05% = 0.72%.'],
          ['What is the short window for?', ['Catching slow leaks', 'Clearing the page soon after recovery', 'Reducing the query cost'], 1, 'It proves the problem is still happening now, so the alert resets within minutes of the fix.'],
          ['A steady 0.8% error rate on a 99.9% SLO. Which rule pages?', ['The 14.4× rule', 'The 6× rule', 'Neither'], 1, 'Burn rate is 8: under 14.4, over 6.']],
    turn='On paper, with no notes: derive 14.4 and 6, then write the paging error rates for 99%, 99.9% and 99.99%. Check yourself against the first hands-on below. Then say the 30-second answer aloud, timed.',
    take=['14.4 = 2% of a 30-day budget in one hour. It is a pace, not an error rate.', 'Error rate that pages = burn rate × (1 − SLO).', 'Long window for precision, short window for reset; two rules for fast and slow burns.', 'Recompute for other windows, loose SLOs and low traffic.']))

# ══════════════════════════════════════════════════════════════ 2 rate / increase / irate
L.append(dict(
    id='k-2', dot='2', part='K1', nav='rate vs increase vs irate', h1='“What’s the difference between rate, increase and irate?”', practical=True,
    meta=meta(2, 'Walk me through this PromQL'),
    learn=['Say what each function returns, in one sentence', 'Work one example by hand, including the extrapolation', 'Explain counter resets and why it is sum(rate()), never rate(sum())', 'Pick the right one for alerts, tables and graphs'],
    body=(
        h2('One sentence each')
        + table(['Function', 'Answers', 'Use it for'],
                [['<code>rate(x[5m])</code>', 'How fast did the counter rise, per second, averaged over the window?', 'Alerts, SLO ratios, recording rules, most graphs'],
                 ['<code>increase(x[5m])</code>', 'How much did it rise in the window? It is rate × 300.', 'Tables and single numbers: “errors in the last hour”'],
                 ['<code>irate(x[5m])</code>', 'How fast was it rising between the last two samples?', 'Zoomed-in graphs only. Never alerts.']])
        + h2('Work it by hand')
        + p('A counter scraped every 15 seconds reads 100, 110, 170, 180 at 15, 30, 45 and 60 seconds. Evaluate <code>[1m]</code> at 60 seconds.')
        + cb('by hand', 'raw rise          180 - 100 = 80, over the 45 s the samples cover\nincrease[1m]      80 x 60 / 45 = 106.67     stretched to the whole 60 s window\nrate[1m]          106.67 / 60  = 1.78 /s\nirate[1m]         (180 - 170) / 15 = 0.67 /s   the +60 spike is already forgotten')
        + p('The stretch is why <code>increase</code> can return 106.67 for something you can only count in whole numbers. Prometheus assumes the counter kept rising at the same pace in the part of the window the samples don’t cover, as long as that gap is small compared with the scrape interval.')
        + h2('Two rules that follow')
        + ul(['<b>rate first, then sum.</b> <code>sum(rate(x[5m]))</code>. A restarting pod’s counter drops to zero; rate sees the drop per series and treats it as a reset. Sum first and the drop is hidden inside the total, where it looks like a huge negative step.',
              '<b>Window at least four scrape intervals.</b> Fewer samples means the stretch is most of the answer, or there is no answer at all. In Grafana, <code>$__rate_interval</code> picks a safe one.'])
        + note('Only for counters', 'All three assume a number that only goes up. For a gauge (memory, queue length) a fall is not a reset: use <code>delta()</code> or <code>deriv()</code>.')),
    say='All three work on counters. rate is the per-second average over the window and handles counter resets. increase is the same value times the window length, so it’s an estimate and can be fractional. irate uses only the last two samples, so it reacts fast and forgets fast. I use rate in alerts and recording rules, increase where a person wants a count, and irate only on zoomed-in graphs.',
    aws='Amazon Managed Service for Prometheus and Amazon Managed Grafana use the same PromQL. In CloudWatch the nearest thing is a metric-math RATE(), or the Sum statistic over a period for counts; CloudWatch has no counter-reset handling, because it stores each period’s value, not a running total.',
    iq=[('The counter rose by 80 but increase() says 106.67. Is that a bug?',
         ['No, it’s extrapolation. My four samples only cover 45 seconds of the 60-second window. Prometheus assumes the same pace through the uncovered 15 seconds and scales the 80 up: 80 × 60 ÷ 45.',
          'It does that because scrapes never land exactly on the window’s edges, so without it every increase would under-count. The price is fractional results and noise when the window holds few samples.']),
        ('Why is irate dangerous in an alert?',
         ['It looks at the last two samples in the window and ignores the rest. A spike that ended 15 seconds ago is invisible, and whether the alert fires depends on which scrape the evaluation happens to land after.',
          'An alert should be stable under small timing changes. rate over a few minutes is; irate isn’t.']),
        ('Someone wrote rate(sum(http_requests_total)[5m:]). What is wrong?',
         ['The sum is taken first, so when one pod restarts and its counter drops to zero, the total falls a little. rate can’t tell which series reset; it sees the whole total as a counter that dropped and miscounts.',
          'It should be sum(rate(http_requests_total[5m])). rate handles the reset per series, and the sum adds up correct rates.'])],
    quiz=[['increase(x[5m]) equals…', ['rate(x[5m]) × 300', 'rate(x[5m]) × 5', 'irate(x[5m]) × 300'], 0, 'Same calculation, in units of “per window” instead of “per second”.'],
          ['Scrape interval is 30 s. Which range is the smallest sensible one for rate?', ['[30s]', '[1m]', '[2m]'], 2, 'About four scrape intervals, so a missed scrape or two still leaves samples.'],
          ['Which is right for an SLO error ratio?', ['irate on both sides', 'rate on both sides', 'increase on top, rate below'], 1, 'rate on errors and on the total; increase would give the same ratio.']],
    turn='Cover the working above and redo it for samples 200, 200, 230, 260 at 15-second steps. Then do the second hands-on: write your expected values into the promtool test before you run it.',
    take=['rate: per-second average over the window, reset-aware.', 'increase = rate × window; an estimate, often fractional.', 'irate: last two samples; graphs only.', 'Always sum(rate()), with a window of at least four scrapes.']))

# ══════════════════════════════════════════════════════════════ 3 low traffic
L.append(dict(
    id='k-3', dot='3', part='K1', nav='Paging at low traffic', h1='“Your service gets 100 requests an hour. How do you alert on its SLO?”', practical=True,
    meta=meta(3, 'What breaks burn-rate alerts?'),
    learn=['Explain why a ratio from a small sample can’t be trusted', 'Use a confidence bound to decide when failures are enough', 'Quote the numbers: 24 in 100, 42 in 200, 173 in 1,000', 'List the other fixes: probes, bad minutes, longer windows'],
    body=(
        h2('The problem in one line')
        + p('With a 99% SLO, the fast-burn page means a 14.4% error rate. At 1,000 requests an hour, 15% failing is strong evidence. At 100 an hour, 15 failures could be bad luck on a service that is really at 10%. The ratio is the same; the evidence is not.')
        + h2('The fix: ask the pessimistic question')
        + p('Don’t ask “is the observed rate above 14.4%?” Ask “even on the most cautious reading of this sample, is the true rate above 14.4%?” The cautious reading is the lower end of a confidence interval. The Wilson score interval is the one to use, because it behaves with small samples and rates near zero.')
        + cb('Wilson lower bound', 'p = failures / n        z = 2.576 for 99% confidence\n\nlower = [ p + z²/2n − z·√( p(1−p)/n + z²/4n² ) ] / ( 1 + z²/n )\n\npage when lower > 14.4 x (1 − SLO)')
        + table(['Requests in the window', 'Failures needed to page', 'Observed rate at that point'],
                [['100', '24', '24%'], ['200', '42', '21%'], ['1,000', '173', '17.3%']])
        + p('As traffic grows the interval narrows and the number you need approaches 14.4%. With plenty of traffic the plain ratio is enough, which is why most services never need this.')
        + h2('Other tools for quiet services')
        + ul(['<b>Synthetic probes</b> give a steady stream of events when customers don’t (drill 5).', '<b>Bad minutes.</b> Judge each minute good or bad and set the SLO in minutes, so one failed request in a quiet minute counts once.',
              '<b>A minimum request count</b> on the short window, so three requests can’t page.', '<b>Longer windows</b>, accepting slower detection.'])),
    say='At low traffic a ratio from a small sample isn’t evidence, so I don’t page on it directly. I page when the lower bound of a Wilson confidence interval is above the threshold. For a 99% SLO that takes 24 failures in 100 requests, not 15. I add synthetic probes so quiet hours still produce events, and for very bursty services I’d set the SLO in bad minutes.',
    aws='CloudWatch alarms have “datapoints to alarm” (M out of N) and a setting for how to treat missing data, which covers the simple cases. For a real confidence bound, compute it in a Lambda or a recording rule and alarm on the result. CloudWatch Synthetics canaries supply the steady events.',
    iq=[('Why Wilson and not mean plus or minus z standard errors?',
         ['The simple interval assumes the sampling distribution is roughly normal, which fails for small samples and for rates near 0 or 1. That is exactly an error rate on a quiet service. It can even give a negative lower bound.',
          'Wilson stays between 0 and 1 and has sensible coverage with small n. It costs one slightly longer formula.']),
        ('99% confidence sounds strict. Doesn’t it delay pages?',
         ['Yes, a little, and that’s the trade. At 95% I’d page on fewer failures and be wrong more often at night. I’d pick the level from what a false page costs the on-call person against what a late page costs customers, and I’d say which z value I used.',
          'One detail: the book’s numbers use the two-sided 99% value, 2.576. The question is really one-sided, which would be 2.326 and need 170, 41 and 23 failures. The book’s choice is the cautious one.'])],
    quiz=[['99% SLO, 100 requests in the window. Failures needed to page at 99% confidence?', ['15', '24', '42'], 1, 'The lower bound for 24 of 100 is 14.8%, just over 14.4%. For 23 it is 14.0%.'],
          ['What happens to the number needed as traffic grows?', ['It moves toward the plain threshold', 'It moves away from it', 'It stays fixed'], 0, 'The interval narrows, so the observed rate you need approaches 14.4%.']],
    turn='Use the calculator in the Labs station: set 200 requests and switch between 99% and 95%. Then explain to an imaginary product manager, in two sentences, why 15 failures out of 100 didn’t page.',
    take=['Small samples make ratios unreliable.', 'Page on the lower confidence bound, not the observed rate.', '24 in 100, 42 in 200, 173 in 1,000 (99% SLO, 99% confidence).', 'Probes, bad minutes and minimum counts are the other tools.']))

# ══════════════════════════════════════════════════════════════ 4 ETL
L.append(dict(
    id='k-4', dot='4', part='K1', nav='An SLO for an ETL pipeline', h1='“What is the critical user journey of an ETL job, and what’s its SLO?”', practical=True,
    meta=meta(4, 'How do you do SRE for data pipelines?'),
    learn=['Name the user and the journey of a batch pipeline', 'Define freshness, completeness and correctness as SLIs', 'Measure all three without writing to the source', 'Explain why batch alerts are deadline-based, not burn-rate'],
    body=(
        h2('The journey belongs to whoever reads the data')
        + p('Nobody presses a button on a pipeline. Its user is the analyst, the finance dashboard or the model that reads the output. So the journey is: <b>when I need the data, it is there, complete and correct.</b> The job’s exit status isn’t part of it: a job can exit 0 with half the rows, or finish an hour after the meeting.')
        + table(['SLI', 'A good run', 'Measured by, read-only'],
                [['Freshness', 'Yesterday’s partition is published by 07:00', 'Publish time against the deadline; newest timestamp at source minus newest in the warehouse'],
                 ['Completeness', 'Row count matches the source within 0.1%, in both directions', 'Reconcile counts per partition'],
                 ['Correctness', 'Totals match; sampled real records match field by field', 'Reconcile sums; trace real records end to end; data-quality checks']])
        + p('One valid event per scheduled run. A run is good only if all three hold. With a daily job that is about 30 events a month, so a 99.9% target is meaningless: it would allow 0.03 bad days. “29 good days in 30” is an honest target.')
        + h2('What is different from a request-driven service')
        + ul(['<b>Retries help.</b> A run that fails at 02:00 and is rerun at 03:30 still meets a 07:00 deadline, provided the load is idempotent. The customer never noticed, so it is a good event.',
              '<b>Stages are serial.</b> Extract, transform, load and the scheduler multiply like any chain of hard dependencies, and each can have an internal deadline that adds up to 07:00.',
              '<b>No burn rate.</b> One event a day gives a burn-rate alert nothing to average. Alert on “the deadline is at risk” at 05:00, on reconciliation failing, and on the checker itself going quiet.'])
        + h2('If you may not write to the source')
        + p('A canary row is the textbook probe, and the source team will often say no. Read instead: compare high-water marks, reconcile per partition, follow real records. Or ask for a small heartbeat table that they own and update every minute. If you own the landing bucket or topic, inject canaries there and use the extract tool’s own lag metrics for the first hop.')
        + note('Why the high-water gap', 'If the shop is closed, nothing new arrives. “Now minus the newest row in the warehouse” grows all day and pages you. Source maximum minus warehouse maximum stays at zero, because both stopped together. The second hands-on shows both numbers side by side.')),
    say='The user of a pipeline is whoever reads the data, so the journey is fresh, complete, correct data by the time they need it. I measure three SLIs at the output: published by the deadline, row counts reconciled with the source, totals and sampled records matching. One run is one event, so the target is something like 29 good days in 30. I alert on deadline risk and reconciliation failures, early enough to rerun, not on burn rate.',
    aws='Glue or EMR for the job, Step Functions or MWAA to schedule it, S3 and Redshift or Athena for the output. Glue Data Quality or Deequ runs reconciliation rules. Publish freshness and row-ratio as CloudWatch custom metrics, alarm on them, and for CDC use DMS’s CDCLatencySource and CDCLatencyTarget.',
    iq=[('Why isn’t “the job succeeded” your SLI?',
         ['Because it measures the wrong thing in both directions. A job can exit 0 after silently dropping rows or applying a wrong transform; in my lab a run that lost 2% of rows reported success. And a job that failed at 02:00 and was rerun by 03:30 harmed nobody.',
          'I still alert on job failure, as a ticket, because it’s a useful early signal. The SLO is judged on the data, at the deadline.']),
        ('You can’t insert test records into the source. How do you probe the pipeline?',
         ['I read instead of writing. For freshness I compare the newest timestamp at the source with the newest in the output. For completeness I reconcile counts and totals per partition. For correctness I pick a few real recent records and check they arrive with the right values.',
          'Tracing a handful of records won’t find a small share of missing rows, so reconciliation is the main check. If the source team agrees, a tiny heartbeat table that they own gives a clean end-to-end signal too.']),
        ('How would this change for a streaming pipeline?',
         ['Freshness becomes lag: how far the output’s event time is behind the newest event, or consumer lag on the topic. The target becomes something like 99% of events available within five minutes.',
          'Traffic is steady, so request-style SLOs and burn-rate alerts work again. Completeness and correctness are still reconciliation, done over windows, and I’d watch for late and duplicate events specifically.'])],
    quiz=[['A daily job has a 99.9% availability target. How many failed runs a month does that allow?', ['3', '1', '0.03'], 2, '30 runs × 0.1% = 0.03. Choose a target that allows a whole number of bad days.'],
          ['The job lost 2% of rows. Which check finds it?', ['Tracing five real records', 'Reconciling row counts', 'The job’s exit status'], 1, 'A sample of five rarely contains a missing row; counts always show it.'],
          ['The source had no new rows for a day. Which freshness measure stays correct?', ['Now minus newest warehouse row', 'Source maximum minus warehouse maximum', 'Job duration'], 1, 'Both sides stop together, so the gap stays zero.']],
    turn='Pick a pipeline you know. Write its user, deadline, three SLIs with thresholds, and the two alerts that would have saved you last time it went wrong. Then run both hands-on tasks and compare.',
    take=['The journey: fresh, complete, correct data when the consumer needs it.', 'Judge the data at the deadline, not the job’s exit code.', 'Read-only checks: high-water gap, reconciliation, traced real records.', 'Batch alerts are about the deadline; reruns before it are good events.']))

# ══════════════════════════════════════════════════════════════ 5 probes
L.append(dict(
    id='k-5', dot='5', part='K1', nav='Synthetic probes', h1='“How do you use synthetic probes with a critical user journey?”', practical=True,
    meta=meta(5, 'Real-user monitoring or synthetics?'),
    learn=['Say what a probe adds that real traffic can’t', 'Script a whole journey safely, tagged as synthetic', 'Alert on probes without paging for one bad location', 'Know the limits, and watch the probe itself'],
    body=(
        h2('What a probe is for')
        + p('A synthetic probe is a scripted customer that walks the journey on a schedule and records whether each run worked and how long it took. Real traffic tells you how customers fared. A probe tells you whether the journey works right now, even when nobody is using it.')
        + table(['Gap in real-traffic SLIs', 'What the probe adds'],
                [['Quiet hours: two orders an hour can’t support a ratio', 'A steady event every few seconds or minutes'],
                 ['Rare but critical journeys: refunds, password reset', 'They are exercised all day'],
                 ['Your SLI starts at your own edge', 'DNS, certificates, CDN and routing are on the probe’s path'],
                 ['You learn about a break from the first customer', 'The probe hits it first, for example straight after a deploy']])
        + h2('Build it so it is safe to run every minute')
        + ul(['<b>Script the whole journey</b>, not a health check: log in, add to basket, pay with a test card, assert the confirmation and the time taken.',
              '<b>Tag the traffic</b> with a header or a test account, and use the tag to keep it out of customer SLIs, revenue and fulfilment. In the lab the edge records probe orders under their own route label.',
              '<b>Run from several locations</b> and page only when two or more agree, so one probe host’s network doesn’t wake anyone.',
              '<b>Watch the probe.</b> A dead probe’s last value was “success”. Alert when its last-run timestamp stops moving.'])
        + cb('alerts', 'record: probe:checkout_success:ratio_2m\nexpr:   avg_over_time(probe_success{journey="checkout"}[2m])\n\npage:   count(probe:checkout_success:ratio_2m < 0.5) >= 2        for 1m\nticket: count(probe:checkout_success:ratio_2m < 0.5) == 1        for 10m\nticket: time() - probe_last_run_timestamp_seconds > 120          for 2m')
        + note('The limit', 'A probe follows the paths you scripted, with tidy test data. Customers find the edge cases. So the real-traffic SLI stays the main SLO; the probe fills in quiet hours, rare journeys and the outside view.')),
    say='Real traffic tells me how customers fared; a probe tells me whether the journey works right now, including when nobody is using it. I script the whole journey with a test account, tag the traffic so it stays out of customer SLIs and revenue, run it from several locations and page only when two agree. And I alert when the probe itself stops reporting, because a dead probe looks healthy.',
    aws='CloudWatch Synthetics canaries run scripted journeys (Puppeteer or Selenium) on a schedule from several Regions and publish SuccessPercent and Duration. Alarm on them with a composite alarm for “two Regions failing”. CloudWatch RUM gives the real-user side. For single HTTP checks, Route 53 health checks are enough.',
    iq=[('You already measure every real request. Why pay for synthetic probes?',
         ['For the times real requests can’t tell me anything. At 3 a.m. there may be two orders an hour, so one failure is a 50% error rate and my burn-rate alerts are noise. A probe every minute from three places gives a steady signal.',
          'It also covers journeys that are rare but matter, like refunds, and the part of the path outside my system: DNS, certificates, the CDN. And it finds a broken deploy before a customer does.']),
        ('Your probe has been green all week and customers are complaining. What happened?',
         ['The probe only walks the path I scripted, with a clean test account. Customers may be hitting a payment method, a region, a product type or a data shape it never touches. That’s why the SLO is on real traffic and the probe only fills gaps.',
          'I’d also check the probe itself: is it still running, is it hitting production and the same edge as customers, and is a cache making its request easier than theirs?']),
        ('How do you stop probe orders polluting business data?',
         ['Every probe request carries a marker: a header, or a dedicated test account. The edge and the metrics pipeline use it to label that traffic separately, so SLI queries and revenue reports exclude it by default. Payment runs in the provider’s test mode, and fulfilment drops test accounts.',
          'I test that separation. In my lab a unit test asserts that after three probe runs and one customer order, the customer route counted exactly one request.'])],
    quiz=[['One of three probe locations is failing. What should happen?', ['Page immediately', 'A ticket after a while', 'Nothing, ever'], 1, 'One location is probably that probe’s own network. Two or more is the service.'],
          ['A probe process dies. What does probe_success show for the next few minutes?', ['0', 'Its last value, often 1', 'An error'], 1, 'The last sample is still returned until it goes stale, so alert on the last-run timestamp.'],
          ['Which is the main SLO for checkout?', ['The probe’s success rate', 'The real-traffic SLI at the edge', 'An average of the two'], 1, 'Real traffic is what customers experienced. The probe covers its blind spots.']],
    turn='Write the probe script for one journey you own as five numbered steps, each with the assertion it makes. Decide how the traffic is tagged and where that tag is filtered. Then run the lab below.',
    take=['Probes measure “does it work now”, real traffic measures “how did customers fare”.', 'Script the whole journey; tag it; keep it out of customer numbers.', 'Page on two locations, ticket on one, and alert on a silent probe.', 'The real-traffic SLI stays the SLO.']))

CARDS = [
    ['Where 14.4 comes from', '2% of a 30-day budget in one hour: 0.02 × 720 h ÷ 1 h. A pace, the same for every SLO.'],
    ['Burn rate to error rate', 'Error rate that pages = burn rate × (1 − SLO). 14.4× is 1.44% at 99.9% and 14.4% at 99%.'],
    ['Short window', 'About 1/12 of the long one. It proves the burn is still happening and clears the page minutes after the fix.'],
    ['rate vs increase vs irate', 'rate: per-second average over the window. increase: rate × window, can be fractional. irate: last two samples only.'],
    ['Why increase is fractional', 'Samples rarely cover the whole window, so Prometheus scales the rise up to the window’s edges.'],
    ['sum(rate()) not rate(sum())', 'rate must see each series to treat a counter drop as a reset; summing first hides it.'],
    ['Wilson lower bound', 'Page when the cautious end of the confidence interval is above the threshold: 24 failures in 100 for a 99% SLO.'],
    ['CUJ of a pipeline', 'Fresh, complete, correct data by the time the consumer needs it, measured at the output.'],
    ['High-water gap', 'Newest timestamp at source minus newest in the warehouse. Stays at zero when the source is quiet.'],
    ['Batch alerting', 'No burn rate with one run a day. Alert on deadline at risk, reconciliation failed, checker silent.'],
    ['What a probe adds', 'Events in quiet hours, rare journeys, the path outside your edge, and early warning after deploys.'],
    ['Probe paging rule', 'Two or more locations failing pages; one is a ticket; a probe that stops reporting is a ticket.'],
]
DRILLS = [
    ['Why 14.4, and why two windows?', ['14.4 is the burn rate that spends 2% of a 30-day budget in one hour: 0.02 × 720. It’s paired with a 5-minute window so the page shows the problem is still happening and clears after the fix. A second rule, 6× over 6 hours and 30 minutes, catches slower leaks. Multiply by the budget for the error rate: 1.44% at 99.9%.']],
    ['rate, increase or irate?', ['rate is the per-second average over the window and handles resets: use it for alerts and SLO ratios. increase is rate times the window, an estimate that can be fractional: use it when a person wants a count. irate uses the last two samples: graphs only.']],
    ['Set an SLO for a nightly ETL job.', ['The user is whoever reads the data, so the journey is fresh, complete and correct data by their deadline. SLIs: published by 07:00, row counts reconciled with the source, totals and sampled records matching. One run is one event, so target 29 good days in 30. Alert at 05:00 if it isn’t published, and on reconciliation failure, so there’s time to rerun.']],
    ['Where do synthetic probes fit?', ['They cover what real traffic can’t: quiet hours, rare journeys and the path outside your edge. Script the whole journey, tag the traffic so it stays out of customer SLIs, page when two locations fail, and alert when the probe goes quiet. The real-traffic SLI remains the SLO.']],
]
DRILLS = [[q, ''.join(f'<p>{a}</p>' for a in ans)] for q, ans in DRILLS]
