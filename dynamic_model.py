"""
Dynamic Time-Series Model for Energy Dignity Index (EDI)
Tracks changes in energy dignity over time and calculates marginal impacts.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from energy_dignity_model import EnergyDignityModel


class DynamicEDIModel:
    """
    Dynamic model for tracking Energy Dignity Index over time.
    
    This model extends the static EDI calculation to capture temporal
    evolution of energy dignity at household, regional, and national levels.
    """
    
    def __init__(self, base_model: Optional[EnergyDignityModel] = None):
        """
        Initialize the dynamic EDI model.
        
        Args:
            base_model: Base EnergyDignityModel instance. If None, creates new one.
        """
        self.base_model = base_model or EnergyDignityModel()
        self.time_series_data = None
        
    def calculate_temporal_edi(
        self, 
        households: pd.DataFrame,
        time_column: str = 'year'
    ) -> pd.DataFrame:
        """
        Calculate EDI scores across multiple time periods.
        
        Args:
            households: DataFrame with household data including time column
            time_column: Name of column containing time period (e.g., 'year')
            
        Returns:
            DataFrame with temporal EDI scores
        """
        results = []
        
        for period in sorted(households[time_column].unique()):
            period_data = households[households[time_column] == period]
            
            # Calculate EDI for each household in this period
            for idx, row in period_data.iterrows():
                indicators = {col: row[col] for col in period_data.columns 
                            if len(col) == 2 and col[0] in 'AERHPG'}
                
                # Calculate dimension scores
                dimension_scores = {}
                for dim in ['A', 'E', 'R', 'H', 'P', 'G']:
                    dim_indicators = {k: v for k, v in indicators.items() if k.startswith(dim)}
                    if dim_indicators:
                        dimension_scores[dim] = self.base_model.calculate_dimension_score(
                            dim, dim_indicators
                        )
                
                # Calculate EDI
                edi = self.base_model.calculate_edi({'dimension_scores': dimension_scores})
                
                # Calculate deprivation score
                deprivation = self.base_model.calculate_deprivation_score(indicators)
                
                results.append({
                    'household_id': row.get('household_id', f'HH_{idx}'),
                    'state': row.get('state', 'Unknown'),
                    'area': row.get('area', 'Unknown'),
                    'period': period,
                    'EDI': edi,
                    'deprivation_score': deprivation,
                    **{f'S_{dim}': score for dim, score in dimension_scores.items()}
                })
        
        self.time_series_data = pd.DataFrame(results)
        return self.time_series_data
    
    def calculate_edi_trends(
        self, 
        time_series_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Calculate trends in EDI over time.
        
        Args:
            time_series_data: DataFrame with temporal EDI scores
            
        Returns:
            DataFrame with trend statistics by state/area
        """
        data = time_series_data if time_series_data is not None else self.time_series_data
        if data is None:
            raise ValueError("No time series data available. Run calculate_temporal_edi first.")
        
        trends = []
        
        for state in data['state'].unique():
            for area in data['area'].unique():
                subset = data[(data['state'] == state) & (data['area'] == area)]
                
                if len(subset['period'].unique()) < 2:
                    continue
                
                # Calculate trend for each metric
                for metric in ['EDI'] + [f'S_{d}' for d in 'AERHPG']:
                    periods = sorted(subset['period'].unique())
                    values = [subset[subset['period'] == p][metric].mean() for p in periods]
                    
                    if len(values) >= 2:
                        # Linear trend (slope)
                        x = np.arange(len(values))
                        slope = np.polyfit(x, values, 1)[0]
                        
                        # Compound annual growth rate
                        if values[0] > 0:
                            cagr = (values[-1] / values[0]) ** (1 / (len(values) - 1)) - 1
                        else:
                            cagr = 0
                        
                        trends.append({
                            'state': state,
                            'area': area,
                            'metric': metric,
                            'start_value': values[0],
                            'end_value': values[-1],
                            'slope': slope,
                            'cagr': cagr,
                            'periods': len(periods)
                        })
        
        return pd.DataFrame(trends)
    
    def calculate_marginal_impacts(
        self,
        dimension_scores: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate marginal impacts for policy targeting.
        
        The marginal impact measures how much EDI would improve
        with a unit improvement in each dimension.
        
        Args:
            dimension_scores: Current dimension scores
            
        Returns:
            Dictionary with marginal impact analysis
        """
        current_edi = self.base_model.calculate_edi({'dimension_scores': dimension_scores})
        
        impacts = {}
        for dim, score in dimension_scores.items():
            # Current marginal: ∂EDI/∂S_d = w_d * EDI / S_d
            if score > 0:
                current_marginal = self.base_model.weights[dim] * (current_edi / score)
            else:
                current_marginal = float('inf')
            
            # Projected EDI with 10% improvement
            improved_scores = dimension_scores.copy()
            improved_scores[dim] = min(1.0, score * 1.1)
            projected_edi = self.base_model.calculate_edi({'dimension_scores': improved_scores})
            
            impacts[dim] = {
                'current_score': score,
                'current_marginal': current_marginal,
                'projected_edi': projected_edi,
                'edi_gain': projected_edi - current_edi,
                'weight': self.base_model.weights[dim]
            }
        
        return {
            'current_edi': current_edi,
            'dimension_impacts': impacts,
            'optimal_target': max(impacts.items(), key=lambda x: x[1]['current_marginal'])[0]
        }
    
    def project_edi(
        self,
        current_dimension_scores: Dict[str, float],
        growth_rates: Dict[str, float],
        years: int = 5
    ) -> List[Dict]:
        """
        Project EDI into the future based on assumed growth rates.
        
        Args:
            current_dimension_scores: Current dimension scores
            growth_rates: Annual growth rate for each dimension
            years: Number of years to project
            
        Returns:
            List of dictionaries with yearly projections
        """
        projections = []
        scores = current_dimension_scores.copy()
        
        for year in range(years + 1):
            # Calculate EDI for current scores
            edi = self.base_model.calculate_edi({'dimension_scores': scores})
            
            projections.append({
                'year': year,
                'EDI': edi,
                **{f'S_{dim}': score for dim, score in scores.items()}
            })
            
            # Apply growth rates for next year
            for dim in scores:
                if dim in growth_rates:
                    scores[dim] = min(1.0, scores[dim] * (1 + growth_rates[dim]))
        
        return projections
    
    def identify_vulnerable_households(
        self,
        household_data: pd.DataFrame,
        edi_threshold: float = 0.4,
        deprivation_threshold: float = 0.3
    ) -> pd.DataFrame:
        """
        Identify households vulnerable to energy dignity decline.
        
        Args:
            household_data: DataFrame with household indicators
            edi_threshold: EDI below which household is considered vulnerable
            deprivation_threshold: Deprivation score above which household is vulnerable
            
        Returns:
            DataFrame of vulnerable households
        """
        vulnerable = []
        
        for idx, row in household_data.iterrows():
            indicators = {col: row[col] for col in household_data.columns 
                        if len(col) == 2 and col[0] in 'AERHPG'}
            
            # Calculate current scores
            dimension_scores = {}
            for dim in ['A', 'E', 'R', 'H', 'P', 'G']:
                dim_indicators = {k: v for k, v in indicators.items() if k.startswith(dim)}
                if dim_indicators:
                    dimension_scores[dim] = self.base_model.calculate_dimension_score(
                        dim, dim_indicators
                    )
            
            edi = self.base_model.calculate_edi({'dimension_scores': dimension_scores})
            deprivation = self.base_model.calculate_deprivation_score(indicators)
            
            # Identify vulnerabilities
            vulnerabilities = []
            for dim, score in dimension_scores.items():
                if score < 0.3:
                    vulnerabilities.append(f'Low {dim}')
                if score == 0:
                    vulnerabilities.append(f'Zero {dim}')
            
            if edi < edi_threshold or deprivation > deprivation_threshold:
                vulnerable.append({
                    'household_id': row.get('household_id', f'HH_{idx}'),
                    'state': row.get('state', 'Unknown'),
                    'area': row.get('area', 'Unknown'),
                    'EDI': edi,
                    'deprivation_score': deprivation,
                    'vulnerabilities': ', '.join(vulnerabilities) if vulnerabilities else 'None',
                    'priority_score': (1 - edi) * 0.5 + deprivation * 0.5
                })
        
        return pd.DataFrame(vulnerable).sort_values('priority_score', ascending=False)
    
    def calculate_policy_impact(
        self,
        baseline_scores: Dict[str, float],
        intervention_dimension: str,
        intervention_magnitude: float
    ) -> Dict:
        """
        Simulate the impact of a policy intervention.
        
        Args:
            baseline_scores: Current dimension scores
            intervention_dimension: Which dimension to target
            intervention_magnitude: Size of improvement (0-1)
            
        Returns:
            Dictionary with intervention impact analysis
        """
        # Baseline EDI
        baseline_edi = self.base_model.calculate_edi({'dimension_scores': baseline_scores})
        
        # Post-intervention scores
        intervention_scores = baseline_scores.copy()
        intervention_scores[intervention_dimension] = min(
            1.0, 
            baseline_scores[intervention_dimension] + intervention_magnitude
        )
        
        # Post-intervention EDI
        intervention_edi = self.base_model.calculate_edi({'dimension_scores': intervention_scores})
        
        # Calculate which households would benefit most
        marginal_impact = self.calculate_marginal_impacts(baseline_scores)
        
        return {
            'baseline_edi': baseline_edi,
            'intervention_edi': intervention_edi,
            'edi_improvement': intervention_edi - baseline_edi,
            'percent_improvement': ((intervention_edi - baseline_edi) / baseline_edi * 100) 
                if baseline_edi > 0 else float('inf'),
            'target_dimension': intervention_dimension,
            'intervention_magnitude': intervention_magnitude,
            'current_marginal': marginal_impact['dimension_impacts'][intervention_dimension]['current_marginal']
        }


def generate_scenario_analysis(
    baseline_scores: Dict[str, float],
    scenarios: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Generate scenario analysis for different policy paths.
    
    Args:
        baseline_scores: Current dimension scores
        scenarios: Dictionary of scenario names to dimension growth rates
        
    Returns:
        DataFrame with scenario comparison
    """
    model = DynamicEDIModel()
    results = []
    
    for scenario_name, growth_rates in scenarios.items():
        projections = model.project_edi(baseline_scores, growth_rates, years=5)
        
        for proj in projections:
            results.append({
                'scenario': scenario_name,
                'year': proj['year'],
                'EDI': proj['EDI'],
                **{f'S_{dim}': proj[f'S_{dim}'] for dim in 'AERHPG'}
            })
    
    return pd.DataFrame(results)
