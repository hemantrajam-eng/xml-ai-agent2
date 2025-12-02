# modules/xml_utils.py
import xml.etree.ElementTree as ET

def split_field(text):
    """Split comma-separated attribute safely and return stripped tokens."""
    if not text:
        return []
    return [t.strip() for t in text.split(",") if t.strip()]

def prettify_xml(elem: ET.Element) -> str:
    """Pretty-print XML Element to unicode string (simple indent)."""
    def _indent(e, level=0):
        i = "\n" + level * "  "
        if len(e):
            if not e.text or not e.text.strip():
                e.text = i + "  "
            for child in e:
                _indent(child, level+1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        if level and (not e.tail or not e.tail.strip()):
            e.tail = i
    _indent(elem)
    return ET.tostring(elem, encoding="unicode")
