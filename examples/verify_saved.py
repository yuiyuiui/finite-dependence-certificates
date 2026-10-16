"""The saved finite certificate can be replayed with Python's standard library."""

import json
from pathlib import Path
from finite_dependence import verify_certificate

record = json.loads(Path(__file__).with_name("three_color_path_certificate.json").read_text())
assert verify_certificate(record)
print("Exact finite hierarchy contradiction verified")
