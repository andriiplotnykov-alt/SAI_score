import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# --- CONFIGURATION ---
DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)

def normalize_score(series, target_min=1, target_max=25, invert=False):
    """Ramène une série sur une échelle de 1 à 25 avec option d'inversion"""
    upper_limit = series.quantile(0.95)
    lower_limit = series.quantile(0.05)
    clipped_series = series.clip(lower=lower_limit, upper=upper_limit)
    
    s_min, s_max = clipped_series.min(), clipped_series.max()
    if s_max == s_min: return series.apply(lambda x: target_min)
    
    normalized = ((clipped_series - s_min) / (s_max - s_min)) * (target_max - target_min) + target_min
    return (target_max + target_min - normalized) if invert else normalized

def run_sai_scorer_v2():
    # Fixed query based on actual database schema
    query = """
    SELECT 
        c.symbol, c.ebitda_margin, c.fcf_yield, c.volatility,
        c.net_debt_ebitda, c.ev_ebitda, c.capex_intensity,
        f.Total_Debt, f.immobilisations, f.stocks,
        COALESCE(d.target_ebitda_margin, c.ebitda_margin) as target_ebitda_margin,
        COALESCE(d.max_leverage, 3.0) as max_leverage
    FROM dim_company c
    LEFT JOIN fact_financials f ON c.symbol = f.symbol AND f.fiscal_year = 2024
    LEFT JOIN ref_sector_benchmarks d ON c.sector = d.sector
    WHERE c.ebitda_margin IS NOT NULL AND c.fcf_yield IS NOT NULL
    """
    
    try:
        df = pd.read_sql(query, con=engine)
    except Exception as e:
        print(f" SQL Error: {e}")
        try:
            fallback_query = """
            SELECT 
                symbol, ebitda_margin, fcf_yield, 
                COALESCE(volatility, 0.25) as volatility,
                net_debt_ebitda, ev_ebitda, capex_intensity
            FROM dim_company 
            WHERE ebitda_margin IS NOT NULL AND fcf_yield IS NOT NULL
            """
            df = pd.read_sql(fallback_query, con=engine)
        except Exception as e2:
            print(f" Fallback query failed: {e2}")
            return

    required_cols = ['symbol', 'ebitda_margin', 'fcf_yield']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f" Missing required columns: {missing_cols}")
        return

    if 'volatility' not in df.columns:
        df['volatility'] = 0.25  # Default volatility
    else:
        df['volatility'] = df['volatility'].fillna(0.25)

    if df.empty:
        print(" No valid data found after filtering.")
        return

    df['raw_serviceability'] = df['fcf_yield'] / (df['volatility'].fillna(0.25) + 0.01)
    df['Score_Serviceability'] = normalize_score(df['raw_serviceability'])

    # Margin improvement potential
    if 'target_ebitda_margin' in df.columns:
        df['margin_gap'] = df['target_ebitda_margin'].fillna(df['ebitda_margin']) - df['ebitda_margin']
    else:
        # Fallback: Use sector average or assume 10% improvement potential
        df['margin_gap'] = df['ebitda_margin'] * 0.10
    df['Score_Optimization'] = normalize_score(df['margin_gap'])


    if 'immobilisations' in df.columns and 'stocks' in df.columns:
        df['collateral_ratio'] = (df['immobilisations'].fillna(0) + df['stocks'].fillna(0)) / (df['Total_Debt'].fillna(1) + 1)
    else:
        df['collateral_ratio'] = 1 / (df['net_debt_ebitda'].fillna(3) + 1)
    df['Score_Collateral'] = normalize_score(df['collateral_ratio'])

    # -SAI score
    df['Final_SAI_Score'] = (
        (df['Score_Serviceability'] * 0.40) + 
        (df['Score_Optimization'] * 0.30) + 
        (df['Score_Collateral'] * 0.30)
    )

    # Sauvegarde dans SQL
    scores_to_db = df[['symbol', 'Score_Serviceability', 'Score_Optimization', 'Score_Collateral', 'Final_SAI_Score']]
    scores_to_db.to_sql('temp_sai_v2', con=engine, if_exists='replace', index=False)
    
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO Calculated_Scores (symbol, LBO_Score, Op_Efficiency_Score, Deep_Value_Score, SAI_Note)
            SELECT symbol, Score_Serviceability, Score_Optimization, Score_Collateral, Final_SAI_Score 
            FROM temp_sai_v2
            ON DUPLICATE KEY UPDATE 
                LBO_Score = VALUES(LBO_Score),
                Op_Efficiency_Score = VALUES(Op_Efficiency_Score),
                Deep_Value_Score = VALUES(Deep_Value_Score),
                SAI_Note = VALUES(SAI_Note);
        """))

    print("\n✅ SAI SCORER 2.0 TERMINÉ")
    print(df.sort_values(by='Final_SAI_Score', ascending=False)[['symbol', 'Final_SAI_Score']].head(10))

if __name__ == "__main__":
    run_sai_scorer_v2()