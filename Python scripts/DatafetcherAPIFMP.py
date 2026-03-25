import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
import time
import numpy as np

# --- CONFIGURATION ---
DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)

# MAPPING DES TICKERS (Correction des erreurs 404 courantes)
TICKER_MAPPING = {
    "ORPEA.PA": "EMEIS.PA",
    "LHN.SW": "HOLN.SW",
    "TKWY.AS": "JET.AS",
    "SEB.PA": "SK.PA",
    "MCRO.L": "MCRO.L" # Note: À surveiller si délisté par acquisition
}

indices_tickers = [
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
indices_tickers = list(set(indices_tickers))

def get_advanced_lbo_metrics(ticker):
    # Appliquer le mapping si nécessaire
    target_ticker = TICKER_MAPPING.get(ticker, ticker)
    try:
        stock = yf.Ticker(target_ticker)
        info = stock.info
        
        # Filtre de Taille (500M - 10B pour capter plus de cibles)
        mkt_cap = info.get("marketCap", 0)
        if mkt_cap < 400_000_000:
            return None

        # Récupération des rapports
        is_stmt = stock.income_stmt
        bs_stmt = stock.balance_sheet
        cf_stmt = stock.cashflow

        if is_stmt.empty or bs_stmt.empty:
            return None

        # Extraction des data points
        ebitda = is_stmt.loc["EBITDA"].iloc[0] if "EBITDA" in is_stmt.index else 0
        revenue = is_stmt.loc["Total Revenue"].iloc[0] if "Total Revenue" in is_stmt.index else 1
        debt = bs_stmt.loc["Total Debt"].iloc[0] if "Total Debt" in bs_stmt.index else 0
        cash = bs_stmt.loc["Cash And Cash Equivalents"].iloc[0] if "Cash And Cash Equivalents" in bs_stmt.index else 0
        net_debt = debt - cash
        capex = abs(cf_stmt.loc["Capital Expenditure"].iloc[0]) if "Capital Expenditure" in cf_stmt.index else 0
        
        fcf = cf_stmt.loc["Free Cash Flow"].iloc[0] if "Free Cash Flow" in cf_stmt.index else (ebitda - capex)
        
        data = {
            "symbol": ticker, # Garder le ticker original pour la DB
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "country": info.get("country"),
            "market_cap": mkt_cap,
            "ebitda_margin": round(ebitda / revenue, 4),
            "fcf_yield": round(fcf / mkt_cap, 4) if mkt_cap > 0 else 0,
            "net_debt_ebitda": round(net_debt / ebitda, 2) if ebitda != 0 else 0,
            "capex_intensity": round(capex / revenue, 4),
            "ev_ebitda": round(info.get("enterpriseToEbitda", 0), 2)
        }
        print(f"✅ {ticker} (via {target_ticker}) validé.")
        return data

    except Exception as e:
        print(f"⚠️ Erreur sur {ticker}: {e}")
        return None

# --- EXECUTION ---
results = []
for t in indices_tickers:
    res = get_advanced_lbo_metrics(t)
    if res:
        results.append(res)
    time.sleep(0.7)

if results:
    df_new = pd.DataFrame(results)
    df_new = df_new.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df_new.to_sql('temp_dim_company', con=engine, if_exists='replace', index=False)
    
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO dim_company (symbol, name, sector, country, market_cap, ebitda_margin, fcf_yield, net_debt_ebitda, capex_intensity, ev_ebitda)
            SELECT symbol, name, sector, country, market_cap, ebitda_margin, fcf_yield, net_debt_ebitda, capex_intensity, ev_ebitda 
            FROM temp_dim_company
            ON DUPLICATE KEY UPDATE 
                market_cap = VALUES(market_cap),
                ebitda_margin = VALUES(ebitda_margin),
                fcf_yield = VALUES(fcf_yield),
                net_debt_ebitda = VALUES(net_debt_ebitda),
                ev_ebitda = VALUES(ev_ebitda);
        """))
    print(f"✅ Pipeline terminé. {len(results)} entreprises traitées.")