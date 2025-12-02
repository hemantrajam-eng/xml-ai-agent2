# modules/xml_cleaner.py
import xml.etree.ElementTree as ET
from .xml_utils import prettify_xml, split_field
from .grouping_logic import flatten_options, union_deps_by_value, merge_values_by_deps

def generate_clean_xml_from_root(root: ET.Element) -> str:
    """
    Implements rules:
    1. Split names -> flatten
    2. If same value ID appears multiple times -> union dependents
    3. Regroup by VALUE (union dependents)
    4. Merge values that share identical merged dependents
    5. DO NOT SORT: preserve first-seen order
    Additionally: keep first-occurrence dependent 'name'
    """
    flat, dep_id_to_name, name_to_value = flatten_options(root)

    # union dependents for each value
    value_to_deps = union_deps_by_value(flat)

    # merge values that have identical dependent sets
    groups = merge_values_by_deps(flat, value_to_deps)

    # build new <dependents> root
    new_root = ET.Element("dependents", root.attrib)

    for g in groups:
        opt = ET.SubElement(new_root, "option")
        opt.set("name", ",".join(g["names"]))
        opt.set("value", ",".join(g["values"]))
        # preserve dependent names from first-seen mapping
        for dep_id in sorted(g["deps_set"], key=str):
            ET.SubElement(opt, "dependent", {
                "type": "0",
                "id": dep_id,
                "name": dep_id_to_name.get(dep_id, ""),
                "reset": "false",
                "retainonedit": "false"
            })

    return prettify_xml(new_root)
