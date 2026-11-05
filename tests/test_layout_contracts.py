"""Guardrails for the layout-intent architecture."""
import unittest

from a2l.layout import (
    Artifact,
    ArtifactRegistry,
    ContractError,
    DuplicateWriterError,
    FreezeError,
    Stage,
    State,
)


class LayoutContractsTest(unittest.TestCase):
    def test_two_producers_cannot_claim_same_path(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        with self.assertRaises(DuplicateWriterError):
            reg.add(Artifact("bank.b", "banks/a.svg", Stage.BANK, "gen-b"))

    def test_freeze_requires_hash(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        with self.assertRaises(FreezeError):
            reg.freeze("bank.a", sha256="")

    def test_downstream_cannot_consume_draft(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        with self.assertRaises(FreezeError):
            reg.require_frozen("bank.a", consumer_stage=Stage.ASSEMBLY)

    def test_downstream_can_consume_frozen(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        reg.freeze("bank.a", sha256="abc")
        art = reg.require_frozen("bank.a", consumer_stage=Stage.ASSEMBLY)
        self.assertIs(art.state, State.FROZEN_STRUCTURAL)

    def test_verified_requires_checker(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        with self.assertRaises(FreezeError):
            reg.freeze("bank.a", sha256="abc", verified=True)

    def test_frozen_cannot_be_downgraded(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a"))
        reg.freeze("bank.a", sha256="abc")
        with self.assertRaises(ContractError):
            reg.replace(Artifact("bank.a", "banks/a.svg", Stage.BANK, "gen-a", State.DRAFT))

    def test_stage_order_is_forward_only(self):
        reg = ArtifactRegistry()
        reg.add(Artifact("assembly", "assembly.svg", Stage.ASSEMBLY, "gen-a"))
        reg.freeze("assembly", sha256="abc")
        with self.assertRaises(ContractError):
            reg.require_frozen("assembly", consumer_stage=Stage.BANK)


if __name__ == "__main__":
    unittest.main()
