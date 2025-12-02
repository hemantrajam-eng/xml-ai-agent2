# modules/excel_utils.py
import pandas as pd
from datetime import datetime

def generate_excel_report(groups, dep_id_to_name, original_mapping=None):
    """
    Generates report dataframe.
    original_mapping: future use (Step #3), for now assumed None.
    """

    rows = []
    group_number = 1

    for g in groups:
        final_group_name = ",".join(g["names"])
        final_group_id = f"G{group_number}"

        for val, name in zip(g["values"], g["names"]):
            sr_no = len(rows) + 1

            # format dependents as id:name
            final_deps_string = ";".join(
                f"{dep}:{dep_id_to_name.get(dep, '')}"
                for dep in g["deps_set"]
            )

            # Since we haven't compared to original yet, mark everything initial state
            row = {
                "Sr No": sr_no,
                "Value ID": val,
                "Original Value Name": name,
                "Final Group Name": final_group_name,
                "Original Group ID": final_group_id,
                "Final Group ID": final_group_id,
                "Group Status": "Non-modified",
                "Dependency Status": "Non-modified",
                "Original Dependents": final_deps_string,
                "Final Dependents": final_deps_string
            }

            rows.append(row)

        group_number += 1

    df = pd.DataFrame(rows)
    return df


def save_report_to_excel(df):
    """
    Saves with YYYYMMDD naming format.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"Cleaned_XML_Report_{date_str}.xlsx"
    df.to_excel(filename, index=False)
    return filename
