# Arcane Shield

Arcane Shield is a project that aims to collect addresses such as public proxies, VPNs and Tor exit nodes from several sources with the objective of using them to block malicious requests to an web service.

## Installation

```
pip install arcaneshield
```

## Usage

To get the list of malicious addresses:

```python
from arcaneshield.sources.all import get_ip_list()

iplist = get_ip_list()
```

To automatically create a AWS WAF Regional rule and populate the corresponding IP Sets, first make sure to set AWS_PROFILE and AWS_DEFAULT_REGION, then run:

```python
from arcaneshield.aws import protect as aws_protect

aws_protect()
```
