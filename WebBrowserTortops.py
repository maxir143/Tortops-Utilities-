from pywinauto import Application


class Browser:
    def __init__(self):
        self.url = ''
        self.element_name = "Barra de direcciones y de búsqueda "
        self.app = Application(backend='uia')

    def connect_browser(self):
        try:
            self.app.connect(title_re=".*Chrome.*", found_index=0)
            return True
        except Exception as e:
            print(f'No se encontro Buscador, {e}')
            pass

    def get_current_page(self):
        try:
            if self.connect_browser():
                dlg = self.app.top_window()
                url = dlg.child_window(title=self.element_name, found_index=0)
                return url.get_value()
        except Exception as e:
            print(f'Error al obtener la url, {e}')
            pass
