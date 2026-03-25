import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import time
import numpy as np

# CONFIG
DB_URL = "mysql+pymysql://root:admin@localhost:3306/lbo_db"
engine = create_engine(DB_URL)
#AI can be used to compose the list of desired tickers for analysis
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

def fetch_market_data(ticker):
    """
    Extrait les données de marché : Date, Share_Price, Shares_Outstanding
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Récupération de l'historique des prix (Derniers 30 jours pour avoir la donnée la plus récente)
        hist = stock.history(period="30d")
        if hist.empty:
            return None

        # Récupération du nombre d'actions en circulation
        # info.get() est plus sûr pour éviter les erreurs si la clé manque
        shares_outstanding = stock.info.get("sharesOutstanding", 0)
        
        # On prend la dernière ligne (donnée la plus récente)
        last_row = hist.iloc[-1]
        
        data = {
            "symbol": ticker,
            "Date": last_row.name.date(),
            "Share_Price": round(last_row["Close"], 4),
            "Shares_Outstanding": shares_outstanding
        }
        
        print(f"✅ Données de marché récupérées pour {ticker}")
        return data

    except Exception as e:
        print(f"⚠️ Erreur marché sur {ticker}: {e}")
        return None

# --- EXECUTION DU PIPELINE ---
market_results = []

for t in indices_tickers:
    res = fetch_market_data(t)
    if res:
        market_results.append(res)
    time.sleep(0.5) # Délai pour respecter les limites de l'API yfinance
if market_results:
    df_market = pd.DataFrame(market_results)
    df_market.to_sql('temp_fact_market', con=engine, if_exists='replace', index=False)

    with engine.begin() as conn:
        # Utilisez text() autour de votre triple quote
        conn.execute(text("""
            INSERT INTO Fact_Market_Data (Company_ID, Date, Share_Price, Shares_Outstanding)
            SELECT 
                c.Company_ID, 
                t.Date, 
                t.Share_Price, 
                t.Shares_Outstanding
            FROM temp_fact_market t
            JOIN dim_company c ON t.symbol = c.symbol
            ON DUPLICATE KEY UPDATE 
                Share_Price = VALUES(Share_Price),
                Shares_Outstanding = VALUES(Shares_Outstanding),
                Date = VALUES(Date);
        """))
    print(f"🚀 Succès : {len(df_market)} lignes insérées.")