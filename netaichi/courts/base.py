from datetime import date


class CourtMeta(type):
    def __init__(cls, name, bases, attrs):
        """CourtMetaの派生クラス読み込まれた時に呼び出されます"""
        if not hasattr(cls, "court_classes"):
            cls.court_classes = []
        else:
            cls.court_classes.append(cls)


class CourtBase(metaclass=CourtMeta):
    name: str
    _value: str
    default_times = [9, 11, 13, 15, 17, 19]

    def __init__(self, manager):
        self.manager = manager

    def _available_times(self, date: date) -> list[int]:
        # オーバーロードして使う
        return self.default_times

    @property
    def times(self) -> list[int]:
        lottery_date = self.manager.lottery_date
        return self._available_times(lottery_date)

    @property
    def value(self) -> str:
        return str(self.__class__._value)

    @value.setter
    def value(self, value: str):
        self.__class__._value = value
