"""Small, dependency-free contracts for layout-intent generation.

The contracts enforce the two failure modes that caused rework:

1. two generators writing the same artifact path;
2. a downstream stage consuming a non-frozen artifact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Iterable


class ContractError(ValueError):
    """Base class for layout contract violations."""


class DuplicateWriterError(ContractError):
    """Raised when two producers claim the same output path."""


class FreezeError(ContractError):
    """Raised when an artifact is frozen without identity/verification."""


class Stage(str, Enum):
    SPEC = "spec"
    PRIMITIVE = "primitive"
    BANK = "bank"
    ASSEMBLY = "assembly"
    ROUTING = "routing"

    @property
    def order(self) -> int:
        return list(Stage).index(self)


class State(str, Enum):
    EXPLORATORY = "exploratory"
    DRAFT = "draft"
    FROZEN_STRUCTURAL = "frozen_structural"
    VERIFIED_SELECTED_RULES = "verified_selected_rules"
    SUPERSEDED = "superseded"

    @property
    def order(self) -> int:
        return list(State).index(self)


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    path: str
    stage: Stage
    producer: str
    state: State = State.DRAFT
    inputs: tuple[str, ...] = ()
    sha256: str | None = None
    checker: str | None = None
    note: str = ""

    def __post_init__(self) -> None:
        if not self.artifact_id:
            raise ContractError("artifact_id is required")
        if not self.path:
            raise ContractError("path is required")
        if Path(self.path).is_absolute():
            raise ContractError("artifact paths must be repository-relative")


@dataclass
class ArtifactRegistry:
    """One artifact -> one producer -> one current state."""

    _by_id: dict[str, Artifact] = field(default_factory=dict)
    _writer_by_path: dict[str, str] = field(default_factory=dict)

    def claim(self, path: str, producer: str) -> None:
        owner = self._writer_by_path.get(path)
        if owner is not None and owner != producer:
            raise DuplicateWriterError(
                f"{path} is already produced by {owner!r}; {producer!r} cannot write it"
            )
        self._writer_by_path[path] = producer

    def add(self, artifact: Artifact) -> Artifact:
        if artifact.artifact_id in self._by_id:
            raise ContractError(f"duplicate artifact id: {artifact.artifact_id}")
        self.claim(artifact.path, artifact.producer)
        if artifact.state in (State.FROZEN_STRUCTURAL, State.VERIFIED_SELECTED_RULES):
            if not artifact.sha256:
                raise FreezeError(f"{artifact.artifact_id} is frozen without sha256")
        self._by_id[artifact.artifact_id] = artifact
        return artifact

    def get(self, artifact_id: str) -> Artifact:
        try:
            return self._by_id[artifact_id]
        except KeyError as exc:
            raise ContractError(f"unknown artifact: {artifact_id}") from exc

    def replace(self, artifact: Artifact) -> Artifact:
        old = self.get(artifact.artifact_id)
        if old.path != artifact.path:
            raise ContractError("artifact path cannot change; create a new id/version")
        if old.producer != artifact.producer:
            raise DuplicateWriterError("artifact producer cannot change silently")
        if old.state is State.FROZEN_STRUCTURAL and artifact.state is State.DRAFT:
            raise ContractError("frozen artifact cannot be downgraded to draft")
        self._by_id[artifact.artifact_id] = artifact
        return artifact

    def freeze(
        self,
        artifact_id: str,
        *,
        sha256: str,
        checker: str | None = None,
        verified: bool = False,
    ) -> Artifact:
        old = self.get(artifact_id)
        if not sha256:
            raise FreezeError("freeze requires a sha256")
        if verified and not checker:
            raise FreezeError("verified_selected_rules requires a checker")
        state = State.VERIFIED_SELECTED_RULES if verified else State.FROZEN_STRUCTURAL
        return self.replace(
            Artifact(**{**old.__dict__, "state": state, "sha256": sha256, "checker": checker})
        )

    def require_frozen(self, artifact_id: str, *, consumer_stage: Stage) -> Artifact:
        art = self.get(artifact_id)
        if art.state not in (State.FROZEN_STRUCTURAL, State.VERIFIED_SELECTED_RULES):
            raise FreezeError(f"{artifact_id} is {art.state.value}, not frozen")
        if art.stage.order >= consumer_stage.order:
            raise ContractError(
                f"{artifact_id} at stage {art.stage.value} cannot feed {consumer_stage.value}"
            )
        return art

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen_paths: dict[str, str] = {}
        for art in self._by_id.values():
            if art.path in seen_paths:
                errors.append(f"path collision: {art.path}")
            seen_paths[art.path] = art.artifact_id
            if art.state in (State.FROZEN_STRUCTURAL, State.VERIFIED_SELECTED_RULES) and not art.sha256:
                errors.append(f"frozen without hash: {art.artifact_id}")
            if art.state is State.VERIFIED_SELECTED_RULES and not art.checker:
                errors.append(f"verified without checker: {art.artifact_id}")
            if art.state is State.SUPERSEDED and art.artifact_id in self._writer_by_path.values():
                errors.append(f"superseded artifact still owns a writer: {art.artifact_id}")
        return errors


def hash_file(path: str | Path) -> str:
    h = sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
