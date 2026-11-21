# Grafana chapter 8: Dashboards with a purpose

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-8`. Code: POC 29 · 6. Read: full text, one pass; all figures seen.*

## Summary

The chapter’s first dashboard shows why the defaults aren’t enough. Adding `app_frontend_requests_total{target="/api/cart"}` from Explore gives an ever-rising line with an unreadable legend and a meaningless title. Four edits make it useful: wrap it in `rate(…[$__rate_interval])` (Grafana even suggests it), set the legend to `{{method}}`, give it a title that says it is a rate and a description that says what to look for, and set the query type to Range only so instant points don’t appear on a time series.

Three questions: **who** is the audience, **what** do they need, and **where** will they view it (a wall screen, a laptop, a phone, an emailed PDF)? The personas answer differently.

## Key ideas

- Building and improving a first panel: rate, legend, title, description, query type
- What every panel can configure: units, thresholds, overrides, value mappings
- Three questions that give a dashboard its purpose, per persona
- Layout and technical techniques that reduce cognitive load
- Folders, tags and permissions; the Steven case study

## What the lesson covers

- From a query to a useful panel
- What a panel can configure
- Give the dashboard a purpose
- Layout
- Folders, tags and permissions
- Case study: a dashboard for Steven

## Terms

what, where, Across the books, Four golden signals

## Interview line

Before building a dashboard I ask who it’s for, what question it answers and where they’ll look at it. Then key indicators go first as Stats with sparklines, detail sits in collapsed rows, every panel has a unit and a description, values come from variables, rates use $__rate_interval, and deployments show as annotations. Dashboards live in team folders, as code.

## On AWS

In Amazon Managed Grafana, sign-in comes from IAM Identity Center or SAML, and Grafana teams can be mapped from groups, so folder permissions follow your organisation. Manage dashboards as JSON in Git and publish them with the grafana Terraform provider. CloudWatch dashboards are the AWS-native alternative for AWS service metrics. POC 29 generates a golden-signals dashboard with collapsed team rows, lints it against this chapter’s rules, and publishes it to AMG with Terraform.

## Takeaways

- Who, what and where come before any panel.
- Indicators first, detail in collapsed rows, links instead of cramming.
- Units, descriptions, variables, $__rate_interval and annotations everywhere.
