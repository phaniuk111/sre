# Prometheus chapter 4: Service discovery and relabeling: deciding what to scrape and what to call it

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-4`. Code: POC 22 · 6. Read: full text, one pass; all figures seen.*

## Summary

In a cloud environment targets change by the minute, so a fixed list of hosts goes stale immediately. Prometheus ships more than two dozen **service discovery** providers, among them Kubernetes, AWS EC2 and Lightsail, Azure, GCP, Consul, Docker, file-based and HTTP. Each refreshes in the background and returns a list of candidate targets with an address and a set of hidden `__meta_<provider>_*` labels.

Discovery deliberately does almost nothing else. Deciding which candidates to keep and what labels they get is the job of **relabeling**. In the book’s words, relabeling is where the magic happens.

With the Prometheus Operator you rarely write `kubernetes_sd_configs` yourself. A ServiceMonitor says “scrape services with these labels, on the port named `http-metrics`, and take the job name from the service’s `jobLabel` label”. The Operator expands that into a scrape job with a short discovery block and a long list of relabel rules.

That last rule explains a confusing moment in the chapter: the scrape job is named `serviceMonitor/prometheus/…-node-exporter/0`, yet querying `{job="serviceMonitor/…"}` returns nothing, because relabeling overwrote `job` with `node-exporter`.

## Key ideas

- How discovery providers hand targets and metadata to Prometheus
- How ServiceMonitors become kubernetes_sd_configs and relabel rules
- Relabel actions, the three places relabeling runs, and how to debug it
- How a provider works inside (the Linode example) and why HTTP SD replaced file_sd scripts

## What the lesson covers

- The big picture
- From ServiceMonitor to scrape job
- Relabel actions
- Debugging
- How a provider works: the Linode example
- HTTP SD

## Claims and numbers

- For years the project refused new providers; the moratorium ended in late 2019 and the count went from 11 to about 25.

## Terms

service discovery, relabeling, Discovery, relabel_configs, Scrape, metric_relabel_configs, TSDB, write_relabel_configs, Targets, HTTP SD

## Interview line

Discovery returns candidate targets with hidden meta labels; relabel_configs decide which to scrape and what labels they get, metric_relabel_configs fix or drop series after the scrape, and write_relabel_configs choose what goes to remote storage. I debug with the Service Discovery page, which shows labels before and after relabeling. For anything without a built-in provider I serve HTTP SD.

## On AWS

On EC2, `ec2_sd_configs` needs `ec2:DescribeInstances`; filter by tag server-side and turn tags into labels with `labelmap` on `__meta_ec2_tag_(.+)`. On EKS, use ServiceMonitors with the Operator, or give the AMP managed collector a scrape config with `kubernetes_sd_configs`. For anything else (Cloud Map, a CMDB, an inventory in DynamoDB), serve HTTP SD from a small Lambda behind a function URL or internal ALB. POC 22 includes the IRSA role and a full EC2 scrape config.

## Takeaways

- Discovery finds candidates; relabeling decides everything else.
- Three hooks: targets before the scrape, series after it, and series before remote write.
- Debug with the Service Discovery page; build custom discovery with HTTP SD.
