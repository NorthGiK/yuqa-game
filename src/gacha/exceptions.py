class NotSameLengthOfRaritiesAndCanches(Exception):
    @property
    def message(self) -> str:
        return "Количество редкостей и количество шансов выпадения для редкостей не равны!"

class NotSelectedCardError(Exception):
    @property
    def message(self) -> str:
        return "Не выбрана ни одна карта из базы данных!"