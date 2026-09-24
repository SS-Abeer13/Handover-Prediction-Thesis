import docx

doc = docx.Document('Docs/Handover_Thesis_Manuscript_Revised.docx')

TABLE_MAP = {
    1: "2.1", 2: "3.1", 3: "3.2", 4: "3.3", 5: "4.1", 6: "4.2", 7: "4.3", 8: "5.1", 9: "5.2",
    10: "5.2b", 11: "5.3", 12: "5.4", 13: "5.5", 14: "5.6", 15: "5.6b", 16: "5.7", 17: "5.8",
    18: "5.9", 19: "5.10", 20: "5.11", 21: "5.12", 22: "5.13", 23: "5.14", 24: "5.15", 25: "5.16",
    26: "6.1", 27: "6.2", 28: "6.3", 29: "6.4", 30: "6.5", 31: "6.6", 32: "A.1", 33: "A.2",
    34: "A.3", 35: "A.4", 36: "A.5", 37: "A.6", 38: "D.1"
}

for idx, tab_num in TABLE_MAP.items():
    tbl = doc.tables[idx]
    if len(tbl.columns) == 4:
        first_row = [c.text.strip().replace('\n', ' ')[:25] for c in tbl.rows[0].cells]
        sample_row = [c.text.strip().replace('\n', ' ')[:25] for c in tbl.rows[1].cells]
        print(f"Table {tab_num} (idx {idx}): cols={first_row} | sample={sample_row}")
