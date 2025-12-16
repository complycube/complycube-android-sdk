#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import defaultdict

def load_results(results_dir: Path):
    results = []
    for p in results_dir.rglob("*.json"):
        try:
            results.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    out_path = Path(args.out)

    results = load_results(results_dir)

    # Key by matrix tuple
    by_key = {}
    for r in results:
        m = r.get("matrix", {})
        key = (
            str(m.get("jdk")),
            str(m.get("gradle")),
            str(m.get("agp")),
            str(m.get("kotlin")),
            str(m.get("compileSdk")),
            str(m.get("targetSdk")),
        )
        by_key[key] = r.get("result", "unknown")

    # Build markdown
    lines = []
    lines.append("# Compatibility Matrix")
    lines.append("")
    lines.append("> Generated from CI build-matrix results (assembleDebug).")
    lines.append("")
    lines.append("## Build combinations")
    lines.append("")
    lines.append("| JDK | Gradle | AGP | Kotlin | compileSdk | targetSdk | Result |")
    lines.append("|---:|---:|---:|---:|---:|---:|:---|")

    for key in sorted(by_key.keys()):
        jdk, gradle, agp, kotlin, compileSdk, targetSdk = key
        res = by_key[key]
        emoji = "✅" if res == "success" else ("❌" if res == "failure" else "⚠️")
        lines.append(f"| {jdk} | {gradle} | {agp} | {kotlin} | {compileSdk} | {targetSdk} | {emoji} {res} |")

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
