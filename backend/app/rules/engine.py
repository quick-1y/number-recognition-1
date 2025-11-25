"""Rules Engine scaffolding with list-aware conditions and actions."""

import uuid
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from app.db.models import PlateListType


class RuleCondition(BaseModel):
    list_type: PlateListType | None = Field(None, description="Фильтр по типу списка")
    list_ids: list[str] = Field(default_factory=list, description="Конкретные списки для сопоставления")
    channel_ids: list[str] = Field(default_factory=list, description="Каналы, для которых действует правило")
    min_confidence: float | None = Field(None, description="Минимальная уверенность OCR")
    direction: str | None = Field(None, description="Направление движения up/down/any")
    schedule: dict[str, Any] | None = Field(None, description="Ограничения по времени/расписанию")
    anti_flood_seconds: int | None = Field(None, description="Cooldown на повторное срабатывание")
    min_frames: int | None = Field(None, description="Минимум кадров для события")


class RuleAction(BaseModel):
    trigger_relay: bool = Field(False, description="Активировать реле камеры")
    send_webhook: bool = Field(True, description="Отправить webhook о событии")
    record_clip: bool = Field(False, description="Записать клип вокруг события")
    annotate_ui: bool = Field(True, description="Добавить метку/подсветку в UI")


class RuleDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    conditions: RuleCondition
    actions: RuleAction


class PlateListPayload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: PlateListType
    priority: int = 100
    ttl_seconds: int | None = None
    schedule: dict | None = None
    description: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)


@dataclass
class RulesEngine:
    default_min_confidence: float
    default_anti_flood_seconds: int
    default_min_frames: int
    default_actions: RuleAction
    lists: dict[str, PlateListPayload] = field(default_factory=dict)
    rules: list[RuleDefinition] = field(default_factory=list)

    def register_list(self, payload: PlateListPayload) -> PlateListPayload:
        self.lists[payload.id] = payload
        return payload

    def add_item(self, list_id: str, item: dict[str, Any]) -> PlateListPayload:
        if list_id not in self.lists:
            raise KeyError(f"List {list_id} not found")
        self.lists[list_id].items.append(item)
        return self.lists[list_id]

    def register_rule(self, rule: RuleDefinition) -> RuleDefinition:
        self.rules.append(rule)
        return rule

    def describe(self) -> dict[str, Any]:
        return {
            "defaults": {
                "min_confidence": self.default_min_confidence,
                "anti_flood_seconds": self.default_anti_flood_seconds,
                "min_frames": self.default_min_frames,
                "actions": self.default_actions.model_dump(),
            },
            "rules": [rule.model_dump() for rule in self.rules],
            "lists": [list_payload.model_dump() for list_payload in self.lists.values()],
        }


def build_rules_engine(
    *,
    min_confidence: float,
    anti_flood_seconds: int,
    min_frames: int,
    default_actions: dict,
) -> RulesEngine:
    return RulesEngine(
        default_min_confidence=min_confidence,
        default_anti_flood_seconds=anti_flood_seconds,
        default_min_frames=min_frames,
        default_actions=RuleAction(**default_actions),
    )
