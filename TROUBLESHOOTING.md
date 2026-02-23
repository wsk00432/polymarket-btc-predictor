# Connection Issues

## DNS Resolution Problem
- Symptom: Unable to connect to Clawdbot gateway
- Solution: Set IPv4 priority
- Command: `export NODE_OPTIONS="--dns-result-order=ipv4first" && clawdbot gateway --bind loopback --port 18789 --verbose --force`
- Root cause: DNS resolution preferring IPv6 when IPv4 should be prioritized