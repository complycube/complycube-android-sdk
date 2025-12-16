#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--jdk", required=True)
    p.add_argument("--gradle", required=True)
    p.add_argument("--agp", required=True)
    p.add_argument("--kotlin", required=True)
    p.add_argument("--compileSdk", required=True)
    p.add_argument("--targetSdk", required=True)
    p.add_argument("--status", required=True)  # success|failure|cancelled
    args = p.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": os.getenv("GITHUB_REPOSITORY"),
        "run_id": os.getenv("GITHUB_RUN_ID"),
        "sha": os.getenv("GITHUB_SHA"),
        "matrix": {
            "jdk": args.jdk,
            "gradle": args.gradle,
            "agp": args.agp,
            "kotlin": args.kotlin,
            "compileSdk": int(args.compileSdk),
            "targetSdk": int(args.targetSdk),
        },
        "result": args.status,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
