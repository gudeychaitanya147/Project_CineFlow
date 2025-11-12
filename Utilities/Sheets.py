
def list_sheets(service, spreadsheet_id):
    """List all sheet names in the spreadsheet."""
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = metadata.get("sheets", [])
    names = [s["properties"]["title"] for s in sheets]
    print("Available Sheets:", names)
    return names

def read_sheet(service, spreadsheet_id, range_name):
    """Read data from a given Google Sheet range."""
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    values = result.get("values", [])
    return values


def write_sheet(service, spreadsheet_id, range_name, values):
    """Write data (2D list) to a given range in Google Sheet."""
    body = {"values": values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

def write_drive_files_to_sheet(service, sheet_range, files):

    header_result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="Output!1:1"
    ).execute()

    headers = header_result.get("values", [[]])[0]

    rows = []
    for f in files:
        row_data = []
        for header in headers:
            if header.lower() == "id":
                row_data.append(f.get("id"))
            elif header.lower() == "title":
                row_data.append(f.get("name"))
            elif header.lower() == "size in b":
                row_data.append(f.get("size"))
            elif header.lower() == "drive url":
                row_data.append(f.get("webViewLink"))
            else:
                row_data.append("")
        rows.append(row_data)

    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=sheet_range,
        valueInputOption="USER_ENTERED",
        body={"values": rows}
    ).execute()

    print(f"{len(rows)} files written to sheets.")

def clear_sheet_data(service, sheet_range):

    service.spreadsheets().values().clear(
        spreadsheetId=SHEET_ID,
        range=sheet_range
    ).execute()
    print(f"Cleared data in range: {sheet_range}")


def update_unprocessed_rows(service, SHEET_ID):

    response = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="Sheet1!A2:G"
    ).execute()

    rows = response.get("values", [])

    rows_to_update = []

    # Step 2: Find rows with empty processed column
    for idx, row in enumerate(rows, start=2):
        processed_value = row[6] if len(row) > 6 else ""
        if processed_value.strip() == "":
            rows_to_update.append(idx)

    if not rows_to_update:
        print("No unprocessed rows found.")
        return

    # Step 3: Prepare update requests
    updates = []
    for row_num in rows_to_update:
        updates.append({
            "range": f"Sheet1!G{row_num}:H{row_num}",
            "values": [["YES", "Updated"]]
        })

    # Step 4: Execute batch update
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updates
    }

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()

    print(f"Updated {len(rows_to_update)} rows")

SHEET_ID = "1ttrGdA9cTP5Qei8P2zp_d0klbUPLkIGiUbTfvsAWhSg"
