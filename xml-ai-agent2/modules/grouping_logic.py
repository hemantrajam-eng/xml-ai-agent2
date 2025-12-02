# modules/grouping_logic.py
from typing import List, Dict, Set, Tuple
from xml.etree import ElementTree as ET

from .xml_utils import split_field

def flatten_options(root: ET.Element):
    """
    Flatten options into list of dicts: {name, value, deps_set}
    Also return dep_id -> first-seen name mapping.
    """
    flat = []
    dep_id_to_name = {}
    name_to_value = {}

    for opt in root.findall("option"):
        names = split_field(opt.get("name", ""))
        values = split_field(opt.get("value", ""))

        deps = opt.findall("dependent")
        dep_ids = []
        for d in deps:
            dep_id = d.get("id")
            dep_name = d.get("name", "") or ""
            dep_ids.append(dep_id)
            if dep_id not in dep_id_to_name:
                dep_id_to_name[dep_id] = dep_name

        for idx, name in enumerate(names):
            value = values[idx] if idx < len(values) else (values[-1] if values else "")
            flat.append({"name": name, "value": value, "deps": set(dep_ids)})
            if name not in name_to_value:
                name_to_value[name] = value

    return flat, dep_id_to_name, name_to_value

def union_deps_by_value(flat_records: List[Dict]) -> Dict[str, Set[str]]:
    """
    For each distinct value, union dependents across all flat entries that use it.
    Returns mapping: value -> set(dep_ids)
    """
    value_to_deps = {}
    for rec in flat_records:
        val = rec["value"]
        value_to_deps.setdefault(val, set())
        value_to_deps[val].update(rec["deps"])
    return value_to_deps

def merge_values_by_deps(flat_records: List[Dict], value_to_deps: Dict[str, Set[str]]):
    """
    Group values that have identical dependents sets. Preserve first-seen group order
    based on appearance in flat_records.
    Returns list of groups preserving first-seen order:
      [ { "names": [...], "values": [...], "deps_set": frozenset(...) }, ... ]
    """
    seen_dep_sets = {}
    for rec in flat_records:
        val = rec["value"]
        dep_key = frozenset(value_to_deps[val])
        if dep_key not in seen_dep_sets:
            seen_dep_sets[dep_key] = {"names": [], "values": [], "deps_set": dep_key}
        group = seen_dep_sets[dep_key]
        if rec["name"] not in group["names"]:
            group["names"].append(rec["name"])
        if val not in group["values"]:
            group["values"].append(val)

    # preserve first-seen order by iteration order of seen_dep_sets
    groups = []
    for k, v in seen_dep_sets.items():
        groups.append({
            "names": v["names"],
            "values": v["values"],
            "deps_set": v["deps_set"]
        })
    return groups
