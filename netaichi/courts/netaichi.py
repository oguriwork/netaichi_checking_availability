from __future__ import annotations

from datetime import date

from .base import CourtBase


class Oodaka(CourtBase):
    name = "大高緑地－庭球場ハード"
    _value = "130"

    def _available_times(self, date: date) -> list[int]:
        """夏期は17時まで、それ以外は15時まで"""
        if date.month in [7, 8]:
            return [9, 11, 13, 15, 17]
        return [9, 11, 13, 15]


class Morikoro(CourtBase):
    name = "愛・地球博－庭球場人工芝ナイタ"
    _value = "410"

    def _available_times(self, date: date) -> list[int]:
        """デフォルト時間を使用"""
        return self.default_times


class MorikoroFutsal(CourtBase):
    name = "愛・地球博－フットサル場テニス"
    _value = "400"

    def _available_times(self, date: date) -> list[int]:
        """デフォルト時間を使用"""
        return self.default_times


class Korogi(CourtBase):
    name = "口論義運動公園－庭球場人工芝"
    _value = "540"

    def _available_times(self, date: date) -> list[int]:
        """4-9月は8時開始、10-3月は9時開始"""
        if date.month in [4, 5, 6, 7, 8, 9]:
            return [8, 10, 12, 14, 16]
        return [9, 11, 13, 15]


class KorogiNighter(CourtBase):
    name = "口論義－庭球場人工芝ナイター"
    _value = "550"

    def _available_times(self, date: date) -> list[int]:
        """4-9月は8時開始+ナイター、10-3月はデフォルト"""
        if date.month in [4, 5, 6, 7, 8, 9]:
            return [8, 10, 12, 14, 16, 18]
        return self.default_times


class KorogiCenter(CourtBase):
    name = "口論義－庭球場１５．１６"
    _value = "530"

    def _available_times(self, date: date) -> list[int]:
        """4-9月は8時開始、10-3月は9時開始"""
        if date.month in [4, 5, 6, 7, 8, 9]:
            return [8, 10, 12, 14, 16]
        return [9, 11, 13, 15]


class Kenkou(CourtBase):
    name = "あいち健康の森－庭球場人工芝"
    _value = "310"

    def _available_times(self, date: date) -> list[int]:
        """固定時間（9-15時）"""
        return [9, 11, 13, 15]


class KenkouNighter(CourtBase):
    name = "あいち健康の森－庭球場ナイタ"
    _value = "320"

    def _available_times(self, date: date) -> list[int]:
        """デフォルト時間（ナイター含む）"""
        return self.default_times


class Obata(CourtBase):
    name = "小幡緑地－庭球場人工芝"
    _value = "180"

    def _available_times(self, date: date) -> list[int]:
        """固定時間（9-15時）"""
        return [9, 11, 13, 15]
