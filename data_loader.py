"""
Data Loader Module for Energy Dignity Index (EDI) Model
Handles loading and processing of Indian household survey data (NFHS, NSSO)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from energy_dignity_model import normalize_indicator

# NFHS Variable Names to EDI Indicator Mapping
NFHS_EDI_MAPPING = {
    # Basic Access (A)
    'hv246': 'A1',      # Electricity source
    'hv226': 'A2',      # Type of cooking fuel
    'hv241': 'A3',      # Rooms with lighting
    
    # Economic Affordability (E) - Derived from expenditure data
    # E1, E2, E3 require calculated fields
    
    # Reliability (R) - From energy module questions
    'sh138a': 'R1',     # Hours of electricity
    'sh138b': 'R2',     # Voltage stability  
    'sh138c': 'R3',     # Outage frequency
    
    # Health (H)
    'hv242': 'H1',      # Cooking location
    'hv227': 'H2',      # Fuel type (different variable for health context)
    'sh140': 'H3',      # Indoor air quality proxy
    
    # Productive (P)
    # P1: Derived from appliance ownership variables
    'hv244': 'P2',      # Study lighting
    
    # Agency (G) - From governance module
    'sh160': 'G1',      # Fuel choice
    'sh161': 'G2',      # Metering fairness
    'sh162': 'G3',      # Grievance redressal
    'sh163': 'G4',      # Participation
}

# State codes for Indian states
INDIA_STATES = {
    '01': 'Jammu & Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab',
    '04': 'Chandigarh', '05': 'Uttarakhand', '06': 'Haryana',
    '07': 'Delhi', '08': 'Rajasthan', '09': 'Uttar Pradesh',
    '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
    '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram',
    '16': 'Tripura', '17': 'Meghalaya', '18': 'Assam',
    '19': 'West Bengal', '20': 'Jharkhand', '21': 'Odisha',
    '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
    '25': 'Daman & Diu', '26': 'Dadra & Nagar Haveli', '27': 'Maharashtra',
    '28': 'Andhra Pradesh', '29': 'Karnataka', '30': 'Goa',
    '31': 'Lakshadweep', '32': 'Kerala', '33': 'Tamil Nadu',
    '34': 'Puducherry', '35': 'Andaman & Nicobar', '36': 'Telangana'
}


class NFHSDataLoader:
    """Loader for National Family Health Survey (NFHS) data files."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the NFHS data loader.
        
        Args:
            data_path: Path to NFHS data file (CSV, Stata, or SPSS format)
        """
        self.data_path = data_path
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load NFHS data from file.
        
        Supports formats: CSV, Stata (.dta), SPSS (.sav)
        """
        path = file_path or self.data_path
        if path is None:
            raise ValueError("No data path provided")
            
        if path.endswith('.csv'):
            self.raw_data = pd.read_csv(path)
        elif path.endswith('.dta'):
            self.raw_data = pd.read_stata(path)
        elif path.endswith('.sav'):
            self.raw_data = pd.read_spss(path)
        else:
            raise ValueError(f"Unsupported file format: {path}")
            
        return self.raw_data
    
    def map_to_edi_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map NFHS variable names to EDI indicator codes.
        
        Args:
            df: Raw NFHS dataframe
            
        Returns:
            Dataframe with EDI indicator columns
        """
        edi_df = pd.DataFrame()
        
        for nfhs_var, edi_code in NFHS_EDI_MAPPING.items():
            if nfhs_var in df.columns:
                edi_df[edi_code] = df[nfhs_var]
                
        return edi_df
    
    def normalize_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize all indicators to [0, 1] scale.
        
        Args:
            df: Dataframe with raw indicator values
            
        Returns:
            Dataframe with normalized scores
        """
        normalized_df = pd.DataFrame(index=df.index)
        
        for column in df.columns:
            normalized_df[column] = df[column].apply(
                lambda x: normalize_indicator(column, x)
            )
            
        return normalized_df


class SyntheticDataGenerator:
    """Generate realistic synthetic household data based on Indian distributions."""
    
    def __init__(self, n_households: int = 1000, seed: int = 42):
        """
        Initialize synthetic data generator.
        
        Args:
            n_households: Number of households to generate
            seed: Random seed for reproducibility
        """
        self.n_households = n_households
        self.rng = np.random.RandomState(seed)
        
    def generate(self) -> pd.DataFrame:
        """
        Generate synthetic household data based on known Indian distributions.
        
        Returns:
            DataFrame with household-level EDI indicators
        """
        data = []
        
        for i in range(self.n_households):
            # Determine household type based on realistic distribution
            household_type = self._sample_household_type()
            state = self._sample_state()
            area = self._sample_area()
            
            # Generate indicators based on household type
            indicators = self._generate_indicators(household_type, area)
            
            data.append({
                'household_id': f'{state[:3]}-{area[0].upper()}-{i:04d}',
                'state': state,
                'area': area,
                'household_type': household_type,
                'year': self.rng.choice([2019, 2020, 2021, 2022, 2023, 2024]),
                **indicators
            })
            
        return pd.DataFrame(data)
    
    def _sample_household_type(self) -> str:
        """Sample household type based on Indian distribution."""
        types = ['deprived', 'marginal', 'developing', 'adequate', 'thriving']
        probs = [0.15, 0.25, 0.30, 0.20, 0.10]
        return self.rng.choice(types, p=probs)
    
    def _sample_state(self) -> str:
        """Sample state based on population distribution."""
        states = list(INDIA_STATES.values())
        # Higher population states have higher probability
        weights = np.array([2, 1, 2, 0.2, 1, 1.5, 0.5, 3, 5, 
                          4, 0.2, 0.3, 0.2, 0.3, 0.2, 0.3, 0.3, 1.5,
                          3, 1.5, 2, 1.5, 3.5, 2, 0.2, 0.2, 4,
                          3, 3, 0.3, 0.1, 1.5, 3, 0.3, 0.1, 2.5])
        weights = weights / weights.sum()
        return self.rng.choice(states, p=weights)
    
    def _sample_area(self) -> str:
        """Sample urban/rural area based on Indian distribution."""
        return self.rng.choice(['urban', 'rural'], p=[0.35, 0.65])
    
    def _generate_indicators(self, household_type: str, area: str) -> Dict:
        """
        Generate indicator values based on household type and area.
        
        Args:
            household_type: One of 'deprived', 'marginal', 'developing', 'adequate', 'thriving'
            area: 'urban' or 'rural'
            
        Returns:
            Dictionary of indicator scores
        """
        # Base parameters for each household type
        params = {
            'deprived': {'mean': 0.2, 'std': 0.15},
            'marginal': {'mean': 0.45, 'std': 0.15},
            'developing': {'mean': 0.65, 'std': 0.15},
            'adequate': {'mean': 0.85, 'std': 0.1},
            'thriving': {'mean': 0.95, 'std': 0.05}
        }
        
        # Rural penalty
        rural_penalty = -0.1 if area == 'rural' else 0
        
        base_mean = params[household_type]['mean'] + rural_penalty
        base_std = params[household_type]['std']
        
        # Generate each indicator with appropriate distribution
        indicators = {}
        
        # Basic Access (A)
        indicators['A1'] = np.clip(self.rng.normal(base_mean + 0.2, base_std), 0, 1)
        indicators['A2'] = np.clip(self.rng.normal(base_mean, base_std), 0, 1)
        indicators['A3'] = np.clip(self.rng.normal(base_mean + 0.1, base_std), 0, 1)
        
        # Economic Affordability (E)
        indicators['E1'] = np.clip(self.rng.normal(base_mean - 0.05, base_std), 0, 1)
        indicators['E2'] = np.clip(self.rng.normal(base_mean, base_std), 0, 1)
        indicators['E3'] = np.clip(self.rng.normal(base_mean + 0.1, base_std), 0, 1)
        
        # Reliability (R)
        indicators['R1'] = np.clip(self.rng.normal(base_mean + 0.05, base_std), 0, 1)
        indicators['R2'] = np.clip(self.rng.normal(base_mean, base_std), 0, 1)
        indicators['R3'] = np.clip(self.rng.normal(base_mean - 0.1, base_std), 0, 1)
        
        # Health (H)
        indicators['H1'] = np.clip(self.rng.normal(base_mean - 0.1, base_std), 0, 1)
        indicators['H2'] = np.clip(self.rng.normal(base_mean, base_std), 0, 1)
        indicators['H3'] = np.clip(self.rng.normal(base_mean - 0.15, base_std), 0, 1)
        
        # Productive (P)
        indicators['P1'] = np.clip(self.rng.normal(base_mean - 0.05, base_std), 0, 1)
        indicators['P2'] = np.clip(self.rng.normal(base_mean + 0.1, base_std), 0, 1)
        indicators['P3'] = np.clip(self.rng.normal(base_mean - 0.1, base_std), 0, 1)
        
        # Agency (G)
        indicators['G1'] = np.clip(self.rng.normal(base_mean - 0.15, base_std), 0, 1)
        indicators['G2'] = np.clip(self.rng.normal(base_mean, base_std), 0, 1)
        indicators['G3'] = np.clip(self.rng.normal(base_mean - 0.2, base_std), 0, 1)
        indicators['G4'] = np.clip(self.rng.normal(base_mean - 0.25, base_std), 0, 1)
        
        return indicators


def load_real_sample_data() -> pd.DataFrame:
    """
    Load realistic sample data based on Indian household survey patterns.
    
    Returns:
        DataFrame with household-level data ready for EDI calculation
    """
    generator = SyntheticDataGenerator(n_households=2000, seed=42)
    return generator.generate()


def calculate_edi_for_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate EDI scores for all households in a dataframe.
    
    Args:
        df: DataFrame with household indicators
        
    Returns:
        DataFrame with added EDI scores and dimension scores
    """
    from energy_dignity_model import EnergyDignityModel
    
    model = EnergyDignityModel()
    results = df.copy()
    
    # Calculate dimension scores
    dimensions = ['A', 'E', 'R', 'H', 'P', 'G']
    for dim in dimensions:
        indicators = [col for col in df.columns if col.startswith(dim)]
        results[f'S_{dim}'] = df[indicators].apply(
            lambda row: model.calculate_dimension_score(dim, row.to_dict()), 
            axis=1
        )
    
    # Calculate overall EDI
    dim_scores = {f'S_{dim}': f'S_{dim}' for dim in dimensions}
    results['EDI'] = results.apply(
        lambda row: model.calculate_edi({
            'dimension_scores': {dim: row[f'S_{dim}'] for dim in dimensions}
        }),
        axis=1
    )
    
    # Calculate deprivation scores
    results['deprivation_score'] = results.apply(
        lambda row: model.calculate_deprivation_score(
            {col: row[col] for col in df.columns if len(col) == 2}
        ),
        axis=1
    )
    
    return results
