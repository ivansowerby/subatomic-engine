from re import compile, search

class Dunder:
    STATEMENT = compile('^(?:_+)?((i)?(?:[a-zA-Z][a-zA-Z0-9]*))(?:_+)?$')
    
    def __init__(self, name: str) -> None:
        matches = search(Dunder.STATEMENT, name)
        name, augmented_prefix = matches.groups()
        self.name =  f'__{name}__'
        self.is_augmented = augmented_prefix != None
