import numpy as np
from typing import Dict, List, Tuple, Any
import math

# Normalization Helpers
def normalize_indicator(indicator_name: str, raw_value: Any) -> float:
    """
    Normalize raw data to a [0, 1] scale based on the Energy Dignity Model specification.
    
    Args:
        indicator_name: The indicator code (e.g., 'A1', 'R3')
        raw_value: The raw data value
        
    Returns:
        Normalized score in [0, 1]
    """
    if indicator_name == 'A1':  # Electricity connection
        return 1.0 if raw_value else 0.0
    elif indicator_name == 'A2':  # Clean cooking fuel
        clean_fuels = ['LPG', 'PNG', 'Electricity', 'Biogas']
        return 1.0 if raw_value in clean_fuels else 0.0
    elif indicator_name == 'A3':  # Basic lighting adequacy (rooms)
        if raw_value >= 4: return 1.0
        if raw_value >= 1: return 0.5
        return 0.0
    elif indicator_name == 'E1':  # Energy expenditure ratio
        # x = 1 - min(ratio, 0.15) / 0.15
        return 1.0 - min(raw_value, 0.15) / 0.15
    elif indicator_name == 'E2':  # LPG refills per year
        if raw_value >= 6: return 1.0
        if raw_value >= 3: return 0.5
        return 0.0
    elif indicator_name == 'E3':  # Bill payment ease
        if raw_value == 'never_missed': return 1.0
        if raw_value == 'sometimes_delayed': return 0.5
        return 0.0
    elif indicator_name == 'R1':  # Hours of electricity per day
        return min(raw_value / 24.0, 1.0)
    elif indicator_name == 'R2':  # Voltage stability
        if raw_value == 'no_issues': return 1.0
        if raw_value == 'occasional': return 0.5
        return 0.0
    elif indicator_name == 'R3':  # Unplanned outages per month
        return math.exp(-0.2 * raw_value)
    elif indicator_name == 'H1':  # Cooking location
        if raw_value == 'separate_ventilated': return 1.0
        if raw_value == 'separate_no_vent': return 0.5
        return 0.0
    elif indicator_name == 'H2':  # Fuel type cleanliness
        ladder = {'Electricity': 1.0, 'LPG': 0.9, 'PNG': 0.9, 'Biogas': 0.8, 'Kerosene': 0.3, 'Coal': 0.15, 'Wood': 0.1, 'Dung': 0.05}
        return ladder.get(raw_value, 0.0)
    elif indicator_name == 'H3':  # Indoor air quality proxy
        # 1 if clean + vent, 0.5 if clean only, 0 otherwise
        if raw_value == 'clean_and_vent': return 1.0
        if raw_value == 'clean_only': return 0.5
        return 0.0
    elif indicator_name == 'P1':  # Appliance ownership
        return min(raw_value / 8.0, 1.0)
    elif indicator_name == 'P2':  # Study lighting
        return 1.0 if raw_value else 0.0
    elif indicator_name == 'P3':  # Productive use
        if raw_value == 'active': return 1.0
        if raw_value == 'constrained': return 0.5
        return 0.0
    elif indicator_name == 'G1':  # Fuel choice
        if raw_value == 'free_choice': return 1.0
        if raw_value == 'constrained': return 0.5
        return 0.0
    elif indicator_name == 'G2':  # Metering fairness
        if raw_value == 'metered_fair': return 1.0
        if raw_value == 'flat_rate': return 0.5
        return 0.0
    elif indicator_name == 'G3':  # Grievance redressal
        if raw_value == 'resolved': return 1.0
        if raw_value == 'known_unresolved': return 0.5
        return 0.0
    elif indicator_name == 'G4':  # Participation
        return 1.0 if raw_value else 0.0
    
    raise ValueError(f"Unknown indicator: {indicator_name}")

class EnergyDignityModel:
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize the Energy Dignity Index (EDI) model.

        Args:
            weights: Dictionary of dimension weights. If None, uses baseline weights.
        """
        # Baseline weights from the model specification
        self.baseline_weights = {
            'A': 0.20,  # Basic Access
            'E': 0.20,  # Economic Affordability
            'R': 0.15,  # Reliability & Quality
            'H': 0.15,  # Health & Environment
            'P': 0.15,  # Productive & Developmental Adequacy
            'G': 0.15   # Agency & Empowerment
        }
        
        self.weights = weights if weights else self.baseline_weights
        self.validate_weights()
        
        # Indicator weights within dimensions
        self.indicator_weights = {
            'A': {'A1': 0.4, 'A2': 0.4, 'A3': 0.2},
            'E': {'E1': 0.4, 'E2': 0.35, 'E3': 0.25},
            'R': {'R1': 0.45, 'R2': 0.25, 'R3': 0.30},
            'H': {'H1': 0.25, 'H2': 0.45, 'H3': 0.30},
            'P': {'P1': 0.4, 'P2': 0.3, 'P3': 0.3},
            'G': {'G1': 0.3, 'G2': 0.25, 'G3': 0.25, 'G4': 0.20}
        }
        
        # Deprivation cutoffs (z-values) for Alkire-Foster method
        self.deprivation_cutoffs = {
            'A1': 0.999, 'A2': 0.999,  # Must have access (1.0) to not be deprived
            'E1': 0.333, 'E2': 0.666,  # Affordability thresholds
            'R1': 0.833, 'R3': 0.548,  # 20h/24h and e^(-0.2*3)
            'H1': 0.999, 'H2': 0.5,   # Health thresholds
            'P1': 0.375, 'P2': 0.999,  # Productive thresholds
            'G1': 0.999, 'G3': 0.999   # Agency thresholds
        }
        
    def validate_weights(self):
        """Ensure dimension weights sum to 1.0."""
        total = sum(self.weights.values())
        if not np.isclose(total, 1.0):
            raise ValueError(f"Dimension weights must sum to 1.0, got {total}")

    def calculate_dimension_score(self, dimension: str, indicators: Dict[str, float]) -> float:
        """
        Calculate the score for a single dimension.
        
        Args:
            dimension: Dimension code (A, E, R, H, P, G)
            indicators: Dictionary of indicator scores for that dimension
            
        Returns:
            Dimension score S_{h,d} in [0, 1]
        """
        if dimension not in self.indicator_weights:
            raise ValueError(f"Unknown dimension: {dimension}")
            
        weights = self.indicator_weights[dimension]
        score = 0.0
        
        for indicator, weight in weights.items():
            if indicator not in indicators:
                raise ValueError(f"Missing indicator {indicator} for dimension {dimension}")
            score += weight * indicators[indicator]
            
        return score

    def calculate_edi(self, household_data: Dict[str, Any]) -> float:
        """
        Calculate the Energy Dignity Index for a single household.
        
        Args:
            household_data: Dictionary with dimension scores or raw indicators
            
        Returns:
            EDI score in [0, 1]
        """
        dimension_scores = {}
        
        # If dimension scores are provided directly
        if 'dimension_scores' in household_data:
            dimension_scores = household_data['dimension_scores']
        else:
            # Calculate from raw indicators
            for dimension in ['A', 'E', 'R', 'H', 'P', 'G']:
                if dimension in household_data:
                    dimension_scores[dimension] = self.calculate_dimension_score(
                        dimension, household_data[dimension]
                    )
                else:
                    raise ValueError(f"Missing data for dimension {dimension}")
        
        # Calculate weighted geometric mean
        edi = 1.0
        for dimension, score in dimension_scores.items():
            if score < 0 or score > 1:
                raise ValueError(f"Dimension score for {dimension} must be in [0,1], got {score}")
            
            # Handle zero scores (complete deprivation)
            if score == 0:
                return 0.0
                
            edi *= pow(score, self.weights[dimension])
            
        return edi

    def calculate_deprivation_score(self, household_data: Dict[str, float]) -> float:
        """
        Calculate the Alkire-Foster deprivation score c_h for a household.
        
        Args:
            household_data: Dictionary of normalized indicator scores
            
        Returns:
            Weighted deprivation score
        """
        c_h = 0.0
        
        for dimension, indicators in self.indicator_weights.items():
            for indicator, ind_weight in indicators.items():
                if indicator not in household_data:
                    raise ValueError(f"Missing indicator {indicator}")
                    
                # Check if household is deprived in this indicator
                # Only check if we have a specific cutoff for this indicator
                if indicator in self.deprivation_cutoffs:
                    if household_data[indicator] < self.deprivation_cutoffs[indicator]:
                        c_h += self.weights[dimension] * ind_weight
                    
        return c_h

    def calculate_m0(self, households: List[Dict[str, float]], k: float = 0.333) -> Tuple[float, float, float]:
        """
        Calculate the Adjusted Headcount Ratio (M0) using Alkire-Foster method.
        
        Args:
            households: List of household indicator dictionaries
            k: Dignity deficiency cutoff threshold
            
        Returns:
            Tuple of (H, I, M0) - headcount, intensity, and adjusted headcount ratio
        """
        n = len(households)
        deprivation_scores = [self.calculate_deprivation_score(h) for h in households]
        
        # Count deficient households
        deficient = [1 for c in deprivation_scores if c >= k]
        H = sum(deficient) / n if n > 0 else 0
        
        # Calculate intensity
        if sum(deficient) > 0:
            I = sum(c * d for c, d in zip(deprivation_scores, deficient)) / sum(deficient)
        else:
            I = 0
            
        M0 = H * I
        
        return H, I, M0

    def calculate_regional_edi(self, households: List[Dict[str, Any]]) -> float:
        """Calculate mean EDI for a region."""
        if not households:
            return 0.0
            
        edi_scores = [self.calculate_edi(h) for h in households]
        return np.mean(edi_scores)

    def dimensional_contribution(self, households: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate each dimension's contribution to overall dignity deficiency.
        
        Returns:
            Dictionary mapping dimension to its contribution percentage
        """
        total_deprivation = 0
        dimension_deprivation = {d: 0 for d in self.indicator_weights}
        
        for household in households:
            for dimension, indicators in self.indicator_weights.items():
                for indicator, ind_weight in indicators.items():
                    if indicator not in household:
                        raise ValueError(f"Missing indicator {indicator}")
                        
                    # Only check if we have a specific cutoff for this indicator
                    if indicator in self.deprivation_cutoffs:
                        if household[indicator] < self.deprivation_cutoffs[indicator]:
                            contribution = self.weights[dimension] * ind_weight
                            dimension_deprivation[dimension] += contribution
                            total_deprivation += contribution
        
        if total_deprivation == 0:
            return {d: 0 for d in dimension_deprivation}
            
        return {
            d: (val / total_deprivation) * 100 
            for d, val in dimension_deprivation.items()
        }

    def marginal_impact(self, dimension_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate the partial derivatives ∂EDI/∂S_d for policy targeting.
        
        Args:
            dimension_scores: Current dimension scores
            
        Returns:
            Dictionary of marginal impacts for each dimension
        """
        edi = self.calculate_edi({'dimension_scores': dimension_scores})
        
        if edi == 0:
            return {d: 0 for d in dimension_scores}
            
        marginal_impacts = {}
        for dimension, score in dimension_scores.items():
            if score > 0:
                marginal_impacts[dimension] = self.weights[dimension] * (edi / score)
            else:
                marginal_impacts[dimension] = float('inf')
                
        return marginal_impacts
