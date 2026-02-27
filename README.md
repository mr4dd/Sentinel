# Sentinel

## 1. Purpose

Sentinel was created to address a lack of visibility into what networked devices are doing and what network services they're reaching out to without having to rely on huge software platforms designed for high throughput data ingestion and processing that bring unnecessary complexity into environments that do not require it.


## 2. Functioning

Sentinel works by aggregating 3 different data sources: system logs, resources usage, and network traffic. It does so by relying on the scapy python library and native unix tools such as journalctl.
This data is then sent over to a server for visualization, storage, and further processing according to the user's needs

## 3. License

This project is provided under the [AGPL License](LICENSE.md)

