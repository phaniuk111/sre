# Hands-on track: one SLO for a journey that spans several services (SRE ch 8, ch 9, Appendix E; POC 31).
from extras import table, tiles
from extras2 import pic, p, ul
from pe import h2, h3, note
from obs1 import box, arrow

L = []
REPO = 'https://github.com/phaniuk111/sre/tree/main/poc-31-checkout-journey-slo-lab'


def meta(n, src, poc='POC 31'):
    return f'<span class="chip">Hands-on · SLO journey</span>Lesson {n} of 5 · {src}' + (f' · {poc}' if poc else '')


def cb(fn, src, term=False):
    esc = src.strip('\n').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'<div class="cb{" term" if term else ""}"><div class="fn">{fn}</div>'
            f'<button type="button" class="copy">Copy</button><pre><code>{esc}</code></pre></div>')


def see(text):
    return f'<details class="ans"><summary>What you should see</summary><p>{text}</p></details>'


# ══════════════════════════════════════════════════════════════ 1 measure the journey
_arch = (box(10, 20, 100, 44, 'Browser', '') + box(150, 20, 150, 44, 'Load balancer', 'every attempt', 'hl')
         + box(340, 20, 160, 44, 'Checkout API', 'calls in turn')
         + arrow(112, 42, 148, 42) + arrow(302, 42, 338, 42)
         + ''.join(box(10 + i * 125, 120, 112, 44, n, s) for i, (n, s) in enumerate([('Cart', 'hard'), ('Inventory', 'hard'), ('Payment', 'hard'), ('Orders DB', 'hard')]))
         + ''.join(arrow(420, 66, 66 + i * 125, 118) for i in range(4))
         + box(260, 200, 130, 40, 'Card provider', 'third party') + arrow(316, 166, 320, 198)
         + box(10, 200, 160, 40, 'Recommendations', 'soft: has a fallback', 'dash') + arrow(400, 66, 120, 198, '', 0, 0, True)
         + box(420, 200, 80, 40, 'Email', 'via queue', 'dash')
         + '<text x="225" y="88" text-anchor="middle" class="m" style="font-size:12px">the journey SLI is measured here</text>')
L.append(dict(
    id='j-1', dot='1', part='J1', nav='Measure the journey', h1='One SLO for a journey: measure it where the customer is',
    meta=meta(1, 'SRE ch 8 “Critical User Journeys”, ch 9'),
    learn=['What a critical user journey (CUJ) is, and why it gets one SLO', 'Why the journey SLI is measured at the edge, not by averaging services', 'How to define valid and good events in writing'],
    body=(
        p('Press <b>Place order</b> in an online shop and a chain starts: checkout checks the basket, reserves stock, charges the card through a payment provider and saves the order. Five teams own those pieces. The customer sees one thing: did my order go through, quickly? Your SRE book calls this a <b>critical user journey</b>, a series of steps a user takes to do something that matters to them, and it gets one SLO.')
        + pic(520, 250, _arch, 'The shop used in this track and in POC 31. Solid boxes must all work for an order; dashed ones are optional or happen afterwards.',
              'Checkout journey: browser to load balancer to checkout, which calls cart, inventory, payment and orders in turn; recommendations is soft; email goes through a queue.')
        + h2('Measure where every attempt passes')
        + p('The SLI is the share of events that were good. For checkout an event is one attempt to place an order, and a good one ends with a confirmed order in under two seconds. Count them at the load balancer, gateway or ingress: every attempt passes there, including the ones that fail before any service runs. Add client-side measurement later (it needs a looser target, because phones and patchy networks add noise) and a synthetic probe that places a real test order. The book warns that probing only the home page tests a fraction of what matters.')
        + h2('Why not average the services’ own numbers?')
        + ul(['<b>Unseen failures.</b> A crashed checkout pod never records the requests it dropped; the load balancer records the 502 it sent back.',
              '<b>Absorbed failures.</b> A payment call that failed and was retried successfully looks bad on payment’s dashboard and was fine for the customer.',
              '<b>Accidental weighting.</b> Inventory might answer ten calls per order and payment one, so an average of success rates weights them by accident.'])
        + p('Service numbers still matter: they show where a problem is, and each team uses them for its internal SLO (lesson 2).')
        + h2('Write down what counts')
        + table(['Event', 'Valid?', 'Good?'],
                [['Order confirmed (200) in 0.4 s', 'Yes', 'Yes'], ['Card declined, answered 200 “declined” in 0.3 s', 'Yes', 'Yes: a correct answer'],
                 ['Order confirmed, but in 3.4 s', 'Yes', 'No: slow'], ['502 from the load balancer: no checkout pod ready', 'Yes', 'No'],
                 ['429 from your own rate limiter during a sale', 'Yes', 'No: your system turned them away'], ['400 malformed form', 'No: the customer sent something broken', ''],
                 ['Health checks and load tests', 'No: not customers', ''], ['Recommendations panel failed, order confirmed in 1.1 s', 'Yes', 'Yes: soft dependency']])),
    say='I set one SLO per critical user journey and measure it where every attempt passes, the load balancer or gateway, as confirmed outcomes within a latency threshold over valid attempts. I don’t average service success rates: a crashed service can’t count what it dropped, retried failures never reached the customer, and the average weights services by call volume. Service metrics are for diagnosis and internal SLOs.',
    aws='On EKS, measure at the ingress controller or gateway (route and status labels) and scrape it with ADOT or the AMP managed collector. An ALB’s CloudWatch metrics have no per-route detail, so they can’t give a per-journey SLI by themselves. Add CloudWatch RUM for the client view and a CloudWatch Synthetics canary that places a test order.',
    iq=[('Checkout calls five services and each has a good dashboard. Why not average their success rates to get checkout’s SLI?',
         ['Because the customer experiences one thing: did my order go through, quickly? I’d measure that where every attempt passes, at the load balancer or gateway, as confirmed orders under two seconds divided by valid attempts.',
          'Averaging service numbers goes wrong three ways. A service can’t count requests that never reached it, like the 502s while its pods were crashing. A failure one service records may have been retried and never reached the customer. And services handle different numbers of calls per order, so an average weights them by accident.',
          'I still use the service metrics, to find where a problem is and as each team’s internal SLO, just not as the journey’s SLI.'])],
    quiz=[['Checkout’s pods were OOM-killed for 20 minutes; the load balancer returned 502 to 4% of attempts. Does checkout’s own success metric show it?', ['Yes, checkout owns the journey', 'No, the killed pods never counted those requests', 'Yes, after the pods restart'], 1, 'Only the load balancer saw those attempts. POC 31 exercise 2 shows it live.'],
          ['Which event should be left out of valid events?', ['A 429 from your own rate limiter', 'Load-test traffic before a sale', 'A request that timed out at the load balancer'], 1, 'Valid events are real customer attempts; your own 429s and timeouts are bad events, not excluded ones.']],
    turn=f'Clone the repo and start <a href="{REPO}">POC 31</a> (<code>make prometheus && make up</code>). After three minutes run <code>python lab.py status</code>, then do exercise 1 in EXERCISES.md: compute the journey SLI by hand from <code>edge_request_duration_seconds_count</code> and compare it with the recording rule.',
    take=['One SLO per critical user journey, measured where every attempt passes.', 'Never average service SLIs into a journey SLI.', 'Write down valid and good events before you write any query.']))

# ══════════════════════════════════════════════════════════════ 2 the target and the ceiling
_calc = '''<div class="wid" id="jc"><b>Checkout’s ceiling: change the design</b>
<p>Set each piece’s availability and whether an order needs it. The bar shows how much of the error budget the hard pieces use between them.</p>
<div class="jcrow"><label for="jc_t">Journey target</label><select id="jc_t"><option value="0.999" selected>99.9%</option><option value="0.9995">99.95%</option><option value="0.995">99.5%</option></select></div>
<div id="jc_rows"></div><svg id="jc_svg" viewBox="0 0 640 70" role="img" aria-label="Error budget used by the hard dependencies"></svg>
<p class="res" id="jc_out"></p></div>
<script>(function(){var D=[["Checkout’s own code",.9999,1],["Cart",.9999,1],["Inventory",.9995,1],["Payment",.9995,1],["Orders DB",.9999,1],["Recommendations",.995,1]],A=[.99,.995,.999,.9995,.9999,.99999];
var rows=document.getElementById("jc_rows");
D.forEach(function(d,i){var r=document.createElement("div");r.className="jcrow";r.innerHTML='<label>'+d[0]+'</label><select data-i="'+i+'">'+A.map(function(a){return '<option value="'+a+'"'+(a===d[1]?' selected':'')+'>'+(a*100).toFixed(a>=.9999?3:2).replace(/0+$/,"").replace(/\\.$/,"")+'%</option>'}).join("")+'</select><select data-h="'+i+'"><option value="1" selected>Hard: every order needs it</option><option value="0">Soft: has a fallback</option></select>';rows.appendChild(r)});
function draw(){var t=+document.getElementById("jc_t").value,b=1-t,c=1,used=0,s="",W=600,sc=W/(2*b),cols=["#00a05a","#0a5cff","#7a3cff","#e6a100","#007c85","#be185d"];
D.forEach(function(d,i){if(!d[2])return;c*=d[1];var w=Math.min((1-d[1])*sc,W-used);if(w>0){s+='<rect x="'+(20+used)+'" y="14" width="'+w.toFixed(1)+'" height="26" style="fill:'+cols[i]+'"><title>'+d[0]+'</title></rect>';used+=w}});
var bx=20+b*sc;s='<rect x="20" y="14" width="'+W+'" height="26" rx="4" style="fill:var(--panel2);stroke:var(--rule2)"/>'+s+'<line x1="'+bx+'" y1="6" x2="'+bx+'" y2="48" style="stroke:var(--red);stroke-width:2.5"/><text x="'+bx+'" y="62" text-anchor="middle" style="fill:currentColor;font-size:12px">error budget</text>';
document.getElementById("jc_svg").innerHTML=s;var share=(1-c)/b,ok=c>=t-1e-12;
document.getElementById("jc_out").innerHTML='Ceiling <b>'+(c*100).toFixed(3)+'%</b>: '+(ok?'meets the target; the hard pieces use '+Math.round(share*100)+'% of the budget.':'<b>below the target</b>; the hard pieces alone use '+Math.round(share*100)+'% of the budget. Make one soft, or ask more of it.')}
rows.addEventListener("change",function(e){var i=e.target.dataset.i,h=e.target.dataset.h;if(i!=null)D[i][1]=+e.target.value;if(h!=null)D[h][2]=+e.target.value;draw()});
document.getElementById("jc_t").addEventListener("change",draw);draw()})();</script>'''
L.append(dict(
    id='j-2', dot='2', part='J1', nav='What the design can meet', h1='What target can the design actually meet?',
    meta=meta(2, 'SRE ch 8, Appendix E'),
    learn=['Who agrees the target, and what data to bring', 'Serial dependencies multiply; parallel ones multiply failures', 'The rule of the extra nine, and splitting the budget into internal SLOs', 'Why latency percentiles don’t add'],
    body=(
        h2('Who sets the number')
        + p('Your SRE book is clear that engineering doesn’t pick the target alone: business, product, engineering and operations agree it together, because missing it has business consequences. Its example is three nines for everything except checkout at four, and it finds fewer than five top-level SLOs enough for most services. Bring two things to that meeting: what the edge has measured over recent months, and the design’s <b>ceiling</b>, the best availability the way it’s built allows even if every team does its job.')
        + h2('Hard dependencies multiply')
        + p('A hard dependency is one every order needs. With independent failures, multiply success rates: five at 99.9% give about 99.5%. For small numbers, add the failure rates instead. Appendix E’s example: a service calling an 80% and a 90% dependency in turn can reach 72% at most; calling both in parallel and taking the first answer (hedging), it fails only when both fail, so it can reach 98%. A soft dependency, one with a fallback, leaves the product entirely.')
        + _calc
        + h2('The rule of the extra nine')
        + p('Each critical dependency should be about one nine better than the service relying on it: 99.99% for a 99.9% checkout. Each then uses about a tenth of the budget. With five, half the budget is gone before checkout’s own bugs, which is why removing a hard dependency is often the cheapest reliability win.')
        + h2('Split the budget into internal SLOs')
        + p('At 99.9% over 30 days the budget is about 43 minutes of total outage. Turn each share into a number: 99.99% by default; if the card provider’s record is 99.97%, give payment a deliberate third (0.1% ÷ 3 ≈ 0.033%, an internal SLO of about 99.967%) and squeeze the rest. Measure each internal SLO as the success rate of checkout’s calls to that dependency. The book describes internal SLOs as covering smaller pieces of a journey with no money changing hands: a team that misses one puts engineering time into the fix. With many dependencies, set the journey and core-component SLOs first and negotiate the middle.')
        + h2('Latency doesn’t add up')
        + p('The 99th percentile is the time 99% of requests beat. If cart’s p99 is 300 ms and payment’s 800 ms, checkout’s p99 can be above or below 1.1 s, depending on whether slow calls land on the same orders. In POC 31, with 2% slow calls on two dependencies, each p99 read about 1.5 s and the journey’s 1.74 s, nowhere near their 3-second sum. Budget time per step, measure the journey end to end.')),
    say='Before agreeing a target I check the design’s ceiling: hard dependencies multiply, so five at 99.9% cap the journey near 99.5%. I give each critical dependency an internal SLO about one nine tighter, measured from the caller’s side, make dependencies soft where a fallback exists, and never add latency percentiles; I measure journey latency at the edge.',
    aws='On AWS the same arithmetic applies to managed services: check each service’s published availability (and your own measured record) before promising a journey SLO. Multi-AZ and multi-provider designs are the hedged case, but only if the copies share nothing that fails together.',
    iq=[('The payment team asks what internal SLO they should hold so checkout can meet 99.9%. What do you tell them?',
         ['Payment is a hard dependency: no payment, no order. Checkout’s 99.9% lets 0.1% of checkouts fail, about 43 minutes’ worth a month, and that has to cover checkout’s own deploys and every other dependency too.',
          'By the extra-nine rule payment should hold 99.99%, which uses about a tenth of the budget. If the provider’s record makes that impossible, we give payment a bigger share on purpose, say a third (about 99.967%), and squeeze the others.',
          'It’s measured as the success rate of checkout’s calls to payment. If even that isn’t realistic, we make payment softer, for example by accepting the order and confirming payment shortly after, or we lower checkout’s target.'])],
    quiz=[['Four hard dependencies, each 99.95%, independent failures. Best the journey can do?', ['99.95%', 'About 99.8%', 'About 99.9%'], 1, '0.9995⁴ ≈ 0.998.'],
          ['Two independent replicas at 99% each, hedged (first answer wins). Availability?', ['99%', '98%', '99.99%'], 2, 'It fails only when both fail: 0.01 × 0.01.']],
    turn='In the ceiling widget, start from the defaults (below target). Make the fewest changes that reach 99.9%, then do POC 31 exercise 6 (recommendations soft, then hard) and watch the same effect in live traffic.',
    take=['Hard dependencies multiply; fallbacks and hedging raise the ceiling.', 'Dependencies need internal SLOs about one nine tighter, measured from the caller.', 'Percentiles don’t add: measure journey latency end to end.']))

# ══════════════════════════════════════════════════════════════ 3 what breaks the maths
_retry = ''
for row, (y0, bad, ok_retry, lab) in enumerate([(30, [6, 19, 33, 47, 55], True, 'Scattered failures: the retry succeeds'), (120, list(range(24, 29)), False, 'The same rate as an outage: the retry fails too')]):
    _retry += f'<text x="10" y="{y0 - 10}" class="b" style="font-size:13px">{lab}</text>'
    for i in range(60):
        b = i in bad
        _retry += f'<rect x="{10 + i * 10}" y="{y0}" width="8" height="20" rx="2" style="fill:{"var(--red)" if b else "var(--panel2)"};stroke:var(--rule2);stroke-width:.5"/>'
        if b:
            _retry += f'<rect x="{10 + i * 10}" y="{y0 + 30}" width="8" height="10" rx="2" style="fill:{"var(--green)" if ok_retry else "var(--red)"}"/>'
L.append(dict(
    id='j-3', dot='3', part='J1', nav='What breaks the maths', h1='What breaks the simple maths',
    meta=meta(3, 'SRE ch 8; Appendix E assumptions'),
    learn=['When retries help and when they don’t', 'Shared parts that break independence', 'Async work, third parties, and who owns the journey SLO'],
    body=(
        p('The multiplication rules assume each failure is independent of the others. Real systems break that assumption in predictable ways, and interviewers ask about all of them.')
        + h2('Retries help only when failures are independent')
        + pic(620, 180, _retry, 'Each cell is a slice of time; red is a failed call and the small cell underneath is its retry. The failure rate is the same in both rows.',
              'Two rows of time slices: scattered failures whose retries succeed, and a block outage whose retries fail.')
        + p('If the card provider drops 0.5% of calls at random, one retry means a payment fails only when both attempts fail: 0.005 × 0.005 = 0.0025%. If the same 0.5% comes as outages, the retry lands in the same outage and fails too. Retries also add load just when a dependency struggles and add time to the journey: cap them, back off, and use an idempotency key so a repeated charge is ignored. In POC 31, 2% random payment failures burned budget at about 20×; one retry brought the journey down to 0.4× while payment, seen from checkout, still showed about 98%.')
        + h2('Check that “independent” is true')
        + p('Two inventory replicas that read one database, run on one network or ship through one pipeline fail together. Treat them as one dependency no better than the part they share, not as a 99.9999% pair.')
        + h2('Async work gets its own SLI')
        + p('The confirmation email goes through a queue after the order is saved. The order succeeded even if the email is late, so email isn’t in the checkout SLI. Give it a freshness SLI: 99% of confirmation emails sent within five minutes of the order.')
        + h2('Third parties count against you')
        + p('The card provider’s failures are your customers’ failures, so they stay in the SLI. You can’t fix the provider, so you design around it (careful retries, a second provider, confirm-payment-later) and set the target from its measured record, not its contract.')
        + h2('One team owns the journey SLO')
        + p('Usually the team that owns checkout, with SRE support, owns the journey SLO and its error budget policy. Dependency teams own their internal SLOs. Policies often carve out exceptions: Google’s example lets a team keep releasing when another team’s outage spent the budget and that team has frozen its own releases. Your SRE book adds that a policy usually applies only to committed SLOs, and that a monthly reset keeps one bad January from freezing releases all year.')),
    say='Retries rescue scattered failures, not outages, and they hide failures from the journey, not from the dependency’s own SLI. Shared databases or networks break the independence that multiplication assumes. Async work gets its own freshness SLI, third-party failures stay in mine, and the journey’s owner holds the error budget policy while dependencies hold internal SLOs.',
    aws='Retries with exponential backoff and jitter are built into the AWS SDKs; check the defaults before adding your own on top, or retries multiply. For multi-AZ “redundancy”, look for shared parts: one RDS primary, one NAT gateway, one deploy pipeline.',
    iq=[('A dependency fails 1% of calls. A teammate proposes three retries to make it disappear. What do you say?',
         ['It depends on how the failures arrive. If they’re scattered and independent, one retry already cuts the dependency’s impact to about 0.01% of orders; three is overkill and adds load and latency.',
          'If the 1% comes as outages, retries a few hundred milliseconds apart all land inside the same outage, so they barely help and they pile load onto a struggling service.',
          'So I’d look at the failure pattern first, cap retries at one or two with backoff and jitter and an idempotency key, and for outages invest in a fallback or a second provider instead.'])],
    quiz=[['Two replicas at 99.9% each, hedged, both reading one 99.95% database. Best availability?', ['About 99.9999%', 'About 99.95%', '99.9%'], 1, 'The shared database fails both at once, so it sets the limit.'],
          ['Emails are delayed two hours by the mail provider. Effect on the checkout SLO?', ['None; it spends the email freshness SLO', 'Every order in that window is bad', 'Exclude those orders'], 0, 'The orders succeeded on time; async work has its own SLI.']],
    turn='Do POC 31 exercises 3–5: 2% random payment failures, then one retry, then the same rate as outages. Note the burn rate and payment’s own success rate each time.',
    take=['Retries multiply away independent failures only.', 'Look for shared parts before you trust a parallel design.', 'Async work, third parties and ownership each need an explicit decision.']))

# ══════════════════════════════════════════════════════════════ 4 PromQL and alerts
L.append(dict(
    id='j-4', dot='4', part='J1', nav='PromQL and alerts', h1='The journey SLI and burn-rate alerts in PromQL',
    meta=meta(4, 'SRE ch 8 “Automatic Alert Configurations”; Mastering Prometheus ch 13'),
    learn=['Recording rules for good, valid and error ratio', 'The histogram bucket trap in Prometheus 3', 'Multiwindow burn-rate pages and tickets', 'Rolling several SLIs into one: the bad-minute rule'],
    body=(
        p('An SLI is a ratio of two rates: good events per second over valid events per second. Latency comes from a histogram: each <code>_bucket</code> series with label <code>le</code> counts requests at or under that boundary, and <code>_count</code> counts all of them. These are the rules POC 31 runs:')
        + cb('rules/checkout-slo.yml', '''- record: journey:checkout_good:rate5m
  expr: sum(rate(edge_request_duration_seconds_bucket{route="POST /checkout", code=~"2..", le=~"2(\\\\.0)?"}[5m]))
- record: journey:checkout_valid:rate5m
  expr: sum(rate(edge_request_duration_seconds_count{route="POST /checkout", code!="400"}[5m]))
- record: journey:checkout_error_ratio:rate5m
  expr: 1 - journey:checkout_good:rate5m / journey:checkout_valid:rate5m
# repeated for 30m, 1h, 6h, 3d and 30d''')
        + note('The le trap', '<p>A bucket only exists where the histogram has a boundary (defaults: 1, 2.5, 5 s), and Prometheus 3 stores bucket labels in float form, <code>le="2.0"</code>, even when a client sends <code>2</code>. An exact <code>le="2"</code> then matches nothing: the good rate is empty, the error ratio is empty and no alert can ever fire. We found this while building POC 31; the rules match <code>le=~"2(\\\\.0)?"</code>.</p>', 'warn')
        + h2('Burn-rate alerts')
        + p('Burn rate is the error ratio divided by the budget ratio (0.1% for 99.9%). A burn of 14.4 spends 2% of a 30-day budget in an hour. The fast page needs both the last hour and the last five minutes above it: the hour proves it matters, the five minutes stops the page soon after a fix. A second page at 6× over 6 hours and 30 minutes, and a ticket at 1× over 3 days and 6 hours, catch slower leaks. Your SRE book says Google now generates these from each SLO definition, and uses a Wilson score test instead of fixed thresholds for services under about 100 requests an hour.')
        + cb('rules/checkout-slo.yml', '''- alert: CheckoutBudgetBurnFast
  expr: |
    journey:checkout_error_ratio:rate1h > (14.4 * 0.001)
    and
    journey:checkout_error_ratio:rate5m > (14.4 * 0.001)
  for: 2m
  labels: {severity: page, journey: checkout}''')
        + table(['Rule', 'Long window', 'Short window', 'Burn', 'Budget used', 'Action'],
                [['Fast', '1 h', '5 min', '14.4×', '2% in an hour', 'Page'], ['Slow', '6 h', '30 min', '6×', '5% in six hours', 'Page'], ['Leak', '3 d', '6 h', '1×', '10% in three days', 'Ticket']])
        + h2('Test the rules like code')
        + p('POC 31 pins each behaviour with promtool unit tests: healthy traffic stays quiet, a 15-minute outage pages and clears five minutes after the fix, a two-minute blip pages nobody, slow successes burn budget, 400s aren’t valid, and a missing 2-second bucket leaves the SLI empty.')
        + cb('terminal', 'cd rules && promtool test rules checkout-slo.test.yml', term=True)
        + h2('Several requests, no single edge')
        + p('When a journey is several requests with no single one covering it, multiply each step’s ratio, or use the rule from your SRE book’s chapter 9: judge the journey minute by minute and count a minute as bad if any step’s SLI was bad. That is a window-based SLO, the kind Mastering Prometheus builds with <code>bool</code> and a subquery:')
        + cb('solutions/bad-minute.yml', '''- record: journey:checkout_bad_minute:bool
  expr: max(dep:checkout_dependency_error_ratio:rate1m{dep!="recommendations"} > bool 0.001)
- record: journey:checkout_good_minutes:ratio_1h
  expr: 1 - avg_over_time(journey:checkout_bad_minute:bool[1h])''')),
    say='I record good and valid rates at the edge for every alert window, page when the 1-hour and 5-minute burn rates both exceed 14.4×, page again at 6× over 6 hours, ticket at 1× over 3 days, and test the rules with promtool, including a check that the SLI returns data at all, because on Prometheus 3 an exact le="2" matcher silently matches nothing.',
    aws='Load the same rule files into Amazon Managed Service for Prometheus as rule group namespaces and route severity=page and severity=ticket through the AMP alert manager to SNS and Incident Manager. POC 31’s terraform/amp.tf does exactly this.',
    iq=[('Your burn-rate alert didn’t fire during a real outage. What do you check?',
         ['First whether the SLI returns data at all: run the good and valid recording rules on their own. A matcher that finds nothing, such as le="2" when Prometheus 3 stores le="2.0", or a renamed route label, makes the error ratio empty, and an empty comparison never fires.',
          'Then the windows and thresholds: was the outage long enough for the 1-hour window to cross 14.4× with the for duration? A 10-minute outage at 100% does; a 10-minute outage at 5% doesn’t, by design.',
          'Finally the pipeline: did Prometheus evaluate the rules (rule evaluation failures), was the alert routed (Alertmanager receivers, silences, inhibition)? Then I’d add a promtool test that reproduces the outage so it can’t regress.'])],
    quiz=[['SLO 99.9%, last-hour error ratio 1.8%, last 5 minutes 0.2% after a fix. Does the fast page fire?', ['Yes, the hour is above 1.44%', 'No, the 5-minute window is below 1.44%', 'Only after 6 hours'], 1, 'Both windows must be above 14.4 × 0.1% = 1.44%.'],
          ['Why match le=~"2(\\.0)?" instead of le="2"?', ['Regex is faster', 'Prometheus 3 stores the label as 2.0, so an exact "2" matches nothing', 'To include the 2.5 s bucket'], 1, 'Label matching is exact text; POC 31 exercise 9 shows the empty result.']],
    turn='Run <code>make rules-test</code> in POC 31. Then break one rule on purpose (change the matcher to <code>le="2"</code>), rerun, and read which test catches it.',
    take=['An SLI is good rate ÷ valid rate, recorded for every alert window.', 'Fast page: 1 h and 5 min above 14.4×; test the rules with promtool.', 'Check that every SLI series returns data.']))

# ══════════════════════════════════════════════════════════════ 5 the lab
L.append(dict(
    id='j-5', dot='5', part='J1', nav='Lab: build and break it', h1='Lab: run the shop, break it, watch the SLO react',
    meta=meta(5, 'About 90 minutes · verified end to end with Prometheus 3.5'),
    learn=['Start the shop, load and Prometheus on your laptop', 'Predict, break, observe: eight exercises', 'Write an internal SLO and the bad-minute rule yourself'],
    body=(
        p(f'<a href="{REPO}">POC 31</a> runs this track’s checkout for real: an edge (the load balancer), checkout and five dependencies, about ten orders a second, and Prometheus running the rules from lesson 4. You change things from the terminal with <code>lab.py</code>. With Docker you also get a Grafana dashboard. For each exercise, write your prediction down before you run it.')
        + cb('terminal', '''git clone https://github.com/phaniuk111/sre && cd sre/poc-31-checkout-journey-slo-lab
pip install prometheus_client
make prometheus        # one time: prometheus + promtool into ./bin
make up                # shop + load + Prometheus on :9090   (or: make compose-up, adds Grafana on :3000)
python lab.py status   # after about 3 minutes''', term=True)
        + note('Windows are real', '<p>A page needs its condition to hold for 2 minutes and stops about 5 minutes after the fix. Wait, and reset each change before the next exercise (<code>python lab.py chaos &lt;service&gt; --reset</code>).</p>')
        + h3('1 · Kill checkout: who notices?')
        + cb('terminal', 'python lab.py stop checkout\nsleep 150; python lab.py status\npython lab.py start checkout', term=True)
        + see('The journey SLI falls and the edge answers 502, but checkout’s own metric still reads 100%: it isn’t being scraped and never received those requests. The fast page fires after 2 minutes and stops about 5 minutes after the restart, while the 1-hour burn rate is still huge.')
        + h3('2 · Payment fails 2% of calls, then one retry')
        + cb('terminal', 'python lab.py chaos payment --error-rate 0.02 --mode random\nsleep 180; python lab.py status\npython lab.py config --retries payment=1\nsleep 330; python lab.py status', term=True)
        + see('Without the retry the burn rate is about 20× and it pages. With one retry the journey drops to about 0.4× (we measured 0.036% errors), but payment, as checkout sees it, still shows about 98%.')
        + h3('3 · The same rate as outages')
        + cb('terminal', 'python lab.py chaos payment --error-rate 0.1 --mode outage --period-s 300\nsleep 330; python lab.py status', term=True)
        + see('A block of 503s every five minutes; with the retry still on, we lost about 9% of orders over a five-minute window. The retry lands in the same outage.')
        + h3('4 · Recommendations: soft, then hard')
        + cb('terminal', 'python lab.py chaos recommendations --error-rate 0.05\nsleep 120; python lab.py status\npython lab.py config --recommendations hard\nsleep 330; python lab.py status', term=True)
        + see('While soft, recommendations show about 95% and the journey is untouched. Once hard, the journey loses about 5% of orders and pages.')
        + h3('5 · Slow successes and a long tail')
        + cb('terminal', 'python lab.py chaos payment --latency-ms 2300               # (a)\npython lab.py chaos payment --reset\npython lab.py chaos cart --slow-rate 0.02 --slow-ms 1500    # (b)\npython lab.py chaos payment --slow-rate 0.02 --slow-ms 1500', term=True)
        + see('(a) Every order is a 200, yet the SLI collapses: a slow success is a bad event. (b) We measured cart p99 1.47 s, payment 1.52 s and the journey 1.74 s, nowhere near the 3-second sum.')
        + h3('6 · Write payment’s internal SLO')
        + p('Write recording rules and a fast-burn alert for payment at 99.99% (budget ratio 0.0001) from <code>checkout_dependency_attempts_total{dep, outcome}</code>, routed as a ticket to the payment team. Load it and repeat exercise 2 with the retry on.')
        + see('The journey stays healthy and its page stays quiet, but PaymentInternalSLOBurnFast fires with owner=payment-team. Compare with solutions/internal-slos.yml.')
        + h3('7 · The le trap')
        + cb('terminal', '''python lab.py promql 'count by (le) (edge_request_duration_seconds_bucket)'
python lab.py promql 'sum(rate(edge_request_duration_seconds_bucket{le="2"}[5m]))\'''', term=True)
        + see('The bucket is stored as le="2.0", and le="2" returns nothing.')
        + h3('8 · The bad-minute rule')
        + p('Write a 0/1 bad-minute rule from the per-dependency error ratios (ignore recommendations) and the share of good minutes in the last hour, then run <code>python lab.py chaos inventory --error-rate 0.005</code>.')
        + see('The request-based SLI barely moves (0.5% of orders fail), but most minutes turn bad, because at ten orders a second almost every minute contains a failure. Compare with solutions/bad-minute.yml.')
        + p('EXERCISES.md in the repo has all eleven, including reading the SLI by hand and deploying the same rules to Amazon Managed Service for Prometheus with Terraform.')),
    say='I’ve built this end to end: a shop with five dependencies, a journey SLI at the edge, multiwindow burn-rate alerts tested with promtool, and chaos experiments showing that retries fix scattered failures but not outages, that soft dependencies raise the ceiling, and that slow successes burn budget too.',
    aws='terraform/amp.tf in POC 31 creates an AMP workspace, loads the journey and internal SLO rules as rule group namespaces, and routes pages and tickets to two SNS topics. Point a local Prometheus at it with remote_write and SigV4, then terraform destroy when you finish.',
    iq=[('Tell me about a time you tested your alerting.',
         ['In my SLO lab I wrote the journey SLI and burn-rate alerts as recording and alerting rules, then pinned their behaviour with promtool unit tests: an outage pages and clears five minutes after the fix, a two-minute blip pages nobody, slow successes burn budget.',
          'Then I ran the real system and injected faults: I killed checkout and watched the edge SLI drop while checkout’s own metric stayed at 100%, and I compared random failures with outages to show that retries only help the first.',
          'The most useful finding was a silent failure: on Prometheus 3 an exact le="2" matcher returns nothing, so the alert could never fire. Now every SLI rule has a test that it returns data.'])],
    quiz=[['In exercise 2, after adding one retry, what does payment’s own success rate (seen from checkout) show?', ['About 99.96%', 'About 98%, unchanged', '100%'], 1, 'Retries hide failures from the journey, not from the dependency’s internal SLO.'],
          ['In exercise 3, why doesn’t the retry help?', ['It isn’t enabled', 'The retry lands inside the same outage', 'Outage mode disables retries'], 1, 'Retries rescue independent failures only.']],
    turn='Do all eight exercises, writing your prediction before each one. Then explain exercise 2’s result out loud in under a minute, as if to an interviewer.',
    take=['Measure, break, observe: the numbers you can quote come from your own runs.', 'Retries, soft dependencies and slow tails each move the SLO differently.', 'Test that every SLI returns data.']))

CARDS = [
    ['Critical user journey (CUJ)', 'A series of steps a user takes to do something that matters to them; it usually crosses several services and gets one SLO.'],
    ['Where to measure a journey SLI', 'Where every attempt passes: the load balancer, gateway or ingress, plus client-side and a synthetic probe later.'],
    ['Why not average service SLIs', 'Unseen failures (crashed services), absorbed failures (retries), and accidental weighting by call volume.'],
    ['Design ceiling', 'The best availability a design allows: multiply the hard dependencies’ success rates.'],
    ['Rule of the extra nine', 'Critical dependencies about one nine better than the service relying on them: 99.99% for 99.9%.'],
    ['Internal SLO', 'A dependency’s target for its callers, measured as the success rate of their calls to it; missing it is a ticket for that team.'],
    ['Retries and outages', 'One retry turns independent failure rate f into f²; in an outage it changes almost nothing.'],
    ['le trap in Prometheus 3', 'Bucket labels are stored as le="2.0"; an exact le="2" matches nothing and the alert never fires.'],
    ['Bad-minute rule', 'Judge the journey per minute: a minute is bad if any step’s SLI was bad (SRE book ch 9).'],
]
DRILLS = [
    ['Set an SLO for a checkout that calls five services.', ['Agree one SLO for the journey with product and business, measured at the edge as confirmed orders under two seconds over valid attempts. Check the design’s ceiling by multiplying hard dependencies, make what you can soft, and give each dependency an internal SLO about one nine tighter, measured from checkout’s calls.', 'Alert on burn rate with paired windows (1 h and 5 min at 14.4× pages, 3 d and 6 h at 1× tickets), test the rules with promtool, and give async work like email its own freshness SLI.']],
    ['Your journey SLO looks fine but one dependency keeps failing. Is that a problem?', ['Maybe not for customers: retries or fallbacks may be absorbing it. But it shows up on that dependency’s internal SLO, measured from the caller, and it should open a ticket for that team. It also means the journey has less headroom: if failures turn into outages, retries stop helping.']],
]
DRILLS = [[q, ''.join(f'<p>{a}</p>' for a in ans)] for q, ans in DRILLS]
