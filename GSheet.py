import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


class SheetManager:
    def __init__(self, JSON: str, url: str):
            self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']  # define the scope
            self.json = JSON
            self.sheet_url = url
            self.sheets = {}
            try:
                self.check_connection()
            except Exception as e:
                print(f'Error con la configuracion inicial: {e}')

    def update(self, JSON: str, url: str):
        self.json = JSON
        self.sheet_url = url

    def check_connection(self):
        try:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath(self.json), self.scope)  # add credentials to the account
            self.client = gspread.authorize(self.creds)  # authorize the client sheet
            self.sheet = self.client.open_by_url(self.sheet_url )
            return True
        except Exception as e:
            print(f'Error conectarse al archivo: {e}')

    def send_report(self, page: str, data: dict, row: int = -1):
        try:
            if data is None:
                return
            sheet_instance = self.sheet.worksheet(page)
            if row == -1:
                columns = sheet_instance.col_values(1)
                row = len(columns) + 1
            for col, data in data.items():
                sheet_instance.update(f'{col}{row}', data)
            return True
        except Exception as e:
            print(f'Error al mandar reporte: {e}')

    def get_pages(self):
        try:
            for sheet in self.sheet.worksheets():
                sheet_title = sheet.title
                sheet_id = sheet.id
                self.sheets[sheet_title] = sheet_id
            return self.sheets
        except Exception as e:
            print(f'Error al obtener paginas: {e}')
