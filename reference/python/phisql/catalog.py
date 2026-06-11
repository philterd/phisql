# Copyright 2026 Philterd, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
In-memory view of the PhiSQL spec catalog YAML files.

The catalog files under ``spec/v1.0/catalog/`` are the single source of truth
for entity types, strategies, keywords, and predicate forms. The compiler is
driven entirely by them; this module loads the subset the compiler needs
(entity types and strategies). Lookups by name are case-insensitive, matching
the language spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import yaml

from . import _paths


@dataclass(frozen=True)
class StrategyArg:
    """A named argument allowed on a strategy."""

    name: str
    phileas_field: Optional[str]
    type: Optional[str]
    enum_values: tuple = ()


@dataclass(frozen=True)
class Strategy:
    """Catalog entry for a filter strategy."""

    name: str
    phileas_enum: str
    args: tuple = ()

    def find_arg(self, arg_name: Optional[str]) -> Optional[StrategyArg]:
        """Returns the strategy argument with the given name, or None."""
        if arg_name is None:
            return None
        for arg in self.args:
            if arg.name.lower() == arg_name.lower():
                return arg
        return None


@dataclass(frozen=True)
class EntityType:
    """Catalog entry for an entity type."""

    name: str
    phileas_field: str
    phileas_strategies_field: str


class Catalog:
    """Loaded entity-type and strategy catalogs, keyed case-insensitively."""

    #: Catalog version (matches the spec version this catalog targets).
    VERSION = "v1.0"

    def __init__(self, entities_by_name: dict, strategies_by_name: dict):
        self._entities_by_name = entities_by_name
        self._strategies_by_name = strategies_by_name

    @classmethod
    def load_default(cls) -> "Catalog":
        """Loads the v1.0 catalog from the spec ``catalog/`` directory."""
        catalog_dir = _paths.catalog_dir()

        entities = {}
        with (catalog_dir / "entity-types.yaml").open(encoding="utf-8") as fh:
            root = yaml.safe_load(fh)
        for item in root.get("entities") or []:
            entity = EntityType(
                name=item["name"],
                phileas_field=item["phileas_field"],
                phileas_strategies_field=item["phileas_strategies_field"],
            )
            entities[entity.name.upper()] = entity

        strategies = {}
        with (catalog_dir / "strategies.yaml").open(encoding="utf-8") as fh:
            root = yaml.safe_load(fh)
        for item in root.get("strategies") or []:
            args = []
            for raw in item.get("args") or []:
                enum_values = raw.get("enum_values") or []
                args.append(
                    StrategyArg(
                        name=raw["name"],
                        phileas_field=raw.get("phileas_field"),
                        type=raw.get("type"),
                        enum_values=tuple(enum_values),
                    )
                )
            strategy = Strategy(
                name=item["name"],
                phileas_enum=item["phileas_enum"],
                args=tuple(args),
            )
            strategies[strategy.name.upper()] = strategy

        return cls(entities, strategies)

    def get_entity(self, name: Optional[str]) -> Optional[EntityType]:
        """Returns the entity type with the given (case-insensitive) name, or None."""
        if name is None:
            return None
        return self._entities_by_name.get(name.upper())

    def get_strategy(self, name: Optional[str]) -> Optional[Strategy]:
        """Returns the strategy with the given (case-insensitive) name, or None."""
        if name is None:
            return None
        return self._strategies_by_name.get(name.upper())
