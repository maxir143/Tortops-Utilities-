from pywinauto import Application


class Browser:
    def __init__(self):
        self.url = ''
        self.element_name = "Barra de direcciones y de búsqueda "
        self.app = Application(backend='uia')

    def connect_browser(self):
        try:
            self.app.connect(title_re=".*Chrome.*", timeout=1, found_index=0)
            return True
        except Exception as e:
            print(f'Couldn"t find Chrome window, {e}')

    def get_current_page(self):
        try:
            dlg = self.app.top_window()
            url = dlg.child_window(title=self.element_name, found_index=0).get_value()
            return url
        except Exception as e:
            print(f'Cant get current url, {e}')
            self.connect_browser()
            return False
