# Wallet-Risk-Scoring-From-Scratch
Wallet Risk Scoring From Scratch 
# DeFi Wallet Risk Scorer

This Python script fetches wallet addresses from a Google Sheet, queries account data from Expand Network's API, computes risk-related features for each wallet, and generates a risk score on a scale of 0–1000.

## 🔧 Features

- Fetch wallet list from Google Sheets
- Query DeFi metrics (borrowed, repaid, supplied assets, health factor)
- Compute custom features and risk score
- Save scored results to a CSV file

## 📂 Input

Google Sheet (wallets):
- URL: `https://docs.google.com/spreadsheets/d/1ZzaeMgNYnxvriYYpe8PE7uMEblTI0GV5GIVUnsP-sBs`
- Must have a column named `wallet` with Ethereum addresses

## 💾 Output

- `wallet_risk_scores.csv`: CSV file with two columns:
  - `wallet_id`
  - `score` (0–1000)

## ⚙️ Installation

```bash
pip install -r requirements.txt

