"""
Sample household data for the Energy Dignity Index (EDI) model.
Based on the worked example in ENERGY_DIGNITY_MODEL.md.
"""

SAMPLE_HOUSEHOLDS = [
    {
        "household_id": "UP-R-001",
        "state": "Uttar Pradesh",
        "area": "Rural",
        # Raw indicators (before normalization)
        "indicators": {
            # Dimension A: Basic Access
            "A1": 1.0,  # Electricity connection: Yes
            "A2": 0.5,  # Clean cooking fuel: LPG + occasional wood
            "A3": 1.0,  # Basic lighting: Adequate
            
            # Dimension E: Economic Affordability
            "E1": 0.47, # Energy expenditure ratio (1 - 0.08/0.15)
            "E2": 0.5,  # LPG refills: 3/year
            "E3": 1.0,  # Bill payment: Never missed
            
            # Dimension R: Reliability & Quality
            "R1": 0.75, # Electricity hours: 18h/24h
            "R2": 1.0,  # Voltage stability: No issues
            "R3": 0.20, # Outages: 8/month (e^(-0.2*8) = 0.20)
            
            # Dimension H: Health & Environment
            "H1": 0.5,  # Cooking location: Separate, no window
            "H2": 0.7,  # Fuel type: LPG (0.9) but mixed use
            "H3": 0.5,  # Indoor air quality: Partial protection
            
            # Dimension P: Productive & Developmental Adequacy
            "P1": 0.5,  # Appliances: 4 of 8
            "P2": 1.0,  # Study lighting: Available
            "P3": 0.5,  # Productive use: Constrained
            
            # Dimension G: Agency & Empowerment
            "G1": 0.5,  # Fuel choice: Constrained by cost
            "G2": 1.0,  # Metering: Fair
            "G3": 0.0,  # Grievance redressal: Does not know
            "G4": 0.0   # Participation: None
        }
    },
    {
        "household_id": "DL-U-001",
        "state": "Delhi",
        "area": "Urban",
        "indicators": {
            "A1": 1.0, "A2": 1.0, "A3": 1.0,
            "E1": 0.8, "E2": 1.0, "E3": 1.0,
            "R1": 0.96, "R2": 1.0, "R3": 0.82,
            "H1": 1.0, "H2": 0.9, "H3": 1.0,
            "P1": 0.875, "P2": 1.0, "P3": 1.0,
            "G1": 1.0, "G2": 1.0, "G3": 1.0, "G4": 0.5
        }
    },
    {
        "household_id": "BR-R-002",
        "state": "Bihar",
        "area": "Rural",
        "indicators": {
            "A1": 1.0, "A2": 0.0, "A3": 0.5,
            "E1": 0.3, "E2": 0.0, "E3": 0.5,
            "R1": 0.54, "R2": 0.5, "R3": 0.14,
            "H1": 0.0, "H2": 0.1, "H3": 0.0,
            "P1": 0.25, "P2": 0.0, "P3": 0.0,
            "G1": 0.0, "G2": 0.0, "G3": 0.0, "G4": 0.0
        }
    },
    {
        "household_id": "MH-U-002",
        "state": "Maharashtra",
        "area": "Urban",
        "indicators": {
            "A1": 1.0, "A2": 1.0, "A3": 1.0,
            "E1": 0.75, "E2": 1.0, "E3": 1.0,
            "R1": 0.92, "R2": 1.0, "R3": 0.67,
            "H1": 1.0, "H2": 0.9, "H3": 1.0,
            "P1": 0.75, "P2": 1.0, "P3": 1.0,
            "G1": 1.0, "G2": 1.0, "G3": 0.5, "G4": 1.0
        }
    },
    {
        "household_id": "WB-R-003",
        "state": "West Bengal",
        "area": "Rural",
        "indicators": {
            "A1": 1.0, "A2": 0.5, "A3": 0.5,
            "E1": 0.55, "E2": 0.5, "E3": 0.5,
            "R1": 0.71, "R2": 0.5, "R3": 0.37,
            "H1": 0.5, "H2": 0.5, "H3": 0.5,
            "P1": 0.5, "P2": 0.5, "P3": 0.5,
            "G1": 0.5, "G2": 0.5, "G3": 0.0, "G4": 0.0
        }
    }
]
