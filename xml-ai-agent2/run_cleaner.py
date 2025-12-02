# run_cleaner.py
import xml.etree.ElementTree as ET
from modules.xml_cleaner import generate_clean_xml_from_root
from modules.grouping_logic import flatten_options, union_deps_by_value, merge_values_by_deps
from modules.excel_utils import generate_excel_report, save_report_to_excel

SAMPLE_XML = """<dependents>
  <option name="A" value="306">
    <dependent type="0" id="cust_1590" name="Account Number" reset="false" retainonedit="false"/>
  </option>
  <option name="B" value="1175">
    <dependent type="0" id="cust_360" name="Customer Declaration" reset="false" retainonedit="false"/>
  </option>
</dependents>"""

def main():
    root = ET.fromstring(SAMPLE_XML)

    # STEP 1: Clean XML
    cleaned_xml = generate_clean_xml_from_root(root)
    print("\n=== CLEANED XML ===\n")
    print(cleaned_xml)

    # STEP 2: Prepare report input structures
    flat, dep_id_to_name, _ = flatten_options(root)
    value_to_deps = union_deps_by_value(flat)
    groups = merge_values_by_deps(flat, value_to_deps)

    # STEP 3: Generate Excel Report
    df = generate_excel_report(groups, dep_id_to_name)
    file_path = save_report_to_excel(df)

    print(f"\n📁 Report generated: {file_path}")


if __name__ == "__main__":
    main()
