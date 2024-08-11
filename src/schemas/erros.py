class ErroPersonalizado(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class MissingDataError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

