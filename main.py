"""
Main script to demonstrate the Energy Dignity Index (EDI) model.
"""
from energy_dignity_model import EnergyDignityModel
from sample_data import SAMPLE_HOUSEHOLDS

def main():
    print("=" * 60)
    print("ENERGY DIGNITY INDEX (EDI) MODEL - INDIA")
    print("=" * 60)
    
    # Initialize the model
    model = EnergyDignityModel()
    
    # Process each household
    results = []
    print("\n1. INDIVIDUAL HOUSEHOLD ANALYSIS")
    print("-" * 40)
    
    for household in SAMPLE_HOUSEHOLDS:
        # Calculate dimension scores
        dimension_scores = {}
        for dim in ['A', 'E', 'R', 'H', 'P', 'G']:
            indicators = {k: v for k, v in household['indicators'].items() if k.startswith(dim)}
            dimension_scores[dim] = model.calculate_dimension_score(dim, indicators)
        
        # Calculate EDI
        edi = model.calculate_edi({'dimension_scores': dimension_scores})
        
        # Calculate deprivation score
        c_h = model.calculate_deprivation_score(household['indicators'])
        
        results.append({
            'ID': household['household_id'],
            'State': household['state'],
            'Area': household['area'],
            'EDI': edi,
            'Deprivation': c_h,
            'Dimension_Scores': dimension_scores
        })
        
        print(f"\nHousehold: {household['household_id']} ({household['state']}, {household['area']})")
        print(f"  EDI Score: {edi:.3f}")
        print(f"  Dimension Scores:")
        for dim, score in dimension_scores.items():
            print(f"    {dim}: {score:.3f}")
        print(f"  Deprivation Score (c_h): {c_h:.3f}")
    
    # Regional Analysis
    print("\n\n2. REGIONAL ANALYSIS")
    print("-" * 40)
    
    edi_scores = [r['EDI'] for r in results]
    mean_edi = sum(edi_scores) / len(edi_scores)
    print(f"Mean EDI across all households: {mean_edi:.3f}")
    
    # Urban vs Rural
    urban_edi = [r['EDI'] for r in results if r['Area'] == 'Urban']
    rural_edi = [r['EDI'] for r in results if r['Area'] == 'Rural']
    
    if urban_edi and rural_edi:
        urban_mean = sum(urban_edi) / len(urban_edi)
        rural_mean = sum(rural_edi) / len(rural_edi)
        print(f"Urban Mean EDI: {urban_mean:.3f}")
        print(f"Rural Mean EDI: {rural_mean:.3f}")
        print(f"Urban-Rural Gap: {urban_mean - rural_mean:.3f}")
    
    # Deprivation Analysis (Alkire-Foster Method)
    print("\n\n3. DEPRIVATION ANALYSIS (ALKIRE-FOSTER METHOD)")
    print("-" * 40)
    
    H, I, M0 = model.calculate_m0([h['indicators'] for h in SAMPLE_HOUSEHOLDS], k=0.333)
    print(f"Headcount (H): {H:.3f} ({int(H * len(SAMPLE_HOUSEHOLDS))} of {len(SAMPLE_HOUSEHOLDS)} households)")
    print(f"Intensity (I): {I:.3f}")
    print(f"Adjusted Headcount Ratio (M0): {M0:.3f}")
    
    # Dimensional Contribution to Deficiency
    print("\n\n4. DIMENSIONAL CONTRIBUTION TO DEFICIENCY")
    print("-" * 40)
    
    contributions = model.dimensional_contribution([h['indicators'] for h in SAMPLE_HOUSEHOLDS])
    dim_names = {
        'A': 'Basic Access',
        'E': 'Economic Affordability',
        'R': 'Reliability & Quality',
        'H': 'Health & Environment',
        'P': 'Productive & Developmental',
        'G': 'Agency & Empowerment'
    }
    
    for dim, contrib in sorted(contributions.items(), key=lambda x: x[1], reverse=True):
        print(f"{dim_names[dim]}: {contrib:.1f}%")
    
    # Policy Insights
    print("\n\n5. POLICY INSIGHTS")
    print("-" * 40)
    
    # Find most deprived household
    most_deprived = max(results, key=lambda x: x['Deprivation'])
    print(f"Most deprived household: {most_deprived['ID']} (Deprivation: {most_deprived['Deprivation']:.3f})")
    
    # Find weakest dimension across all households
    avg_dim_scores = {}
    for dim in ['A', 'E', 'R', 'H', 'P', 'G']:
        scores = [r['Dimension_Scores'][dim] for r in results]
        avg_dim_scores[dim] = sum(scores) / len(scores)
    
    weakest_dim = min(avg_dim_scores.items(), key=lambda x: x[1])
    print(f"Weakest dimension overall: {dim_names[weakest_dim[0]]} (Avg Score: {weakest_dim[1]:.3f})")
    
    # Marginal impact analysis
    print("\nMarginal Impact Analysis (Potential EDI gain per unit improvement):")
    sample_dim_scores = results[0]['Dimension_Scores']  # Use first household
    marginal = model.marginal_impact(sample_dim_scores)
    
    for dim, impact in sorted(marginal.items(), key=lambda x: x[1], reverse=True):
        print(f"  {dim_names[dim]}: {impact:.3f}")

if __name__ == "__main__":
    main()
