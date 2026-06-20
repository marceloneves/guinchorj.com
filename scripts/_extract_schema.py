"""Read render_page JSON from stdin and print all JSON-LD blocks."""
import sys, json, re

data = json.load(sys.stdin)
print("SPA:", data.get("is_spa"))
print("PUB:", data.get("publication_date"))

raw = data.get("raw_content", "")
pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
blocks = re.findall(pattern, raw, re.DOTALL | re.IGNORECASE)
print(f"TOTAL BLOCKS: {len(blocks)}")
for i, b in enumerate(blocks):
    print(f"\n=== BLOCK {i} ===")
    print(b.strip()[:4000])
