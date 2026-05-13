"""
EDINET API 連携モジュール

APIキーなし: モックデータ（有価証券報告書の公開情報を基にした参考値）
APIキーあり: EDINET API v2 から実データを取得・XBRL解析

対応企業（モック）: 7203 トヨタ自動車 / 6758 ソニーグループ / 8306 三菱UFJ FG
EDINET API v2 キー取得: https://disclosure2.edinet-fsa.go.jp/
"""

import io
import re
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

EDINET_API_BASE = "https://disclosure2.edinet-fsa.go.jp/api/v2"

# ============================================================
# 会社マスター（証券コード → EDINET コード）
# ============================================================
COMPANY_MASTER: dict[str, dict] = {
    "7203": {"name": "トヨタ自動車",         "edinet_code": "E02144"},
    "6758": {"name": "ソニーグループ",        "edinet_code": "E01777"},
    "8306": {"name": "三菱UFJフィナンシャル・グループ", "edinet_code": "E03606"},
}

# ============================================================
# モックデータ（百万円単位、有価証券報告書の公開情報を基にした参考値）
# 決算期: いずれも3月末   FY = 決算終了年
# ============================================================

# ---- 7203 トヨタ自動車 ----
_TOYOTA_ROWS = [
    {"year": 2020, "sales": 29929992, "operating_profit": 2442869,
     "ordinary_profit": 2442869, "net_income": 2761477,
     "total_assets": 62303024, "equity": 18975063, "liabilities": 43327961,
     "current_assets": 20156000, "current_liabilities": 18600000,
     "cash": 3907000, "accounts_receivable": 2800000,
     "inventory": 2546000, "fixed_assets": 42147024,
     "interest_bearing_debt": 26000000,
     "operating_cash_flow": 3598019, "investing_cash_flow": -2462052,
     "financing_cash_flow": -900000, "employees": 359542},
    {"year": 2021, "sales": 27214594, "operating_profit": 2197748,
     "ordinary_profit": 2197748, "net_income": 2245261,
     "total_assets": 62597488, "equity": 20994977, "liabilities": 41602511,
     "current_assets": 21500000, "current_liabilities": 19200000,
     "cash": 4521000, "accounts_receivable": 2900000,
     "inventory": 2300000, "fixed_assets": 41097488,
     "interest_bearing_debt": 24000000,
     "operating_cash_flow": 2928127, "investing_cash_flow": -1793548,
     "financing_cash_flow": -700000, "employees": 366283},
    {"year": 2022, "sales": 31379507, "operating_profit": 2995697,
     "ordinary_profit": 2995697, "net_income": 2850110,
     "total_assets": 71172591, "equity": 23019003, "liabilities": 48153588,
     "current_assets": 23500000, "current_liabilities": 21000000,
     "cash": 5212000, "accounts_receivable": 3100000,
     "inventory": 2700000, "fixed_assets": 47672591,
     "interest_bearing_debt": 27000000,
     "operating_cash_flow": 4434073, "investing_cash_flow": -3188373,
     "financing_cash_flow": -800000, "employees": 372817},
    {"year": 2023, "sales": 37154298, "operating_profit": 3268185,
     "ordinary_profit": 3268185, "net_income": 2451317,
     "total_assets": 84902414, "equity": 27224093, "liabilities": 57678321,
     "current_assets": 27000000, "current_liabilities": 24000000,
     "cash": 6237000, "accounts_receivable": 3700000,
     "inventory": 3200000, "fixed_assets": 57902414,
     "interest_bearing_debt": 30000000,
     "operating_cash_flow": 4810011, "investing_cash_flow": -3291714,
     "financing_cash_flow": -900000, "employees": 375235},
    {"year": 2024, "sales": 45095325, "operating_profit": 5352934,
     "ordinary_profit": 5352934, "net_income": 4944933,
     "total_assets": 94543736, "equity": 32143619, "liabilities": 62400117,
     "current_assets": 31000000, "current_liabilities": 28000000,
     "cash": 7812000, "accounts_receivable": 4500000,
     "inventory": 3800000, "fixed_assets": 63543736,
     "interest_bearing_debt": 33000000,
     "operating_cash_flow": 8735116, "investing_cash_flow": -5447826,
     "financing_cash_flow": -1200000, "employees": 381467},
]

# ---- 6758 ソニーグループ ----
_SONY_ROWS = [
    {"year": 2020, "sales": 8665698, "operating_profit": 845567,
     "ordinary_profit": 845567, "net_income": 582178,
     "total_assets": 21284581, "equity": 4136637, "liabilities": 17147944,
     "current_assets": 7000000, "current_liabilities": 8000000,
     "cash": 1831000, "accounts_receivable": 1350000,
     "inventory": 720000, "fixed_assets": 14284581,
     "interest_bearing_debt": 2000000,
     "operating_cash_flow": 800000, "investing_cash_flow": -900000,
     "financing_cash_flow": -200000, "employees": 111700},
    {"year": 2021, "sales": 8999360, "operating_profit": 960197,
     "ordinary_profit": 960197, "net_income": 1171532,
     "total_assets": 23178226, "equity": 5242218, "liabilities": 17936008,
     "current_assets": 8000000, "current_liabilities": 8500000,
     "cash": 2200000, "accounts_receivable": 1450000,
     "inventory": 750000, "fixed_assets": 15178226,
     "interest_bearing_debt": 2200000,
     "operating_cash_flow": 1200000, "investing_cash_flow": -800000,
     "financing_cash_flow": -150000, "employees": 109700},
    {"year": 2022, "sales": 9921518, "operating_profit": 1202670,
     "ordinary_profit": 1202670, "net_income": 882177,
     "total_assets": 25375803, "equity": 6042093, "liabilities": 19333710,
     "current_assets": 8500000, "current_liabilities": 9000000,
     "cash": 2470000, "accounts_receivable": 1600000,
     "inventory": 800000, "fixed_assets": 16875803,
     "interest_bearing_debt": 2400000,
     "operating_cash_flow": 900000, "investing_cash_flow": -1000000,
     "financing_cash_flow": -200000, "employees": 108900},
    {"year": 2023, "sales": 11539837, "operating_profit": 1208765,
     "ordinary_profit": 1208765, "net_income": 970555,
     "total_assets": 28602413, "equity": 6813658, "liabilities": 21788755,
     "current_assets": 9500000, "current_liabilities": 10000000,
     "cash": 2810000, "accounts_receivable": 1900000,
     "inventory": 860000, "fixed_assets": 19102413,
     "interest_bearing_debt": 2800000,
     "operating_cash_flow": 1100000, "investing_cash_flow": -1200000,
     "financing_cash_flow": -250000, "employees": 113000},
    {"year": 2024, "sales": 13020991, "operating_profit": 1180294,
     "ordinary_profit": 1180294, "net_income": 970555,
     "total_assets": 31600000, "equity": 7500000, "liabilities": 24100000,
     "current_assets": 10500000, "current_liabilities": 11000000,
     "cash": 3000000, "accounts_receivable": 2100000,
     "inventory": 920000, "fixed_assets": 21100000,
     "interest_bearing_debt": 3100000,
     "operating_cash_flow": 1300000, "investing_cash_flow": -1100000,
     "financing_cash_flow": -300000, "employees": 113000},
]

# ---- 8306 三菱UFJフィナンシャル・グループ（銀行持株会社）----
# 銀行は経常収益を売上高代わりに使用。流動資産・流動負債・在庫は業態上N/A。
_MUFG_ROWS = [
    {"year": 2020, "sales": 5918408, "operating_profit": 941946,
     "ordinary_profit": 941946, "net_income": 528064,
     "total_assets": 295000000, "equity": 15000000, "liabilities": 280000000,
     "current_assets": np.nan, "current_liabilities": np.nan,
     "cash": 95000000, "accounts_receivable": np.nan,
     "inventory": np.nan, "fixed_assets": np.nan,
     "interest_bearing_debt": np.nan,
     "operating_cash_flow": 2000000, "investing_cash_flow": -1500000,
     "financing_cash_flow": -500000, "employees": 162157},
    {"year": 2021, "sales": 5523778, "operating_profit": 1020478,
     "ordinary_profit": 1020478, "net_income": 777283,
     "total_assets": 342000000, "equity": 17500000, "liabilities": 324500000,
     "current_assets": np.nan, "current_liabilities": np.nan,
     "cash": 120000000, "accounts_receivable": np.nan,
     "inventory": np.nan, "fixed_assets": np.nan,
     "interest_bearing_debt": np.nan,
     "operating_cash_flow": 3000000, "investing_cash_flow": -2000000,
     "financing_cash_flow": -300000, "employees": 163082},
    {"year": 2022, "sales": 6009432, "operating_profit": 1261069,
     "ordinary_profit": 1261069, "net_income": 1130328,
     "total_assets": 369000000, "equity": 16500000, "liabilities": 352500000,
     "current_assets": np.nan, "current_liabilities": np.nan,
     "cash": 115000000, "accounts_receivable": np.nan,
     "inventory": np.nan, "fixed_assets": np.nan,
     "interest_bearing_debt": np.nan,
     "operating_cash_flow": 4000000, "investing_cash_flow": -3000000,
     "financing_cash_flow": -200000, "employees": 160486},
    {"year": 2023, "sales": 8183625, "operating_profit": 1820571,
     "ordinary_profit": 1820571, "net_income": 1496034,
     "total_assets": 381000000, "equity": 18000000, "liabilities": 363000000,
     "current_assets": np.nan, "current_liabilities": np.nan,
     "cash": 118000000, "accounts_receivable": np.nan,
     "inventory": np.nan, "fixed_assets": np.nan,
     "interest_bearing_debt": np.nan,
     "operating_cash_flow": 5000000, "investing_cash_flow": -4000000,
     "financing_cash_flow": -400000, "employees": 160486},
    {"year": 2024, "sales": 9188248, "operating_profit": 2178648,
     "ordinary_profit": 2178648, "net_income": 1492805,
     "total_assets": 405000000, "equity": 22000000, "liabilities": 383000000,
     "current_assets": np.nan, "current_liabilities": np.nan,
     "cash": 135000000, "accounts_receivable": np.nan,
     "inventory": np.nan, "fixed_assets": np.nan,
     "interest_bearing_debt": np.nan,
     "operating_cash_flow": 6000000, "investing_cash_flow": -5000000,
     "financing_cash_flow": -500000, "employees": 160000},
]

_MOCK_DATA: dict[str, dict] = {
    "7203": {"name": "トヨタ自動車",                    "rows": _TOYOTA_ROWS},
    "6758": {"name": "ソニーグループ",                   "rows": _SONY_ROWS},
    "8306": {"name": "三菱UFJフィナンシャル・グループ",   "rows": _MUFG_ROWS},
}

# 対応企業の表示用テキスト
SUPPORTED_LABEL = "7203（トヨタ）/ 6758（ソニー）/ 8306（三菱UFJ）"


def get_mock_df(securities_code: str) -> pd.DataFrame:
    """モックデータから DataFrame を返す"""
    entry = _MOCK_DATA.get(securities_code)
    if entry is None:
        raise ValueError(
            f"証券コード {securities_code} は未対応です。\n"
            f"現在対応: {SUPPORTED_LABEL}"
        )
    rows = [{"company": entry["name"], **r} for r in entry["rows"]]
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


# ============================================================
# EDINET API 実装（APIキーが必要）
# ============================================================

_XBRL_ELEMENTS: dict[str, list[str]] = {
    "sales": [
        "NetSales", "Revenue", "NetRevenue", "SalesRevenue",
        "RevenueIFRS", "TotalRevenues",
    ],
    "operating_profit": [
        "OperatingIncome", "ProfitFromOperations",
        "OperatingProfitLoss", "OperatingProfit",
        "ProfitLossFromOperatingActivities",
    ],
    "ordinary_profit": [
        "OrdinaryIncome", "ProfitBeforeTax", "ProfitLossBeforeTax",
    ],
    "net_income": [
        "ProfitLossAttributableToOwnersOfParent",
        "NetIncome", "ProfitLoss", "NetProfit",
        "ProfitAttributableToOwnersOfParent",
    ],
    "total_assets": ["Assets", "TotalAssets"],
    "equity": [
        "NetAssets", "Equity", "TotalEquity",
        "EquityAttributableToOwnersOfParent",
    ],
    "liabilities": ["Liabilities", "TotalLiabilities"],
    "current_assets": ["CurrentAssets"],
    "current_liabilities": ["CurrentLiabilities"],
    "cash": [
        "CashAndCashEquivalents",
        "CashAndCashEquivalentsAtEndOfPeriod",
        "CashAndDeposits",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "CashFlowsFromOperatingActivities",
    ],
    "investing_cash_flow": [
        "NetCashProvidedByUsedInInvestingActivities",
        "CashFlowsFromInvestingActivities",
    ],
    "financing_cash_flow": [
        "NetCashProvidedByUsedInFinancingActivities",
        "CashFlowsFromFinancingActivities",
    ],
    "employees": ["NumberOfEmployees"],
}

_TARGET_CONTEXTS = frozenset({
    "CurrentYearDuration", "CurrentYearInstant",
    "CurrentYear", "CY", "ConsolidatedMember",
})


def _search_annual_docs(edinet_code: str, api_key: str, n_years: int = 5) -> list[dict]:
    """EDINET API で有価証券報告書（docTypeCode=120）を検索"""
    if not _REQUESTS_AVAILABLE:
        raise RuntimeError("requests ライブラリが必要です: pip install requests")

    results = []
    today = date.today()

    for year_offset in range(n_years + 1):
        target_year = today.year - year_offset
        found_this_year = False

        for month in (6, 7, 8, 9, 5, 10):
            for day in (28, 15, 1):
                search_date = date(target_year, month, day)
                if search_date > today:
                    continue

                url = f"{EDINET_API_BASE}/documents.json"
                params = {
                    "date": search_date.strftime("%Y-%m-%d"),
                    "type": 2,
                    "Subscription-Key": api_key,
                }
                try:
                    resp = requests.get(url, params=params, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()
                except Exception:
                    continue

                for doc in data.get("results", []):
                    if (doc.get("edinetCode") == edinet_code and
                            doc.get("docTypeCode") == "120"):
                        results.append(doc)
                        found_this_year = True
                        break

                if found_this_year:
                    break
            if found_this_year:
                break

    return results


def _parse_xbrl_from_zip(zip_bytes: bytes) -> dict:
    """ZIP 内の XBRL ファイルを解析して財務データを抽出（円→百万円変換込み）"""
    financials: dict[str, float] = {}

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            xbrl_files = [
                n for n in zf.namelist()
                if n.lower().endswith(".xbrl") and "PublicDoc" in n
            ]
            if not xbrl_files:
                return financials
            xbrl_data = zf.read(xbrl_files[0])
    except Exception:
        return financials

    try:
        root = ET.fromstring(xbrl_data)
    except ET.ParseError:
        return financials

    for metric, candidates in _XBRL_ELEMENTS.items():
        if metric in financials:
            continue
        for local_name in candidates:
            for elem in root.iter():
                tag_local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag_local != local_name:
                    continue
                ctx = elem.get("contextRef", "")
                if not any(tc in ctx for tc in _TARGET_CONTEXTS):
                    continue
                raw_text = (elem.text or "").strip()
                if not re.match(r"^-?\d+$", raw_text):
                    continue
                raw_val = int(raw_text)
                if abs(raw_val) > 10**9:
                    financials[metric] = raw_val / 1_000_000
                else:
                    financials[metric] = float(raw_val)
                break
            if metric in financials:
                break

    return financials


def fetch_from_edinet(
    securities_code: str, api_key: str, n_years: int = 5
) -> pd.DataFrame:
    """EDINET API から実データを取得して DataFrame を返す"""
    if not _REQUESTS_AVAILABLE:
        raise RuntimeError("requests ライブラリが必要です: pip install requests")

    entry = COMPANY_MASTER.get(securities_code)
    if entry is None:
        raise ValueError(
            f"証券コード {securities_code} はマスターに未登録です。\n"
            f"現在対応: {SUPPORTED_LABEL}"
        )

    company_name = entry["name"]
    edinet_code = entry["edinet_code"]
    docs = _search_annual_docs(edinet_code, api_key, n_years)
    if not docs:
        raise ValueError(
            "EDINET APIで有価証券報告書が見つかりませんでした。"
            "APIキーが正しいか確認してください。"
        )

    rows = []
    for doc in docs:
        doc_id = doc.get("docID", "")
        period_end = doc.get("periodEnd", "")
        year = int(period_end[:4]) if period_end and len(period_end) >= 4 else 0
        if not doc_id or year == 0:
            continue

        url = f"{EDINET_API_BASE}/documents/{doc_id}"
        params = {"type": 5, "Subscription-Key": api_key}
        try:
            resp = requests.get(url, params=params, timeout=60)
            resp.raise_for_status()
        except Exception:
            continue

        financials = _parse_xbrl_from_zip(resp.content)
        if financials:
            rows.append({"company": company_name, "year": year, **financials})

    if not rows:
        raise ValueError(
            "XBRL からデータを抽出できませんでした。"
            "対応フォーマット（J-GAAP / IFRS）か確認してください。"
        )

    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


# ============================================================
# メインエントリーポイント
# ============================================================

def fetch_df(
    securities_code: str,
    api_key: Optional[str] = None,
) -> tuple[pd.DataFrame, bool]:
    """
    証券コードから財務 DataFrame を取得する。

    Args:
        securities_code: 4桁の証券コード（例: "7203"）
        api_key: EDINET API v2 キー（None の場合はモックデータを返す）

    Returns:
        (DataFrame, is_mock)
        is_mock=True の場合は参考値（実EDINET未使用）
    """
    code = securities_code.strip().zfill(4)

    if api_key:
        df = fetch_from_edinet(code, api_key)
        return df, False

    return get_mock_df(code), True


def supported_codes() -> list[str]:
    """モックデータ対応の証券コード一覧"""
    return list(_MOCK_DATA.keys())
