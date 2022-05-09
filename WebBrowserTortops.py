from pywinauto import Application
import uiautomation as auto


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
            return auto.Control(Depth=1, ClassName='Chrome_WidgetWin_1', SubName='Google Chrome', foundIndex=1).Name
        except Exception as e:
            print(f'Cant get current url, {e}')
            self.connect_browser()
            return False
