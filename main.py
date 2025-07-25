import requests
import pandas as pd
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

API_BASE = "https://api.expand.network"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZzaeMgNYnxvriYYpe8PE7uMEblTI0GV5GIVUnsP-sBs/edit#gid=0"
SHEET_NAME = "Sheet1"
OUTPUT_CSV = "wallet_risk_scores.csv"

def get_wallets_from_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(GOOGLE_SHEET_URL)
        data = sheet.worksheet(SHEET_NAME).get_all_records()
        df = pd.DataFrame(data)
        if 'wallet' not in df.columns:
            raise ValueError("Missing 'wallet' column in Google Sheet.")
        return df
    except Exception as e:
        print(f"Error fetching wallets from Google Sheet: {e}")
        return pd.DataFrame()

def fetch_account_data(wallet):
    try:
        res = requests.get(f"{API_BASE}/lendborrow/getuseraccountdata", params={"address": wallet})
        acct_data = res.json().get("data", {})
        time.sleep(0.2)
        return acct_data
    except Exception as e:
        print(f"Error fetching account data for {wallet}: {e}")
        return {}

def compute_features(wallet, acct):
    try:
        total_borrow = float(acct.get("borrowAmount", 0))
        total_repay = float(acct.get("repayAmount", 0))
        total_supply = float(acct.get("totalCollateralETH", 0))
        health_factor = float(acct.get("healthFactor", 0))
        repay_to_borrow = total_repay / (total_borrow + 1e-6)
        utilization_ratio = total_borrow / (total_supply + 1e-6)
        liquidation_flag = 1 if health_factor < 1.0 else 0
        return {
            "wallet_id": wallet,
            "repay_to_borrow": repay_to_borrow,
            "utilization_ratio": utilization_ratio,
            "health_factor": health_factor,
            "liquidation_flag": liquidation_flag
        }
    except Exception as e:
        print(f"Error computing features for {wallet}: {e}")
        return None

def compute_score(row):
    score = (
        0.5 * row['repay_to_borrow'] +
        0.2 * (1 - row['utilization_ratio']) +
        0.3 * min(row['health_factor'], 2.0) / 2.0 -
        0.3 * row['liquidation_flag']
    )
    return score

def main():
    df_wallets = get_wallets_from_sheet()
    if df_wallets.empty:
        print("No wallets to process.")
        return
    feature_list = []
    for wallet in df_wallets['wallet']:
        acct = fetch_account_data(wallet)
        features = compute_features(wallet, acct)
        if features:
            feature_list.append(features)
    df_feat = pd.DataFrame(feature_list)
    df_feat['raw_score'] = df_feat.apply(compute_score, axis=1)
    min_score = df_feat['raw_score'].min()
    max_score = df_feat['raw_score'].max()
    df_feat['score'] = ((df_feat['raw_score'] - min_score) / (max_score - min_score + 1e-6) * 1000).astype(int)
    df_feat[['wallet_id', 'score']].to_csv(OUTPUT_CSV, index=False)
    print(f"[✓] Wallet risk scores written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
