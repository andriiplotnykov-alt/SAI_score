import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# CONFIG

DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)

tickers = [
    "UBI.PA", "WLN.PA", "NEX.PA", "DIM.PA", "SEB.PA", "VHO.PA", "COFA.PA", "ERI.PA", 
    "SK.PA", "IPN.PA", "BVI.PA", "MFP.PA", "ICADE.PA", "GFC.PA", "TKO.PA", "DEC.PA", 
    "ALD.PA", "BOL.PA", "COV.PA", "ELIS.PA", "ENX.PA", "ERMT.PA", "FNAC.PA", "GET.PA", 
    "MERY.PA", "NEOEN.PA", "ORPEA.PA", "POM.PA", "RMS.PA", "SBT.PA", "SOIT.PA", "SPIE.PA",
    "TEP.PA", "TFI.PA", "VALL.PA", "VIRP.PA", "WNDL.PA", "ATO.PA", "BEN.PA", "ALBIO.PA",
    "BALO.PA", "IDL.PA", "RAM.PA", "ALM.PA", "VRBP.PA", "PUM.DE", "HEI.DE", "BOSS.DE", 
    "EVK.DE", "KGX.DE", "FME.DE", "FRA.DE", "JUN3.DE", "SDF.DE", "WAF.DE", "HNR1.DE", 
    "G1A.DE", "TYL.DE", "MOR.DE", "AFX.DE", "NDX1.DE", "ETL.DE", "AOX.DE", "BNR.DE", 
    "CON.DE", "DEQ.DE", "DHER.DE", "LEG.DE", "OTW.DE", "PSM.DE", "RHM.DE", "SRT.DE", 
    "SY1.DE", "TAG.DE", "VOS.DE", "WCH.DE", "DBAN.DE", "GFT.DE", "SNH.DE", "BVB.DE", 
    "AM3D.DE", "PBB.DE", "HDD.DE", "SMHN.DE", "ADV.DE", "DUE.DE", "GEL.DE", "HBH.DE", 
    "O2D.DE", "PNE3.DE", "JET.L", "IGG.L", "BME.L", "GNS.L", "VCP.L", "MCRO.L", "DRMT.L", 
    "TLW.L", "HAY.L", "ASC.L", "NETW.L", "TRN.L", "WSL.L", "INDV.L", "DLG.L", "GCP.L", 
    "BAB.L", "BYG.L", "CAPC.L", "DLN.L", "DOM.L", "ESNT.L", "FAN.L", "GPE.L", "HWDN.L", 
    "IWG.L", "JDW.L", "KGF.L", "LGEN.L", "MGGT.L", "NXT.L", "OCDO.L", "PHNX.L", "RMV.L", 
    "SGE.L", "TUI.L", "UTG.L", "VRE.L", "WIZZ.L", "SRE.L", "ASHM.L", "HSX.L", "TPW.L", 
    "GRG.L", "SSPG.L", "OXIG.L", "PTEC.L", "RAT.L", "SNR.L", "SPT.L", "TKWY.AS", "ARGX.BR", 
    "SOLB.BR", "ACKB.BR", "BEFB.BR", "POST.AS", "FUGR.AS", "GLPG.AS", "IMCD.AS", "JDEP.AS", 
    "NN.AS", "OCI.AS", "RAND.AS", "VPAK.AS", "WDP.BR", "AALB.AS", "BESI.AS", "CORB.BR", 
    "COFB.BR", "DIET.BR", "ELI.BR", "PROX.BR", "SOB.BR", "BASIC.AS", "FLOW.AS", "SBMO.AS", 
    "VATN.SW", "TEMN.SW", "LOGN.SW", "SIG.SW", "DKSH.SW", "CFR.SW", "GEBN.SW", "LHN.SW", 
    "SANN.SW", "STMN.SW", "BSLN.SW", "HELN.SW", "KNIN.SW", "SCMN.SW", "SOON.SW", "SUN.SW", 
    "ELUXB.ST", "ALFA.ST", "DOM.ST", "EQT.ST", "GETIB.ST", "LIFCOB.ST", "SAGAB.ST", 
    "SINCH.ST", "THULE.ST", "VOLVB.ST", "ORSTED.CO", "PNDORA.CO", "CHR.CO", "DEMANT.CO", 
    "ADE.OL", "NEL.OL", "TOM.OL", "TEL.OL", "PRY.MI", "MONC.MI", "BAMI.MI", "INW.MI", 
    "AMP.MI", "RE.MI", "FER.MC", "GRF.MC", "VIS.MC", "MEL.MC", "CABK.MC", "ANA.MC", 
    "ACS.MC", "BKT.MC", "COL.MC", "IDR.MC", "MAP.MC", "SCYR.MC", "TRE.MC", "AZMT.MI", 
    "BCA.MI", "BZU.MI", "DIA.MI", "FBK.MI", "HER.MI", "IRE.MI", "JUVE.MI", "PIRC.MI", 
    "SAF.MI", "TEN.MI", "AENA.MC", "EBRO.MC", "LOG.MC", "SLR.MC", "UNI.MC"
]

def get_lbo_metrics(symbol):
    try:
        stock = yf.Ticker(symbol)
        
        # 1. Récupération des revenus pour la croissance
        financials = stock.financials
        if 'Total Revenue' not in financials.index:
            return None
        
        rev_series = financials.loc['Total Revenue'].dropna()
        if len(rev_series) < 2:
            avg_growth = 0
        else:
            # Calcul YoY (yfinance donne les dates de la plus récente à la plus ancienne)
            # On trie par date pour calculer la croissance correctement
            rev_series = rev_series.sort_index(ascending=True)
            growth_rates = rev_series.pct_change().dropna()
            avg_growth = growth_rates.mean()

        # 2. Récupération de la D&A (souvent dans le Cash Flow)
        cash_flow = stock.cashflow
        dna = 0
        # Chercher les labels possibles pour D&A dans yfinance
        dna_labels = ['Depreciation And Amortization', 'Depreciation & Amortization', 'Depreciation']
        for label in dna_labels:
            if label in cash_flow.index:
                dna = cash_flow.loc[label].iloc[0] # Valeur la plus récente
                break
        
        return {
            "symbol": symbol,
            "avg_revenue_growth": round(avg_growth, 4),
            "depreciation_amortization": dna
        }
    except Exception as e:
        print(f"Erreur sur {symbol}: {e}")
        return None

# --- BOUCLE DE RÉCUPÉRATION ---
results = []
for t in tickers:
    data = get_lbo_metrics(t)
    if data:
        results.append(data)
        print(f" {t} : Growth={data['avg_revenue_growth']*100:.2f}% | D&A={data['depreciation_amortization']}")

# --- SAUVEGARDE SQL ---
if results:
    df_metrics = pd.DataFrame(results)
    
    # Création de la table
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS LBO_Extra_Metrics (
                symbol VARCHAR(20) PRIMARY KEY,
                avg_revenue_growth DECIMAL(10, 4),
                depreciation_amortization DECIMAL(20, 2)
            );
        """))
    
    # Insertion/Update
    df_metrics.to_sql('temp_extra_metrics', con=engine, if_exists='replace', index=False)
    
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO LBO_Extra_Metrics (symbol, avg_revenue_growth, depreciation_amortization)
            SELECT symbol, avg_revenue_growth, depreciation_amortization FROM temp_extra_metrics
            ON DUPLICATE KEY UPDATE 
                avg_revenue_growth = VALUES(avg_revenue_growth),
                depreciation_amortization = VALUES(depreciation_amortization);
        """))
    print("\n Données injectées avec succès dans 'LBO_Extra_Metrics'")