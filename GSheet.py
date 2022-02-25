import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime


class SheetManager:
    def __init__(self, JSON: str = '', sheet: str = '', page_index: [int, str] = 0):
        try:
            self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']  # define the scope
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath(JSON), self.scope)  # add credentials to the account
            self.client = gspread.authorize(self.creds)  # authorize the client sheet
            self.sheet = self.client.open(sheet)  # get the instance of the Spreadsheet
            self.sheet_instance = self.sheet.get_worksheet(page_index)  # get the first sheet of the Spreadsheet
        except Exception as e:
            print(e)

    def send_report(self, data: dict, row: int = -1):
        try:
            if data is None:
                return
            if row == -1:
                columns = self.sheet_instance.col_values(1)
                row = len(columns) + 1
            for col, data in data.items():
                self.sheet_instance.update(f'{col}{row}', data)
            return True
        except Exception as e:
            print(e)