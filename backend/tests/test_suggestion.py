"""
Tests for the suggestion engine: decision rules for both modes.
Validates that the correct architecture is recommended for each scenario.
"""
import pytest

from app.suggestion.engine import suggest_architecture, PATTERNS


# ── Brownfield Decision Rules ────────────────────────────────────

class TestBrownfieldSuggestion:
    """Verify brownfield decision table."""

    def test_high_instability_hexagonal(self):
        """avg_instability > 0.8 → Hexagonal."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.85,
            dependency_density=0.3,
            total_modules=8,
            risk_score=0.65,
            per_module=[{"module": "a", "fan_out": 4}],
        )
        assert result["suggested_architecture"] == "Hexagonal Architecture"

    def test_high_fan_out_hexagonal(self):
        """max fan-out > 10 → Hexagonal."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.5,
            dependency_density=0.3,
            total_modules=8,
            risk_score=0.45,
            per_module=[{"module": "hub", "fan_out": 12}],
        )
        assert result["suggested_architecture"] == "Hexagonal Architecture"

    def test_high_risk_layered(self):
        """risk_score > 0.7 (but instability ≤ 0.8, fan_out ≤ 10) → Layered."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.7,
            dependency_density=0.8,
            total_modules=8,
            risk_score=0.75,
            per_module=[{"module": "a", "fan_out": 5}],
        )
        assert result["suggested_architecture"] == "Layered Architecture"

    def test_low_risk_many_modules_microservices(self):
        """risk < 0.5, modules > 15 → Microservices."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.3,
            dependency_density=0.1,
            total_modules=20,
            risk_score=0.25,
            per_module=[{"module": "a", "fan_out": 2}],
        )
        assert result["suggested_architecture"] == "Microservices"

    def test_moderate_risk_mvc(self):
        """0.4 ≤ risk ≤ 0.7 → MVC."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.5,
            dependency_density=0.4,
            total_modules=8,
            risk_score=0.55,
            per_module=[{"module": "a", "fan_out": 3}],
        )
        assert result["suggested_architecture"] == "MVC"

    def test_low_risk_few_modules_monolith(self):
        """risk < 0.4, few modules → Modular Monolith."""
        result = suggest_architecture(
            mode="brownfield",
            avg_instability=0.2,
            dependency_density=0.1,
            total_modules=5,
            risk_score=0.17,
            per_module=[{"module": "a", "fan_out": 1}],
        )
        assert result["suggested_architecture"] == "Modular Monolith"


# ── Greenfield Decision Rules ────────────────────────────────────

class TestGreenfieldSuggestion:
    """Verify greenfield decision table."""

    def test_high_scale_high_complexity_microservices(self):
        result = suggest_architecture(
            mode="greenfield", scalability="high", complexity="high"
        )
        assert result["suggested_architecture"] == "Microservices"

    def test_high_scale_medium_complexity_microservices(self):
        result = suggest_architecture(
            mode="greenfield", scalability="high", complexity="medium"
        )
        assert result["suggested_architecture"] == "Microservices"

    def test_high_complexity_low_scale_hexagonal(self):
        result = suggest_architecture(
            mode="greenfield", scalability="low", complexity="high"
        )
        assert result["suggested_architecture"] == "Hexagonal Architecture"

    def test_medium_all_layered(self):
        result = suggest_architecture(
            mode="greenfield", scalability="medium", complexity="medium"
        )
        assert result["suggested_architecture"] == "Layered Architecture"

    def test_high_scale_low_complexity_mvc(self):
        result = suggest_architecture(
            mode="greenfield", scalability="high", complexity="low"
        )
        assert result["suggested_architecture"] == "MVC"

    def test_low_all_monolith(self):
        result = suggest_architecture(
            mode="greenfield", scalability="low", complexity="low"
        )
        assert result["suggested_architecture"] == "Modular Monolith"


# ── Response Shape Tests ─────────────────────────────────────────

class TestSuggestionResponseShape:
    """Verify the suggestion response always has the required fields."""

    def test_has_required_fields(self):
        result = suggest_architecture(mode="greenfield", scalability="medium", complexity="medium")
        assert "suggested_architecture" in result
        assert "reason" in result
        assert "pattern_description" in result
        assert "pros" in result
        assert "cons" in result

    def test_reason_is_nonempty(self):
        result = suggest_architecture(mode="greenfield", scalability="medium", complexity="medium")
        assert len(result["reason"]) > 10

    def test_pattern_in_catalog(self):
        result = suggest_architecture(mode="greenfield", scalability="high", complexity="high")
        assert result["suggested_architecture"] in PATTERNS

    def test_pros_cons_are_lists(self):
        result = suggest_architecture(mode="greenfield", scalability="medium", complexity="medium")
        assert isinstance(result["pros"], list)
        assert isinstance(result["cons"], list)
        assert len(result["pros"]) > 0
        assert len(result["cons"]) > 0

    def test_unknown_mode_defaults_to_mvc(self):
        result = suggest_architecture(mode="unknown")
        assert result["suggested_architecture"] == "MVC"
