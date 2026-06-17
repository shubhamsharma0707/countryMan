"""
Enhanced Energy Dignity Index Model
Stronger, more accurate model with:
- Ensemble scoring (geometric + arithmetic hybrid)
- Dimension-level confidence intervals
- Bayesian prior updating from historical data
- Sensitivity analysis
- Vulnerability risk scoring
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DimensionResult:
    score: float
    confidence_low: float
    confidence_high: float
    weight: float
    contribution: float  # fractional contribution to EDI


@dataclass
class EDIResult:
    edi: float
    edi_lower: float
    edi_upper: float
    deprivation_score: float
    vulnerability_class: str  # 'High' / 'Medium' / 'Low'
    dimensions: Dict[str, DimensionResult] = field(default_factory=dict)
    risk_flags: List[str] = field(default_factory=list)


class EnhancedEDIModel:
    """
    Production-grade Energy Dignity Index model.

    Improvements over baseline:
    1. Ensemble aggregation: geometric mean (multiplicative deprivation penalty)
       PLUS an adaptive arithmetic component for low-score recovery.
    2. Bayesian weight updating from observed state-level outcomes.
    3. Bootstrap confidence intervals on EDI.
    4. Multi-cutoff Alkire-Foster deprivation (k=1/3, 1/2, 2/3).
    5. Categorical vulnerability classification.
    6. Sensitivity analysis via perturbation.
    """

    # ── Baseline dimension weights (sum = 1.0) ──────────────────────────────
    BASELINE_WEIGHTS: Dict[str, float] = {
        "A": 0.22,  # Basic Access — highest priority (Saubhagya impact)
        "E": 0.20,  # Economic Affordability
        "R": 0.15,  # Reliability & Quality
        "H": 0.18,  # Health & Environment — elevated (clean cooking crisis)
        "P": 0.13,  # Productive & Developmental Use
        "G": 0.12,  # Agency & Empowerment
    }

    # ── Indicator weights within each dimension ──────────────────────────────
    INDICATOR_WEIGHTS: Dict[str, Dict[str, float]] = {
        "A": {"A1": 0.40, "A2": 0.40, "A3": 0.20},
        "E": {"E1": 0.40, "E2": 0.35, "E3": 0.25},
        "R": {"R1": 0.45, "R2": 0.25, "R3": 0.30},
        "H": {"H1": 0.25, "H2": 0.45, "H3": 0.30},
        "P": {"P1": 0.40, "P2": 0.30, "P3": 0.30},
        "G": {"G1": 0.30, "G2": 0.25, "G3": 0.25, "G4": 0.20},
    }

    # ── Deprivation cutoffs (z_d) ───────────────────────────────────────────
    DEPRIVATION_CUTOFFS: Dict[str, float] = {
        "A1": 0.999, "A2": 0.999,
        "E1": 0.333, "E2": 0.666,
        "R1": 0.833, "R3": 0.548,
        "H1": 0.999, "H2": 0.500,
        "P1": 0.375, "P2": 0.999,
        "G1": 0.999, "G3": 0.999,
    }

    # Ensemble blend: α * geometric + (1-α) * arithmetic
    ENSEMBLE_ALPHA: float = 0.70

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        bayesian_prior: Optional[Dict[str, float]] = None,
    ):
        self.weights = weights or dict(self.BASELINE_WEIGHTS)
        self._validate_weights()

        # Optional Bayesian prior from historical observation counts
        self.bayesian_prior = bayesian_prior or {d: 10.0 for d in "AERHPG"}

    # ── Public API ──────────────────────────────────────────────────────────

    def compute(
        self,
        dimension_scores: Dict[str, float],
        n_bootstrap: int = 200,
        noise_std: float = 0.02,
    ) -> EDIResult:
        """
        Compute full EDI with confidence intervals.

        Args:
            dimension_scores: {dim: score} mapping, scores in [0, 1]
            n_bootstrap: number of bootstrap replicates for CI
            noise_std: measurement noise injected per replicate
        """
        # Validate
        for d, s in dimension_scores.items():
            if not (0.0 <= s <= 1.0):
                raise ValueError(f"Score for {d} must be in [0, 1], got {s}")

        # Point estimate
        edi_point = self._ensemble_edi(dimension_scores)

        # Bootstrap CI
        boot_edis = []
        rng = np.random.RandomState(2024)
        for _ in range(n_bootstrap):
            noisy = {
                d: float(np.clip(s + rng.normal(0, noise_std), 0.01, 1.0))
                for d, s in dimension_scores.items()
            }
            boot_edis.append(self._ensemble_edi(noisy))

        edi_lower = float(np.percentile(boot_edis, 5))
        edi_upper = float(np.percentile(boot_edis, 95))

        # Deprivation (for dimension score inputs we create synthetic indicators)
        dep_score = self._deprivation_from_dim_scores(dimension_scores)

        # Dimension results
        dims = {}
        for d, s in dimension_scores.items():
            boot_dim = [
                float(np.clip(s + np.random.normal(0, noise_std), 0, 1))
                for _ in range(n_bootstrap)
            ]
            dims[d] = DimensionResult(
                score=round(s, 4),
                confidence_low=round(float(np.percentile(boot_dim, 5)), 4),
                confidence_high=round(float(np.percentile(boot_dim, 95)), 4),
                weight=self.weights.get(d, 0),
                contribution=round(self.weights.get(d, 0) * s / max(edi_point, 1e-6), 4),
            )

        # Vulnerability class
        vuln = self._classify_vulnerability(edi_point, dep_score)
        risks = self._detect_risk_flags(dimension_scores)

        return EDIResult(
            edi=round(edi_point, 4),
            edi_lower=round(edi_lower, 4),
            edi_upper=round(edi_upper, 4),
            deprivation_score=round(dep_score, 4),
            vulnerability_class=vuln,
            dimensions=dims,
            risk_flags=risks,
        )

    def compute_for_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Vectorised computation for large datasets."""
        dims = list("AERHPG")
        dim_cols = {d: f"S_{d}" for d in dims}

        # Ensure columns exist
        for d, col in dim_cols.items():
            if col not in df.columns:
                df[col] = 0.5  # neutral imputation

        results = df.copy()

        # Geometric component
        geo = np.ones(len(df))
        arith = np.zeros(len(df))
        for d, col in dim_cols.items():
            w = self.weights.get(d, 0)
            scores = df[col].clip(1e-6, 1.0).values
            geo *= np.power(scores, w)
            arith += w * scores

        results["EDI_geo"] = geo
        results["EDI_arith"] = arith
        results["EDI"] = (
            self.ENSEMBLE_ALPHA * geo + (1 - self.ENSEMBLE_ALPHA) * arith
        ).round(4)

        # Deprivation approximation from dimension scores
        results["deprivation_score"] = (1.0 - results["EDI"]).clip(0, 1).round(4)

        return results

    def sensitivity_analysis(
        self, dimension_scores: Dict[str, float], delta: float = 0.05
    ) -> pd.DataFrame:
        """
        Compute ∂EDI/∂S_d numerically for each dimension.
        Returns a dataframe sorted by impact magnitude.
        """
        base_edi = self._ensemble_edi(dimension_scores)
        rows = []
        for d in dimension_scores:
            up_scores = dict(dimension_scores)
            up_scores[d] = min(1.0, up_scores[d] + delta)
            up_edi = self._ensemble_edi(up_scores)

            down_scores = dict(dimension_scores)
            down_scores[d] = max(0.0, down_scores[d] - delta)
            down_edi = self._ensemble_edi(down_scores)

            rows.append(
                {
                    "Dimension": d,
                    "Current Score": round(dimension_scores[d], 4),
                    "Sensitivity (∂EDI/∂S)": round(
                        (up_edi - down_edi) / (2 * delta), 5
                    ),
                    "EDI Gain (+5%)": round(up_edi - base_edi, 5),
                    "Policy Priority": "High" if (up_edi - base_edi) > 0.015 else "Medium",
                }
            )

        return pd.DataFrame(rows).sort_values(
            "EDI Gain (+5%)", ascending=False
        )

    def alkire_foster(
        self,
        df: pd.DataFrame,
        k: float = 0.333,
    ) -> Dict:
        """
        Multi-dimensional poverty measure (Alkire-Foster).

        Args:
            df: DataFrame with S_A … S_G columns
            k: poverty cutoff (fraction of max weighted deprivation)

        Returns dict with H (headcount), A (intensity), M0 (adjusted ratio).
        """
        dim_cols = {d: f"S_{d}" for d in "AERHPG"}
        c_i = pd.Series(0.0, index=df.index)

        for d, col in dim_cols.items():
            if col not in df.columns:
                continue
            w = self.weights.get(d, 0)
            c_i += w * (df[col] < 0.4).astype(float)

        poor = c_i >= k
        H = poor.mean()
        A = c_i[poor].mean() if poor.sum() > 0 else 0.0
        M0 = H * A
        return {"H": round(H, 4), "A": round(A, 4), "M0": round(M0, 4), "k": k}

    def bayesian_weight_update(
        self,
        observed_outcomes: Dict[str, List[float]],
    ) -> Dict[str, float]:
        """
        Update dimension weights using observed EDI outcomes via
        a Dirichlet-like Bayesian approach.

        Args:
            observed_outcomes: {dim: [list of observed scores]}

        Returns updated weight dict.
        """
        updated = {}
        total = 0.0
        for d in self.weights:
            obs = observed_outcomes.get(d, [])
            if obs:
                mean_obs = float(np.mean(obs))
                # Higher observed scores → dimension more achievable → slight weight decrease
                # Lower observed scores → dimension bottleneck → slight weight increase
                gap = 1.0 - mean_obs
                prior_count = self.bayesian_prior.get(d, 10.0)
                posterior = self.weights[d] * prior_count + gap
                updated[d] = posterior
            else:
                updated[d] = self.weights[d] * self.bayesian_prior.get(d, 10.0)
            total += updated[d]

        # Normalize
        return {d: round(v / total, 4) for d, v in updated.items()}

    def project_edi(
        self,
        current_scores: Dict[str, float],
        growth_rates: Dict[str, float],
        years: int = 5,
    ) -> List[Dict]:
        """Project EDI trajectories under given dimension growth rates."""
        scores = dict(current_scores)
        projections = []
        for yr in range(years + 1):
            edi = self._ensemble_edi(scores)
            projections.append(
                {
                    "year": yr,
                    "EDI": round(edi, 4),
                    **{f"S_{d}": round(s, 4) for d, s in scores.items()},
                }
            )
            for d in scores:
                if d in growth_rates:
                    scores[d] = float(np.clip(scores[d] * (1 + growth_rates[d]), 0, 1))
        return projections

    def calculate_policy_impact(
        self,
        baseline_scores: Dict[str, float],
        intervention_dimension: str,
        intervention_magnitude: float,
    ) -> Dict:
        baseline_edi = self._ensemble_edi(baseline_scores)
        new_scores = dict(baseline_scores)
        new_scores[intervention_dimension] = float(
            np.clip(new_scores[intervention_dimension] + intervention_magnitude, 0, 1)
        )
        new_edi = self._ensemble_edi(new_scores)
        improvement = new_edi - baseline_edi
        pct = (improvement / baseline_edi * 100) if baseline_edi > 0 else 0
        return {
            "baseline_edi": round(baseline_edi, 4),
            "intervention_edi": round(new_edi, 4),
            "edi_improvement": round(improvement, 4),
            "percent_improvement": round(pct, 2),
            "target_dimension": intervention_dimension,
            "intervention_magnitude": intervention_magnitude,
        }

    # ── Internal helpers ────────────────────────────────────────────────────

    def _ensemble_edi(self, scores: Dict[str, float]) -> float:
        """Compute ensemble EDI = α * geo + (1−α) * arith."""
        geo, arith = 1.0, 0.0
        for d, s in scores.items():
            w = self.weights.get(d, 0)
            clamped = max(s, 1e-6)
            geo *= clamped ** w
            arith += w * clamped
        return float(self.ENSEMBLE_ALPHA * geo + (1 - self.ENSEMBLE_ALPHA) * arith)

    def _deprivation_from_dim_scores(self, scores: Dict[str, float]) -> float:
        """Approximate deprivation from dimension scores (lower = better)."""
        dep = 0.0
        for d, s in scores.items():
            w = self.weights.get(d, 0)
            if s < 0.4:
                dep += w * (0.4 - s) / 0.4
        return float(np.clip(dep, 0, 1))

    def _classify_vulnerability(self, edi: float, dep: float) -> str:
        if edi < 0.35 or dep > 0.6:
            return "High"
        elif edi < 0.55 or dep > 0.35:
            return "Medium"
        return "Low"

    def _detect_risk_flags(self, scores: Dict[str, float]) -> List[str]:
        flags = []
        labels = {
            "A": "Basic Access", "E": "Affordability",
            "R": "Reliability", "H": "Health & Environment",
            "P": "Productive Use", "G": "Agency",
        }
        for d, s in scores.items():
            if s < 0.25:
                flags.append(f"Critical: {labels.get(d, d)} severely deprived (score={s:.2f})")
            elif s < 0.40:
                flags.append(f"Warning: {labels.get(d, d)} below dignity threshold (score={s:.2f})")
        return flags

    def _validate_weights(self):
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0, atol=1e-3):
            raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")


# ── Convenience function ────────────────────────────────────────────────────

def compute_edi_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Batch-compute EDI for a state-level dataframe."""
    model = EnhancedEDIModel()
    return model.compute_for_dataframe(df)
