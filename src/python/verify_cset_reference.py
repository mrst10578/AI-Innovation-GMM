"""Compare the supplied AI panel to a *separate*, versioned CSET reference zip.

Does NOT replace the supplied study dataset or presume the versions/methods are identical.
Run: python -m src.python.verify_cset_reference --reference-zip PATH_TO_CAT_ZIP
Reference: https://zenodo.org/records/19103157 (2026-03-19, CSET/ETO v1.11.0).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from src.python.preflight import ROOT

REFERENCE = {
    "version": "1.11.0",
    "publication_date": "2026-03-19",
    "zenodo_record": "https://zenodo.org/records/19103157",
    "doi": "10.5281/zenodo.19103157",
    "country_map": {"CHN": "China (mainland)", "USA": "United States"},
    "years": (2023, 2024),
    "datasets": {
        "patent_applications": ("cat/patents_yearly_applications.csv", "num_patent_applications", "AI_Patents"),
        "estimated_private_equity_investment_musd": ("cat/companies_yearly_estimated.csv", "estimated_investment", "AI_Investment"),
        "disclosed_private_equity_investment_musd": ("cat/companies_yearly_disclosed.csv", "disclosed_investment", "AI_Investment"),
    },
}

def build_audit(reference_zip: Path) -> dict:
    if not reference_zip.is_file():
        raise FileNotFoundError(f"Official reference zip missing: {reference_zip}")
    original = ROOT / "data/raw/AI_Balanced_Panel (1).xlsx"
    panel = pd.read_excel(original, engine="openpyxl")
    if panel.duplicated(["ISO3", "Year"]).any():
        raise ValueError("Duplicate original country/year")
    with ZipFile(reference_zip) as z:
        bad = z.testzip()
        if bad is not None:
            raise ValueError(f"Corrupt official ZIP member: {bad}")
        ref_tables = {kind: pd.read_csv(z.open(name)) for kind,(name,_,_) in REFERENCE["datasets"].items()}
    rows = []
    for iso, official_name in REFERENCE["country_map"].items():
        for year in REFERENCE["years"]:
            source = panel.loc[(panel.ISO3 == iso) & (panel.Year == year)]
            if len(source) != 1:
                raise ValueError(f"Missing/duplicated original entry {iso}/{year}")
            for kind,(_,column,source_column) in REFERENCE["datasets"].items():
                df = ref_tables[kind]
                matches = df.loc[(df.country == official_name) & (df.field == "All") & (df.year == year)]
                if len(matches) != 1:
                    raise ValueError(f"Reference missing/duplicated All-field entry: {kind} {iso}/{year}")
                original_number = float(source.iloc[0][source_column])
                official_number = float(matches.iloc[0][column])
                rows.append({
                    "country": iso, "year": year, "metric": kind,
                    "supplied_column": source_column,
                    "supplied_value": original_number,
                    "cset_reference_value": official_number,
                    "reference_complete": bool(matches.iloc[0]["complete"]),
                    "absolute_difference": original_number - official_number,
                    "ratio_supplied_to_reference": original_number / official_number if official_number else None,
                })
    return {
        "reference_version": REFERENCE["version"],
        "reference_publication_date": REFERENCE["publication_date"],
        "reference_zenodo_url": REFERENCE["zenodo_record"],
        "reference_doi": REFERENCE["doi"],
        "reference_zip_sha256": hashlib.sha256(reference_zip.read_bytes()).hexdigest(),
        "original_source_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
        "comparison_kind": "DEFINITION_AND_VERSION_AUDIT_NOT_IDENTICAL_METRIC_ASSERTION",
        "findings": rows,
        "blocking_questions": [
            "Which named version/release, CSET table, field, raw column, country mapping and transform produced the 270 supplied AI rows?",
            "For patents, are the observations annual patent families, patent application documents, cumulative counts, AI subfields, or another source?",
            "For investment, does the source measure estimated or disclosed equity into privately held firms, how are USD-million units converted, and are fields double counted?",
            "What is the official source completeness/revision flag for each country-year, especially 2024?",
            "World Bank outcome/control country-year source pulls and download dates must also be documented independently.",
        ],
        "do_not_infer": [
            "Mismatched numeric values do not prove fabrication or an error, since definitions and releases could differ.",
            "Do not splice reference data into the original 30-country panel without explicit approval and a new analysis branch.",
            "Do not certify causal GMM conclusions until this provenance gate and identification assumptions are defensible.",
        ],
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference-zip", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=ROOT/"reports"/"CSET_REFERENCE_COMPARISON_20261017.json")
    args = ap.parse_args()
    result=build_audit(args.reference_zip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in result["findings"]:
        print(row["country"],row["year"],row["metric"],row["supplied_value"],row["cset_reference_value"],"complete=",row["reference_complete"])
    print("Source audit written to",args.output)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
