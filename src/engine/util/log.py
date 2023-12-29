from os import system, name as os_name

class Log:
    def __init__(self, tab: str = '\t', newline: str = '\n') -> None:
        self.log = ''
        self.tab_character = tab
        self.newline_character = newline
        self.indentation = 0
    
    def tab(self, n: int = 1) -> None:
        self.log += (self.tab_character * n)

    def newline(self, n: int = 1) -> None:
        self.log += (self.newline_character * n)
    
    def pair(
            self,
            keyword: str,
            value: str = '',
            delimiter: str = ':'
        ) -> None:
        self.tab(self.indentation)
        self.log += f'{keyword} {delimiter} {value}'
        self.newline()
    
    def open_section(self) -> None:
        self.indentation += 1
    
    def open_list(self, keyword: str, open_bracket = '[', delimiter = ':') -> None:
        self.pair(keyword, open_bracket, delimiter)
        self.open_section()

    def close_section(self) -> None:
        self.indentation = max(self.indentation - 1, 0)

    def close_list(self, close_bracket = ']') -> None:
        self.close_section()
        self.pair(close_bracket, '', '')

def flush() -> None:
    system('cls' if os_name == 'nt' else 'clear')