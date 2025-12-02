import pandas as pd
from datetime import datetime
from io import BytesIO
import xml.etree.ElementTree as ET

def _split_field(field):
    """Splits comma/semicolon separated values and trims spaces."""
    if not field:
        return []
    return [f.strip() for f in field.replace(";", ",").split(",") if f.strip()]

def generate_excel_report(original_xml, cleaned_xml):
    """Generates the comparison Excel dataframe."""
    
    root_clean = ET.fromstring(cleaned_xml)
    root_original = ET.fromstring(original_xml)

    export_rows = []

    # ---------------- Build original groups ----------------
    original_group_set_to_id = {}
    value_to_original_group_sets = {}
    value_to_original_deps = {}
    value_to_original_name = {}

    g_count = 0
    for opt in root_original.findall("option"):
        g_count += 1
        gid = f"G{g_count}"

        names = _split_field(opt.get("name", ""))
        values = _split_field(opt.get("value", ""))
        values_set = frozenset(values)
        deps = sorted([f"{d.get('id')}:{d.get('name')}" for d in opt.findall("dependent")])

        if values_set not in original_group_set_to_id:
            original_group_set_to_id[values_set] = gid

        for idx, v in enumerate(values):
            value_to_original_group_sets.setdefault(v, []).append(values_set)
            value_to_original_deps.setdefault(v, set()).update(deps)

            if v not in value_to_original_name:
                # Use name at same position if exists, otherwise fallback last
                value_to_original_name[v] = names[idx] if idx < len(names) else names[-1]

    # ---------------- Build cleaned groups ----------------
    cleaned_groups = []
    for opt in root_clean.findall("option"):
        cleaned_groups.append({
            "names": _split_field(opt.get("name", "")),
            "values": _split_field(opt.get("value", "")),
            "dependents": sorted([f"{d.get('id')}:{d.get('name')}" for d in opt.findall("dependent")]),
            "values_set": frozenset(_split_field(opt.get("value", "")))
        })

    # Assign Group IDs (Hybrid Method)
    next_gid = g_count + 1
    final_valueset_to_gid = {}
    assigned_gids = []

    for group in cleaned_groups:
        vset = group["values_set"]

        if vset in original_group_set_to_id:
            assigned_gids.append(original_group_set_to_id[vset])
            final_valueset_to_gid[vset] = original_group_set_to_id[vset]
        else:
            if vset not in final_valueset_to_gid:
                final_valueset_to_gid[vset] = f"G{next_gid}"
                next_gid += 1

            assigned_gids.append(final_valueset_to_gid[vset])

    # ---------------- Build export rows ----------------
    sr = 1
    
    for group, gid in zip(cleaned_groups, assigned_gids):
        for v in group["values"]:
            orig_sets = value_to_original_group_sets.get(v, [])
            orig_group_id = next((original_group_set_to_id.get(s, "") for s in orig_sets if s == group["values_set"]), "") or \
                             original_group_set_to_id.get(orig_sets[0], "") if orig_sets else ""

            group_status = "Non-modified" if group["values_set"] in orig_sets else "Modified"
            orig_deps = set(value_to_original_deps.get(v, []))
            final_deps = set(group["dependents"])
            dependency_status = "Non-modified" if orig_deps == final_deps else "Modified"

            export_rows.append([
                sr,
                v,
                value_to_original_name.get(v, ""),
                ",".join(group["names"]),
                orig_group_id,
                gid,
                group_status,
                dependency_status,
                ";".join(sorted(orig_deps)),
                ";".join(sorted(final_deps))
            ])
            sr += 1

    return pd.DataFrame(export_rows, columns=[
        "Sr No",
        "Value ID",
        "Original Value Name",
        "Final Group Name",
        "Original Group ID",
        "Final Group ID",
        "Group Status",
        "Dependency Status",
        "Original Dependents",
        "Final Dependents"
    ])

def save_report(df):
    """Returns an in-memory downloadable Excel file."""
    buffer = BytesIO()
    today = datetime.now().strftime("%Y%m%d")
    filename = f"Cleaned_XML_Report_{today}.xlsx"
    df.to_excel(buffer, sheet_name="Mapping", index=False)
    buffer.seek(0)
    return filename, buffer
