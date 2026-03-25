import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text 
import numpy as np

#CONFIG
DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)

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

def fetch_fact_financials(ticker):
    try:
        stock = yf.Ticker(ticker)
        is_stmt = stock.income_stmt      
        bs_stmt = stock.balance_sheet    
        cf_stmt = stock.cashflow         

        if is_stmt.empty or bs_stmt.empty:
            return None

        years = is_stmt.columns
        financial_records = []

        for year in years:
            record = {
                "symbol": ticker,
                "Fiscal_Year": year.year,
                "Revenue": is_stmt.loc["Total Revenue", year] if "Total Revenue" in is_stmt.index else 0,
                "EBITDA": is_stmt.loc["EBITDA", year] if "EBITDA" in is_stmt.index else 0,
                "EBIT": is_stmt.loc["EBIT", year] if "EBIT" in is_stmt.index else 0,
                "Net_Income": is_stmt.loc["Net Income", year] if "Net Income" in is_stmt.index else 0,
                "Total_Assets": bs_stmt.loc["Total Assets", year] if "Total Assets" in bs_stmt.index else 0,
                "Total_Debt": bs_stmt.loc["Total Debt", year] if "Total Debt" in bs_stmt.index else 0,
                "Cash": bs_stmt.loc["Cash And Cash Equivalents", year] if "Cash And Cash Equivalents" in bs_stmt.index else 0,
                "Capex": abs(cf_stmt.loc["Capital Expenditure", year]) if "Capital Expenditure" in cf_stmt.index else 0
            }
            financial_records.append(record)
        
        print(f"✅ Données historiques récupérées pour {ticker}")
        return financial_records

    except Exception as e:
        print(f"⚠️ Erreur financière sur {ticker}: {e}")
        return None

all_financials = []

for t in indices_tickers:
    data = fetch_fact_financials(t)
    if data:
        all_financials.extend(data)
    time.sleep(1) 

if all_financials:
    df_fact = pd.DataFrame(all_financials)
    df_fact = df_fact.replace([np.inf, -np.inf], np.nan).fillna(0)

    # 1. Chargement dans une table temporaire
    df_fact.to_sql('temp_fact_financials', con=engine, if_exists='replace', index=False)

    # 2. Insertion finale avec texte SQLAlchemy
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO Fact_Financials (Company_ID, Fiscal_Year, Revenue, EBITDA, EBIT, Net_Income, Total_Assets, Total_Debt, Cash, Capex)
            SELECT 
                c.Company_ID, 
                t.Fiscal_Year, 
                t.Revenue, 
                t.EBITDA, 
                t.EBIT, 
                t.Net_Income, 
                t.Total_Assets, 
                t.Total_Debt, 
                t.Cash, 
                t.Capex
            FROM temp_fact_financials t
            JOIN dim_company c ON t.symbol = c.symbol
            ON DUPLICATE KEY UPDATE 
                Revenue = VALUES(Revenue),
                EBITDA = VALUES(EBITDA),
                Total_Debt = VALUES(Total_Debt),
                Cash = VALUES(Cash);
        """))
    print(f"✅ Table Fact_Financials mise à jour ({len(df_fact)} lignes).")
else:
    print("❌ Aucune donnée financière n'a pu être collectée.")