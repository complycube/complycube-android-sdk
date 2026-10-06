#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

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

    rows = []
    for r in results:
        m = r.get("matrix", {})
        rows.append({
            "profile": str(m.get("profile", "unnamed")),
            "sdk": str(m.get("sdk", "unknown")),
            "jdk": str(m.get("jdk", "unknown")),
            "gradle": str(m.get("gradle", "unknown")),
            "agp": str(m.get("agp", "unknown")),
            "kotlin": str(m.get("kotlin", "unknown")),
            "compileSdk": str(m.get("compileSdk", "unknown")),
            "targetSdk": str(m.get("targetSdk", "unknown")),
            "minSdk": str(m.get("minSdk", "unknown")),
            "validation": str(m.get("validation", "assemble")),
            "policy": str(m.get("policy", "gate")),
            "result": str(r.get("result", "unknown")),
        })

    rows.sort(key=lambda row: (row["policy"] != "gate", row["profile"]))

    # Build markdown
    lines = []
    lines.append("# Compatibility Matrix")
    lines.append("")
    lines.append("> Generated from release-tag CI results. Every row uses the exact SDK version shown; no floating or historical SDK versions are substituted.")
    lines.append("")
    lines.append("A passing row verifies that the sample application compiled and packaged with that exact combination. Unlisted combinations are **not tested**, not automatically incompatible. Gate rows are release requirements; canary rows provide early warning and do not block a release.")
    lines.append("")
    lines.append("`assemble` builds the debug APK. `full` also builds the release APK, runs unit tests, and runs Android lint.")
    lines.append("")
    lines.append("## Build combinations")
    lines.append("")
    if not rows:
        lines.append("No verified release results are available yet. The next semantic-version release tag will populate this report.")
    else:
        lines.append("| Profile | SDK | JDK | Gradle | AGP | Kotlin | compileSdk | targetSdk | minSdk | Check | Policy | Result |")
        lines.append("|:---|---:|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|")

        for row in rows:
            result = row["result"]
            emoji = "✅" if result == "success" else ("❌" if result == "failure" else "⚠️")
            lines.append(
                f"| {row['profile']} | {row['sdk']} | {row['jdk']} | {row['gradle']} | "
                f"{row['agp']} | {row['kotlin']} | {row['compileSdk']} | {row['targetSdk']} | "
                f"{row['minSdk']} | {row['validation']} | {row['policy']} | {emoji} {result} |"
            )

    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("These checks verify dependency resolution, compilation, tests/lint where marked `full`, and APK packaging. They do not by themselves prove runtime behavior on every Android device or OS version.")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
