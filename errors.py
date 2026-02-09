class APIError(Exception):
    def __init__(self, message="база данных недоступна"):
        self.code = 500
        self.message = message

class BadRequest(APIError):
    def __init__(self, message = "неправильный запрос"):
        self.code = 400
        self.message = message
    
class NotFound(APIError):
    def __init__(self, message = "Не найдено"):
        self.code = 404
        self.message = message
    
class ConflictError(APIError):
    def __init__(self, message = "конфликт между запросом клиента и текущим состоянием ресурса на сервере"):
        self.code = 409
        self.message = message
    