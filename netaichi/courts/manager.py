from __future__ import annotations
from datetime import date
from dateutil.relativedelta import relativedelta  # type: ignore
from typing import Optional
from .base import CourtBase


class CourtManager:
    """コート管理クラス"""

    def __init__(self, diff_month: int):
        self.lottery_date = date.today().replace(day=1) + relativedelta(
            months=diff_month
        )
        self.registry: dict[str, CourtBase] = {}
        self._instances: list[CourtBase] = []

        # 重複チェック用
        names = set()
        values = set()

        for cls in CourtBase.court_classes:
            instance: CourtBase = cls(manager=self)

            # 重複チェック
            if instance.name in names:
                raise ValueError(f"Duplicate court name: {instance.name}")
            if instance.value in values:
                raise ValueError(f"Duplicate court value: {instance.value}")

            names.add(instance.name)
            values.add(instance.value)

            # インスタンスリストに追加（重複排除用）
            self._instances.append(instance)

            # 複数キーでの登録
            self.registry[cls.__name__.lower()] = instance
            self.registry[instance.name] = instance
            self.registry[instance.value] = instance

    def __getattr__(self, key: str) -> CourtBase:
        """属性アクセス用: cm.oodaka など"""
        try:
            return self.registry[key]
        except KeyError:
            raise AttributeError(f"'CourtManager' object has no attribute '{key}'")  # noqa: B904

    def get(self, name_or_value: str) -> Optional[CourtBase]:
        """コートを取得（見つからない場合はNone）"""
        return self.registry.get(name_or_value)

    def get_required(self, name_or_value: str) -> CourtBase:
        """コートを取得（見つからない場合は例外）"""
        instance = self.get(name_or_value)
        if not instance:
            raise ValueError(f"Court '{name_or_value}' not found")
        return instance

    def get_time(self, name_or_value: str) -> list[int]:
        """指定されたコートの利用可能時間を取得"""
        return self.get_required(name_or_value).times

    def to_value(self, name: str) -> str:
        """コート名から値を取得"""
        return self.get_required(name).value

    def to_name(self, value: str) -> str:
        """値からコート名を取得"""
        return self.get_required(value).name

    def all_values(self) -> set[str]:
        """全てのコート値を取得（重複なし）"""
        return {instance.value for instance in self._instances}

    def all_names(self) -> set[str]:
        """全てのコート名を取得（重複なし）"""
        return {instance.name for instance in self._instances}

    def all_instances(self) -> list[CourtBase]:
        """全てのコートインスタンスを取得"""
        return self._instances.copy()

    def search_by_keyword(self, keyword: str) -> list[CourtBase]:
        """キーワードでコートを検索（名前とvalueの両方を検索）"""
        keyword_lower = keyword.lower()
        return [
            instance
            for instance in self._instances
            if keyword_lower in instance.name.lower()
            or keyword_lower in instance.value.lower()
        ]

    def __len__(self) -> int:
        """登録されているコート数を返す"""
        return len(self._instances)

    def __iter__(self):
        """コートインスタンスをイテレート"""
        return iter(self._instances)

    def __contains__(self, name_or_value: str) -> bool:
        """コートが存在するかチェック"""
        return name_or_value in self.registry

    def __repr__(self) -> str:
        return f"CourtManager(courts={len(self)}, lottery_date={self.lottery_date})"
