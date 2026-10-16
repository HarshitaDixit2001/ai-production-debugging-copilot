
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.tools.evidence_collector import EvidenceCollector


collector = EvidenceCollector()

incidents = [
    "POST /payment is returning HTTP 500",
    "Payment API requests are timing out",
    "POST /payment returns HTTP 400 because currency is missing",
    "POST /unknown returns HTTP 500 with no matching logs or documentation",
]

for incident in incidents:
    print("\n" + "=" * 80)
    print(f"INCIDENT: {incident}")
    print("=" * 80)

    results = collector.collect(incident, top_k=5)

    if not results:
        print("NO EVIDENCE FOUND")
        continue

    for item in results:
        print(f"\nTool: {item.get('tool', 'unknown')}")
        print(f"Source: {item.get('source', 'unknown')}")
        print(f"Score: {item.get('score', 'not provided')}")
        print(f"Content: {str(item.get('content', ''))[:700]}")
