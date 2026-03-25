import pandas as pd
from sqlalchemy import create_engine, text

#CONFIG
DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)


# target_mult: EV/EBITDA d'entrée moyen
# annual_growth: Croissance organique long-terme
# nwc_delta_rev: % du Revenu absorbé par la variation du BFR
# capex_intensity: % du Revenu réinvesti en capital
# ebitda_margin: Marge normative du secteur
SECTOR_BENCHMARKS = {
    "Technology": {
        "target_mult": 15.5, "annual_growth": 0.12, "leverage": 3.0, 
        "nwc_delta_rev": 0.02, "capex_intensity": 0.04, "ebitda_margin": 0.25
    },
    "Healthcare": {
        "target_mult": 13.0, "annual_growth": 0.07, "leverage": 4.0, 
        "nwc_delta_rev": 0.03, "capex_intensity": 0.05, "ebitda_margin": 0.20
    },
    "Communication Services": {
        "target_mult": 9.0, "annual_growth": 0.04, "leverage": 4.5, 
        "nwc_delta_rev": 0.01, "capex_intensity": 0.12, "ebitda_margin": 0.30
    },
    "Consumer Cyclical": {
        "target_mult": 10.5, "annual_growth": 0.05, "leverage": 3.5, 
        "nwc_delta_rev": 0.06, "capex_intensity": 0.03, "ebitda_margin": 0.15
    },
    "Consumer Defensive": {
        "target_mult": 11.0, "annual_growth": 0.03, "leverage": 4.5, 
        "nwc_delta_rev": 0.04, "capex_intensity": 0.025, "ebitda_margin": 0.12
    },
    "Financial Services": {
        "target_mult": 10.0, "annual_growth": 0.04, "leverage": 6.0, 
        "nwc_delta_rev": 0.00, "capex_intensity": 0.01, "ebitda_margin": 0.40
    },
    "Industrials": {
        "target_mult": 9.5, "annual_growth": 0.035, "leverage": 3.5, 
        "nwc_delta_rev": 0.08, "capex_intensity": 0.06, "ebitda_margin": 0.18
    },
    "Energy": {
        "target_mult": 6.0, "annual_growth": 0.02, "leverage": 2.5, 
        "nwc_delta_rev": 0.03, "capex_intensity": 0.15, "ebitda_margin": 0.35
    },
    "Basic Materials": {
        "target_mult": 7.5, "annual_growth": 0.025, "leverage": 3.0, 
        "nwc_delta_rev": 0.10, "capex_intensity": 0.08, "ebitda_margin": 0.22
    },
    "Real Estate": {
        "target_mult": 16.0, "annual_growth": 0.03, "leverage": 8.0, 
        "nwc_delta_rev": 0.01, "capex_intensity": 0.05, "ebitda_margin": 0.60
    },
    "Utilities": {
        "target_mult": 10.0, "annual_growth": 0.02, "leverage": 6.0, 
        "nwc_delta_rev": 0.02, "capex_intensity": 0.20, "ebitda_margin": 0.38
    }
}

def update_ref_tables():
    # 1. Transformation en DataFrame
    df_bench = pd.DataFrame.from_dict(SECTOR_BENCHMARKS, orient='index').reset_index()
    df_bench.columns = ['sector', 'ebitda_multiple', 'annual_growth', 'max_leverage', 
                        'nwc_change_pct_rev', 'capex_pct_rev', 'target_margin']

    # 2. Envoi vers la base de données (Table de référence pure)
    try:
        df_bench.to_sql('ref_sector_analysis', con=engine, if_exists='replace', index=False)
        print(" Table 'ref_sector_analysis' mise à jour avec succès.")

        print("\n--- Aperçu des nouveaux drivers sectoriels ---")
        print(df_bench[['sector', 'ebitda_multiple', 'nwc_change_pct_rev', 'capex_pct_rev']].head())
        
    except Exception as e:
        print(f" Erreur SQL : {e}")

if __name__ == "__main__":
    update_ref_tables()