class SymbolTable:

    def __init__(self):
        self.table = {}

    def addEntry(self, symbol : str, address : int):
        self.table[symbol] = address

    def contains(self, symbol) -> bool:
        return symbol in self.table

    def getAddress(self, symbol) -> int:
        if self.contains(symbol):
            return self.table[symbol]
        return None
