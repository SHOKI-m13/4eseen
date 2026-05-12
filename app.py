# ============================================================
# 財務分析Webアプリ - app.py  (UI v2 リッチダーク版)
# 就活生・個人投資家・中小企業経営者向け 財務諸表分析ツール
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# ページ設定（必ず最初に呼ぶ）
# ============================================================
st.set_page_config(
    page_title="FinSight | 財務分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# デザインシステム定数
# ============================================================
C_BG        = "#0A0E1A"   # メイン背景
C_CARD      = "#141824"   # カード背景
C_CARD2     = "#1A1F30"   # カード背景（少し明るめ）
C_BORDER    = "rgba(0,212,255,0.18)"   # ボーダー（シアン）
C_ACCENT    = "#00D4FF"   # アクセント（シアン）
C_PURPLE    = "#7B61FF"   # サブアクセント（パープル）
C_SUCCESS   = "#00C896"   # 良い（グリーン）
C_WARNING   = "#FFB347"   # 注意（オレンジ）
C_DANGER    = "#FF4D6D"   # 危険（レッド）
C_TEXT      = "#E8ECF1"   # メインテキスト
C_MUTED     = "#8B92A5"   # サブテキスト

# ============================================================
# カスタムCSS（ダーク高級感デザイン）
# ============================================================
st.markdown(f"""
<style>
/* ---- ベース ---- */
.stApp {{
    background: linear-gradient(160deg, {C_BG} 0%, #0D1220 100%);
}}
section[data-testid="stSidebar"] {{
    background: {C_CARD} !important;
    border-right: 1px solid {C_BORDER};
}}

/* ---- メトリクスカード ---- */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(123,97,255,0.04) 100%);
    border: 1px solid {C_BORDER};
    border-radius: 14px;
    padding: 18px 20px !important;
    transition: box-shadow 0.25s;
}}
[data-testid="metric-container"]:hover {{
    box-shadow: 0 0 22px rgba(0,212,255,0.12);
}}
[data-testid="stMetricLabel"] {{
    color: {C_MUTED} !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase;
}}
[data-testid="stMetricValue"] {{
    color: {C_TEXT} !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}}
[data-testid="stMetricDelta"] svg {{ display: none; }}
[data-testid="stMetricDelta"] {{
    font-size: 0.8rem !important;
    font-weight: 600;
}}

/* ---- タブ ---- */
.stTabs [data-baseweb="tab-list"] {{
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 5px 6px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 9px;
    color: {C_MUTED} !important;
    font-weight: 500;
    padding: 8px 18px;
    font-size: 0.9rem;
    background: transparent !important;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(90deg, {C_ACCENT}, {C_PURPLE}) !important;
    color: #fff !important;
    font-weight: 700 !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ---- ボタン ---- */
.stButton > button {{
    background: linear-gradient(90deg, {C_ACCENT}, {C_PURPLE});
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 24px;
}}

/* ---- Expander ---- */
.streamlit-expanderHeader {{
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: {C_TEXT} !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}}
.streamlit-expanderContent {{
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}}

/* ---- info / warning / error ---- */
.stAlert {{
    border-radius: 10px !important;
    font-size: 0.88rem;
}}

/* ---- Dataframe ---- */
.stDataFrame {{
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    overflow: hidden;
}}

/* ---- カスタムカードクラス ---- */
.fin-card {{
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 12px;
}}
.fin-card-accent {{
    border-left: 4px solid {C_ACCENT};
}}
.fin-section-label {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {C_ACCENT};
    margin-bottom: 6px;
}}
.fin-title {{
    font-size: 1.5rem;
    font-weight: 800;
    color: {C_TEXT};
    letter-spacing: -0.02em;
}}
.fin-subtitle {{
    font-size: 0.88rem;
    color: {C_MUTED};
    margin-top: 2px;
}}
.fin-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 18px 0;
}}

/* ---- 評価バッジ ---- */
.badge-good {{
    display: inline-block;
    background: rgba(0,200,150,0.15);
    color: {C_SUCCESS};
    border: 1px solid rgba(0,200,150,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}
.badge-warning {{
    display: inline-block;
    background: rgba(255,179,71,0.15);
    color: {C_WARNING};
    border: 1px solid rgba(255,179,71,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}
.badge-danger {{
    display: inline-block;
    background: rgba(255,77,109,0.15);
    color: {C_DANGER};
    border: 1px solid rgba(255,77,109,0.3);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}

/* ---- 分析コメントカード ---- */
.comment-card-good {{
    background: rgba(0,200,150,0.05);
    border-left: 4px solid {C_SUCCESS};
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 14px;
}}
.comment-card-warning {{
    background: rgba(255,179,71,0.05);
    border-left: 4px solid {C_WARNING};
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 14px;
}}
.comment-card-danger {{
    background: rgba(255,77,109,0.05);
    border-left: 4px solid {C_DANGER};
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 14px;
}}
.comment-title {{
    font-size: 1rem;
    font-weight: 700;
    color: {C_TEXT};
    margin-bottom: 8px;
}}
.comment-fact {{
    font-size: 0.88rem;
    color: {C_MUTED};
    margin-bottom: 10px;
    line-height: 1.6;
}}
.comment-list-item {{
    font-size: 0.86rem;
    color: {C_MUTED};
    padding: 3px 0;
    line-height: 1.5;
}}

/* ---- シナリオカード ---- */
.scenario-card-good {{
    background: linear-gradient(135deg, rgba(0,200,150,0.08) 0%, rgba(0,200,150,0.03) 100%);
    border: 1px solid rgba(0,200,150,0.25);
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}}
.scenario-card-neutral {{
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,212,255,0.03) 100%);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}}
.scenario-card-bad {{
    background: linear-gradient(135deg, rgba(255,77,109,0.08) 0%, rgba(255,77,109,0.03) 100%);
    border: 1px solid rgba(255,77,109,0.25);
    border-radius: 14px;
    padding: 20px;
    height: 100%;
}}
.scenario-title {{
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 14px;
}}
.scenario-item {{
    font-size: 0.86rem;
    color: {C_MUTED};
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    line-height: 1.55;
}}
.scenario-item:last-child {{ border-bottom: none; }}

/* ---- 指標テーブルの説明文 ---- */
.metric-explain {{
    font-size: 0.75rem;
    color: {C_MUTED};
    margin-top: 2px;
    line-height: 1.4;
}}
.metric-good {{ color: {C_SUCCESS}; font-weight: 600; }}
.metric-warn {{ color: {C_WARNING}; font-weight: 600; }}
.metric-bad  {{ color: {C_DANGER};  font-weight: 600; }}

/* ---- アップロード前の画面 ---- */
.upload-hero {{
    text-align: center;
    padding: 60px 20px;
}}
.upload-hero h1 {{
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, {C_ACCENT}, {C_PURPLE});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
}}
.upload-hero p {{
    font-size: 1.05rem;
    color: {C_MUTED};
    max-width: 540px;
    margin: 0 auto 32px;
    line-height: 1.7;
}}
.feature-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    max-width: 700px;
    margin: 0 auto 36px;
}}
.feature-item {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    text-align: left;
}}
.feature-icon {{ font-size: 1.4rem; margin-bottom: 6px; }}
.feature-label {{ font-size: 0.8rem; color: {C_MUTED}; font-weight: 500; }}

/* ---- 総合スコア表示 ---- */
.score-ring-wrap {{
    text-align: center;
}}
.score-grade {{
    font-size: 3.2rem;
    font-weight: 900;
    letter-spacing: -0.04em;
}}
.score-label {{
    font-size: 0.85rem;
    color: {C_MUTED};
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
.score-bar-wrap {{
    margin: 8px 0;
}}
.score-bar-label {{
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: {C_MUTED};
    margin-bottom: 3px;
}}

/* ---- ヘッダーバナー ---- */
.company-banner {{
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(123,97,255,0.06) 100%);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}}
.company-initial {{
    width: 52px;
    height: 52px;
    background: linear-gradient(135deg, {C_ACCENT}, {C_PURPLE});
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 900;
    color: #fff;
    flex-shrink: 0;
}}
.company-name {{
    font-size: 1.4rem;
    font-weight: 800;
    color: {C_TEXT};
    letter-spacing: -0.02em;
}}
.company-meta {{
    font-size: 0.83rem;
    color: {C_MUTED};
    margin-top: 3px;
}}

/* ---- 指標グループヘッダー ---- */
.indicator-group-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 22px 0 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(0,212,255,0.15);
}}
.indicator-group-icon {{
    width: 30px;
    height: 30px;
    background: linear-gradient(135deg, {C_ACCENT}33, {C_PURPLE}33);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}}
.indicator-group-name {{
    font-size: 0.95rem;
    font-weight: 700;
    color: {C_TEXT};
    letter-spacing: 0.01em;
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 定数定義
# ============================================================
EXPECTED_COLUMNS = [
    "company", "year", "sales", "operating_profit", "ordinary_profit",
    "net_income", "total_assets", "equity", "liabilities",
    "current_assets", "current_liabilities", "cash",
    "accounts_receivable", "inventory", "fixed_assets",
    "interest_bearing_debt", "operating_cash_flow",
    "investing_cash_flow", "financing_cash_flow", "employees"
]

COLUMN_LABELS = {
    "company": "会社名", "year": "年度",
    "sales": "売上高", "operating_profit": "営業利益",
    "ordinary_profit": "経常利益", "net_income": "純利益",
    "total_assets": "総資産", "equity": "自己資本",
    "liabilities": "負債合計", "current_assets": "流動資産",
    "current_liabilities": "流動負債", "cash": "現金・預金",
    "accounts_receivable": "売上債権", "inventory": "棚卸資産",
    "fixed_assets": "固定資産", "interest_bearing_debt": "有利子負債",
    "operating_cash_flow": "営業キャッシュフロー",
    "investing_cash_flow": "投資キャッシュフロー",
    "financing_cash_flow": "財務キャッシュフロー",
    "employees": "従業員数"
}

# 各指標の初心者向け説明文
METRIC_EXPLANATIONS = {
    "sales_growth":       "前年比で売上が何%増えたか。プラスが大きいほど成長中。",
    "op_profit_growth":   "本業の利益が前年比で何%増えたか。売上成長より重要視される場合も。",
    "net_income_growth":  "最終的な純利益の成長率。特別損益の影響を受けるため、営業利益と比較して確認。",
    "total_assets_growth":"会社全体の資産規模の変化。急増は投資拡大または借入増加のサイン。",
    "operating_margin":   "売上100円あたり本業でいくら稼いだか。目安: 製造業5%、IT系10%以上が優良。",
    "net_margin":         "最終的に手元に残る利益の割合。税引き後のため、営業利益率より低くなる。",
    "roa":                "総資産を使ってどれだけ利益を生んだか（資産効率）。目安: 5%以上が良い。",
    "roe":                "株主のお金でどれだけ稼いだか（投資家視点の収益力）。目安: 8%以上が良い。",
    "equity_ratio":       "総資産のうち自己資金の割合。高いほど借金が少なく財務が安定。目安: 30〜40%以上。",
    "debt_ratio":         "自己資本に対する借金の倍率。低いほど安全。100%超は要注意。",
    "current_ratio":      "1年以内に返す必要のある負債を、すぐ換金できる資産でカバーできるか。目安: 150%以上。",
    "ibd_ratio":          "有利子負債（銀行借入等）が総資産に占める割合。低いほど金利リスクが小さい。",
    "asset_turnover":     "総資産1円あたり何円の売上を生んだか（資産効率）。高いほど効率的。",
    "receivable_turnover":"売上債権（売掛金）の回収スピード。低下すると回収遅れのサイン。",
    "inventory_turnover": "在庫が売上に変わるスピード。低下すると在庫の滞留（売れ残り）の可能性。",
    "ocf_margin":         "売上のうち実際に現金として稼いだ割合。利益より正直な稼ぐ力の指標。",
    "free_cash_flow":     "本業で稼いだ現金から投資を引いた残り。プラスなら財務的に自立している証拠。",
    "ocf_vs_net_income":  "純利益より営業CFが小さい場合は「利益の質」に注意。大きい場合は優秀。",
}

# ============================================================
# ユーティリティ関数（ロジック変更なし）
# ============================================================

def safe_divide(numerator, denominator, default=np.nan):
    """0除算を安全に処理する"""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator

def format_number(value, unit="百万円", decimal=1):
    """数値を読みやすい形式にフォーマット（百万円単位 → 億円・兆円に自動変換）
    変換基準（データが百万円単位の場合）:
      1,000百万円 = 10億円   → abs >= 1,000 なら億円表示
      1,000,000百万円 = 1兆円 → abs >= 1,000,000 なら兆円表示
    """
    if pd.isna(value):
        return "N/A"
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{value / 1_000_000:.{decimal}f}兆円"
    if abs_val >= 1_000:
        # 1億円 = 100百万円 なので 100 で割る
        return f"{value / 100:.{decimal}f}億円"
    return f"{value:.{decimal}f}{unit}"

def format_percent(value, decimal=1):
    """パーセント表示"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimal}f}%"

def growth_rate(current, previous):
    """成長率計算（前期比）"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return np.nan
    return (current - previous) / abs(previous) * 100

def check_column(df, col):
    """列が存在し有効なデータがあるか確認"""
    return col in df.columns and df[col].notna().any()

# ============================================================
# データ読み込み・前処理（ロジック変更なし）
# ============================================================

def load_csv(uploaded_file):
    """CSVを読み込み検証・前処理を行う"""
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="shift-jis")
        except Exception as e:
            st.error(f"ファイル読み込み失敗。UTF-8 または Shift-JIS 形式のCSVを使用してください。\nエラー: {e}")
            return None
    except Exception as e:
        st.error(f"CSVの解析に失敗しました。\nエラー: {e}")
        return None

    df.columns = df.columns.str.strip()

    missing_required = [c for c in ["company", "year"] if c not in df.columns]
    if missing_required:
        st.error(f"必須列が見つかりません: {', '.join(missing_required)}")
        return None

    numeric_cols = [c for c in EXPECTED_COLUMNS if c not in ["company", "year"] and c in df.columns]
    for col in numeric_cols:
        original = df[col].copy()
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors="coerce")
        failed = original[df[col].isna() & original.notna() & (original.astype(str).str.strip() != "")]
        if not failed.empty:
            st.warning(f"列 '{col}' に数値変換できないデータが {len(failed)} 件あります。N/A として処理します。")

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        missing_labels = [COLUMN_LABELS.get(c, c) for c in missing_cols]
        st.info(f"以下の列が見つかりませんでした（該当指標は計算不可として表示）: {', '.join(missing_labels)}")
        for col in missing_cols:
            df[col] = np.nan

    df = df.sort_values(["company", "year"]).reset_index(drop=True)
    return df

# ============================================================
# 財務指標計算（ロジック変更なし）
# ============================================================

def calculate_metrics(df_company):
    """1社分データから全財務指標を計算する"""
    metrics_list = []
    for _, row in df_company.iterrows():
        m = {"year": row["year"]}
        for col in EXPECTED_COLUMNS:
            if col != "year":
                m[col] = row.get(col, np.nan)

        prev_rows = df_company[df_company["year"] < row["year"]]
        if not prev_rows.empty:
            prev = prev_rows.iloc[-1]
            m["sales_growth"]        = growth_rate(row.get("sales"), prev.get("sales"))
            m["op_profit_growth"]    = growth_rate(row.get("operating_profit"), prev.get("operating_profit"))
            m["net_income_growth"]   = growth_rate(row.get("net_income"), prev.get("net_income"))
            m["total_assets_growth"] = growth_rate(row.get("total_assets"), prev.get("total_assets"))
        else:
            m["sales_growth"] = m["op_profit_growth"] = m["net_income_growth"] = m["total_assets_growth"] = np.nan

        sales = row.get("sales", np.nan)
        m["operating_margin"] = safe_divide(row.get("operating_profit", np.nan), sales) * 100
        m["net_margin"]       = safe_divide(row.get("net_income", np.nan), sales) * 100
        m["roa"]              = safe_divide(row.get("net_income", np.nan), row.get("total_assets", np.nan)) * 100
        m["roe"]              = safe_divide(row.get("net_income", np.nan), row.get("equity", np.nan)) * 100

        total_assets      = row.get("total_assets", np.nan)
        equity            = row.get("equity", np.nan)
        liabilities       = row.get("liabilities", np.nan)
        current_assets    = row.get("current_assets", np.nan)
        current_liabilities = row.get("current_liabilities", np.nan)
        ibd               = row.get("interest_bearing_debt", np.nan)

        m["equity_ratio"]  = safe_divide(equity, total_assets) * 100
        m["debt_ratio"]    = safe_divide(liabilities, equity) * 100
        m["current_ratio"] = safe_divide(current_assets, current_liabilities) * 100
        m["ibd_ratio"]     = safe_divide(ibd, total_assets) * 100

        m["asset_turnover"]      = safe_divide(sales, total_assets)
        m["receivable_turnover"] = safe_divide(sales, row.get("accounts_receivable", np.nan))
        m["inventory_turnover"]  = safe_divide(sales, row.get("inventory", np.nan))

        ocf = row.get("operating_cash_flow", np.nan)
        icf = row.get("investing_cash_flow", np.nan)
        net_income = row.get("net_income", np.nan)

        m["ocf_margin"]        = safe_divide(ocf, sales) * 100
        m["free_cash_flow"]    = (ocf if not pd.isna(ocf) else np.nan) + (icf if not pd.isna(icf) else np.nan)
        m["ocf_vs_net_income"] = (ocf - net_income) if (not pd.isna(ocf) and not pd.isna(net_income)) else np.nan

        metrics_list.append(m)

    return pd.DataFrame(metrics_list)

# ============================================================
# 分析コメント生成（ロジック変更なし）
# ============================================================

def analyze_profitability(metrics_df):
    """収益性の分析コメントを生成"""
    comments = []
    latest   = metrics_df.iloc[-1]
    has_prev = len(metrics_df) >= 2
    prev     = metrics_df.iloc[-2] if has_prev else None

    om = latest.get("operating_margin")
    if not pd.isna(om):
        om_val  = float(om)
        prev_om = float(prev["operating_margin"]) if prev is not None and not pd.isna(prev.get("operating_margin")) else None

        if prev_om is not None:
            direction = om_val - prev_om
            if direction < -1:
                comments.append({
                    "title": "営業利益率の低下",
                    "fact": f"営業利益率が {format_percent(prev_om)} → {format_percent(om_val)} に低下しています。",
                    "possibilities": [
                        "原材料費・仕入コストの上昇（インフレ・供給不足）",
                        "人件費増加（賃上げ・採用拡大）",
                        "価格転嫁の遅れ（値上げが追いつかない）",
                        "販売管理費の増加（広告費・システム投資等）",
                        "新規事業・新市場への先行投資段階",
                        "一時的な特別コストの発生",
                    ],
                    "check": [
                        "セグメント別の利益率（どの事業が悪化しているか）",
                        "コスト構造の変化（製造原価率、販管費比率）",
                        "競合他社との利益率比較",
                        "販売価格の推移・値上げの実施状況",
                    ],
                    "verdict": "warning", "verdict_text": "注意が必要",
                })
            elif direction > 1:
                comments.append({
                    "title": "営業利益率の改善",
                    "fact": f"営業利益率が {format_percent(prev_om)} → {format_percent(om_val)} に改善しています。",
                    "possibilities": [
                        "コスト削減施策の成果",
                        "価格転嫁の成功・販売価格の上昇",
                        "規模の経済による固定費効率化",
                        "高収益事業への集中（低収益事業の整理）",
                        "生産性向上・DX推進の効果",
                    ],
                    "check": [
                        "改善が一時的か継続的かの確認",
                        "特別要因（一時的利益）が含まれていないか",
                        "競合他社の動向",
                    ],
                    "verdict": "good", "verdict_text": "良い傾向",
                })

        if om_val < 0:
            comments.append({
                "title": "営業損失の発生",
                "fact": f"営業利益率が {format_percent(om_val)} と赤字状態です。",
                "possibilities": [
                    "本業の競争力の低下",
                    "構造的なコスト高（固定費が重い）",
                    "市場縮小・需要不足",
                    "立ち上げ期のスタートアップ的状況",
                    "リストラ・事業転換中の一時的な損失",
                ],
                "check": [
                    "損失の継続期間と回復見通し",
                    "キャッシュバーン（資金消費）のペース",
                    "事業継続に必要な資金の確保状況",
                    "経営者の再建計画の有無",
                ],
                "verdict": "danger", "verdict_text": "要詳細確認",
            })

    if has_prev and not pd.isna(latest.get("sales_growth")) and not pd.isna(om) and prev is not None and not pd.isna(prev.get("operating_margin")):
        sales_g  = float(latest["sales_growth"])
        om_change = float(om) - float(prev["operating_margin"])
        if sales_g > 5 and om_change < -1:
            comments.append({
                "title": "増収だが利益率は低下（質の問題）",
                "fact": f"売上高は {format_percent(sales_g)} 成長しているにもかかわらず、営業利益率は {format_percent(abs(om_change))} 低下しています。",
                "possibilities": [
                    "薄利多売になっている可能性（量を追うが利益が薄い）",
                    "成長投資フェーズで利益より規模拡大を優先している可能性",
                    "競争激化により価格競争に巻き込まれている可能性",
                    "売上に比例してコストも増加する構造（スケールメリットが出ていない）",
                    "新規市場・新製品の立ち上げコストが先行している可能性",
                ],
                "check": [
                    "利益率の低い事業・顧客セグメントがないか",
                    "成長投資の具体的内容と回収見通し",
                    "業界全体の価格動向",
                ],
                "verdict": "warning", "verdict_text": "注意が必要",
            })
    return comments

def analyze_safety(metrics_df):
    """安全性の分析コメントを生成"""
    comments = []
    latest   = metrics_df.iloc[-1]
    eq_ratio = latest.get("equity_ratio")
    current_ratio = latest.get("current_ratio")

    if not pd.isna(eq_ratio):
        eq_val = float(eq_ratio)
        if eq_val < 20:
            comments.append({
                "title": "自己資本比率が低い（財務レバレッジが高い）",
                "fact": f"自己資本比率が {format_percent(eq_val)} と低水準です（目安: 30〜40%以上）。",
                "possibilities": [
                    "積極的な借入による事業拡大戦略（意図的なレバレッジ）",
                    "過去の赤字累積により自己資本が毀損",
                    "業界特性（金融業・不動産業は低くなりやすい）",
                    "株主還元（自社株買い・配当）による自己資本の減少",
                    "のれん等の無形資産が大きい",
                ],
                "check": [
                    "同業他社の自己資本比率との比較",
                    "借入の金利負担と営業利益のカバー率",
                    "資金調達余力（コミットメントライン等）",
                    "格付け機関の評価",
                ],
                "verdict": "warning", "verdict_text": "注意が必要",
            })
        elif eq_val >= 50:
            comments.append({
                "title": "自己資本比率が高い（財務基盤が安定）",
                "fact": f"自己資本比率が {format_percent(eq_val)} と高水準です。",
                "possibilities": [
                    "財務基盤が強固で倒産リスクが低い",
                    "借入を抑制した保守的な財務運営",
                    "ただし過剰に高い場合は資本効率が低い可能性（ROEが低下）",
                    "借入による投資機会を逃している可能性（手元資金過多）",
                ],
                "check": [
                    "ROEの水準（自己資本が多すぎると低下）",
                    "現金・有価証券等の余剰資金の規模",
                    "成長投資・M&A・株主還元の方針",
                ],
                "verdict": "good", "verdict_text": "良い傾向",
            })

    if not pd.isna(current_ratio):
        cr_val = float(current_ratio)
        if cr_val < 100:
            comments.append({
                "title": "流動比率100%割れ（短期支払能力に注意）",
                "fact": f"流動比率が {format_percent(cr_val)} と100%を下回っています。",
                "possibilities": [
                    "資金繰りが逼迫している可能性",
                    "短期借入で長期投資を賄っている（資産・負債のミスマッチ）",
                    "コンビニ・飲食等の現金商売の場合は正常な水準",
                    "グループ内での資金融通がある場合は実質問題なし",
                ],
                "check": [
                    "業種・業態の特性（現金商売かどうか）",
                    "コミットメントライン（緊急時の借入枠）の有無",
                    "手元現金の水準",
                    "支払期限の迫った負債の規模",
                ],
                "verdict": "danger", "verdict_text": "要詳細確認",
            })
    return comments

def analyze_cashflow(metrics_df):
    """キャッシュフローの分析コメントを生成"""
    comments = []
    latest   = metrics_df.iloc[-1]
    ocf      = latest.get("operating_cash_flow")
    fcf      = latest.get("free_cash_flow")
    ocf_vs_ni = latest.get("ocf_vs_net_income")
    net_income = latest.get("net_income")

    if not pd.isna(ocf_vs_ni) and not pd.isna(net_income) and net_income != 0:
        ratio = float(ocf_vs_ni) / abs(float(net_income))
        if ratio < -0.3:
            comments.append({
                "title": "営業CFが純利益を大幅に下回る（利益の質に注意）",
                "fact": f"純利益 {format_number(float(net_income))} に対し、営業CF {format_number(float(ocf))} と大きく乖離しています。",
                "possibilities": [
                    "売掛金の回収が遅れている（売上計上は先行しているが現金が入っていない）",
                    "在庫が急増している（売れていないのに仕入れている）",
                    "利益の質が低い（会計上の利益と現金収入にズレ）",
                    "一時的な運転資本の増加（成長に伴う必要な資金拘束）",
                    "減価償却等の非現金費用が少ない",
                ],
                "check": [
                    "売掛金の回転日数の推移（増えていれば回収遅れ）",
                    "在庫回転日数の推移（増えていれば滞留在庫）",
                    "取引先の財務状況（不良債権化のリスク）",
                    "業界の与信慣行",
                ],
                "verdict": "warning", "verdict_text": "注意が必要",
            })
        elif ratio > 0.3:
            comments.append({
                "title": "営業CFが純利益を上回る（利益の質が高い）",
                "fact": f"営業CF {format_number(float(ocf))} が純利益 {format_number(float(net_income))} を上回り、現金創出力が高い状態です。",
                "possibilities": [
                    "売掛金の回収が順調",
                    "減価償却費等の非現金費用が多い（設備産業に多い）",
                    "在庫・仕入れの適切な管理",
                    "利益の質が高く、実際に現金を稼いでいる",
                ],
                "check": [
                    "減価償却費の水準（大きい場合は設備更新投資が必要か確認）",
                    "FCFの水準と使途",
                ],
                "verdict": "good", "verdict_text": "良い傾向",
            })

    if not pd.isna(fcf):
        fcf_val = float(fcf)
        if fcf_val < 0:
            comments.append({
                "title": "フリーキャッシュフローがマイナス",
                "fact": f"FCFが {format_number(fcf_val)} と赤字です。",
                "possibilities": [
                    "積極的な設備投資・M&Aによる成長投資（意図的なマイナス）",
                    "本業の現金創出力が不足している",
                    "一時的な大型投資（数年に一度の更新投資）",
                    "事業立ち上げフェーズで先行投資中",
                ],
                "check": [
                    "投資CFの内訳（設備投資かM&Aかによって評価が変わる）",
                    "過去数年間のFCFの推移（一時的か継続的か）",
                    "投資の回収見通し（IRRや投資回収期間）",
                ],
                "verdict": "warning", "verdict_text": "注意が必要（内容要確認）",
            })
        elif fcf_val > 0:
            comments.append({
                "title": "フリーキャッシュフローがプラス",
                "fact": f"FCGが {format_number(fcf_val)} とプラスです。本業で投資資金を賄えています。",
                "possibilities": [
                    "財務的に自立した安定経営",
                    "株主還元（配当・自社株買い）の原資がある",
                    "借入返済・財務健全化が進む可能性",
                    "ただしFCFが高すぎる場合は成長投資が不足している懸念も",
                ],
                "check": [
                    "FCFの使途方針（投資・還元・内部留保のバランス）",
                    "業界成長率との比較（投資機会はあるか）",
                ],
                "verdict": "good", "verdict_text": "良い傾向",
            })
    return comments

def analyze_efficiency(metrics_df):
    """効率性の分析コメントを生成"""
    comments = []
    latest   = metrics_df.iloc[-1]
    has_prev = len(metrics_df) >= 2
    prev     = metrics_df.iloc[-2] if has_prev else None
    at       = latest.get("asset_turnover")

    if not pd.isna(at) and prev is not None:
        at_val  = float(at)
        prev_at = float(prev["asset_turnover"]) if not pd.isna(prev.get("asset_turnover")) else None
        if prev_at is not None and at_val < prev_at * 0.9:
            comments.append({
                "title": "総資産回転率の低下（資産効率の悪化）",
                "fact": f"総資産回転率が {prev_at:.2f}回 → {at_val:.2f}回 に低下しています。",
                "possibilities": [
                    "資産が増加したが売上が追いついていない（過剰投資の可能性）",
                    "不稼働資産・遊休資産の増加",
                    "M&A後の統合過渡期（のれん・資産の増加）",
                    "業界サイクルの低迷期（需要減少）",
                ],
                "check": [
                    "どの資産カテゴリが増加しているか（固定資産・流動資産・のれん等）",
                    "新規投資の稼働開始時期",
                    "業界平均との比較",
                ],
                "verdict": "warning", "verdict_text": "注意が必要",
            })
    return comments

def generate_scenario_analysis(metrics_df, company_name):
    """3シナリオを生成"""
    latest   = metrics_df.iloc[-1]
    has_multi = len(metrics_df) >= 2
    om           = latest.get("operating_margin")
    eq_ratio     = latest.get("equity_ratio")
    sales_growth = latest.get("sales_growth") if has_multi else np.nan
    fcf          = latest.get("free_cash_flow")

    om_ok       = not pd.isna(om)       and float(om) > 0
    eq_strong   = not pd.isna(eq_ratio) and float(eq_ratio) > 40
    growing     = not pd.isna(sales_growth) and float(sales_growth) > 5
    fcf_positive = not pd.isna(fcf)     and float(fcf) > 0

    good_pts, std_pts, bad_pts = [], [], []

    if om_ok:
        om_v = float(om)
        good_pts.append(f"営業利益率 {format_percent(om_v)} を維持・改善しながら収益基盤を強化。コスト最適化が進み競合優位性を確立する。")
        std_pts.append(f"営業利益率は現状 {format_percent(om_v)} 付近で推移。大きな改善も悪化もなく現状維持。")
        bad_pts.append(f"競争激化・コスト上昇により営業利益率が {format_percent(om_v)} から低下。収益構造の見直しが必要になる。")
    else:
        good_pts.append("構造改革・事業再編が奏功し、赤字体質から黒字転換を果たす可能性がある。")
        std_pts.append("現在の赤字体質からの脱却が課題。構造改革の成否が分かれ目となる。")
        bad_pts.append("営業損失が継続または拡大し、事業の存続可能性が問われる局面に至る可能性がある。")

    if growing:
        sg_v = float(sales_growth)
        good_pts.append(f"売上成長率 {format_percent(sg_v)} が継続または加速。新規顧客獲得・市場拡大が進む。")
        std_pts.append(f"売上成長は {format_percent(sg_v)} から鈍化し、一桁前半の安定成長へ移行。")
        bad_pts.append(f"市場飽和・競合激化により売上成長が停滞、または減収へ転じるリスク。")
    else:
        good_pts.append("新製品・新市場への進出により成長を取り戻す可能性がある。")
        std_pts.append("売上は横ばい〜微増で推移。現状維持が精一杯の状況。")
        bad_pts.append("売上の低迷が続き、減収が加速するリスクがある。")

    if eq_strong:
        eq_v = float(eq_ratio)
        good_pts.append(f"自己資本比率 {format_percent(eq_v)} の強固な財務基盤を活かし、M&A・大型投資で攻めに転じる。")
        std_pts.append(f"自己資本比率 {format_percent(eq_v)} で財務安定。大きな変動なく安定経営を継続。")
        bad_pts.append(f"現状の財務基盤は安定しているが、想定外リスク（景気後退・大口取引先破綻等）で財務悪化の可能性。")
    else:
        good_pts.append("財務改革・黒字化により自己資本が積み上がり、財務基盤が改善する。")
        std_pts.append("現状の財務水準を維持。大きな改善も悪化もない。")
        bad_pts.append("財務基盤の脆弱さが露呈し資金調達コストが上昇。最悪の場合、資金調達が困難になる。")

    if fcf_positive:
        good_pts.append("潤沢なFCFを活用した積極的な株主還元・M&Aで企業価値を向上。")
        std_pts.append("FCFは安定的に創出し続けるが、使途が株主還元・内部留保にとどまる。")
        bad_pts.append("大型投資や一時費用によりFCFがマイナス転落。財務的な余裕が縮小する。")

    return {"good": good_pts, "standard": std_pts, "bad": bad_pts}

def calculate_overall_score(metrics_df):
    """総合スコアとカテゴリ別評価を計算"""
    latest = metrics_df.iloc[-1]
    scores = {}

    # 収益性（25点）
    om  = latest.get("operating_margin")
    roe = latest.get("roe")
    ps  = 0
    if not pd.isna(om):
        v = float(om)
        ps += 15 if v >= 10 else 10 if v >= 5 else 5 if v >= 0 else -5
    if not pd.isna(roe):
        v = float(roe)
        ps += 10 if v >= 15 else 7 if v >= 8 else 3 if v >= 0 else 0
    scores["収益性"] = min(max(ps, 0), 25)

    # 安全性（25点）
    eq_ratio = latest.get("equity_ratio")
    cr       = latest.get("current_ratio")
    ss       = 0
    if not pd.isna(eq_ratio):
        v = float(eq_ratio)
        ss += 15 if v >= 50 else 10 if v >= 30 else 5 if v >= 20 else 0
    if not pd.isna(cr):
        v = float(cr)
        ss += 10 if v >= 200 else 8 if v >= 150 else 5 if v >= 100 else 2
    scores["安全性"] = min(max(ss, 0), 25)

    # 成長性（25点）
    sg = latest.get("sales_growth")
    pg = latest.get("op_profit_growth")
    gs = 0
    if not pd.isna(sg):
        v = float(sg)
        gs += 13 if v >= 10 else 10 if v >= 5 else 6 if v >= 0 else 0
    if not pd.isna(pg):
        v = float(pg)
        gs += 12 if v >= 10 else 8 if v >= 0 else 0
    scores["成長性"] = min(max(gs, 0), 25)

    # CF力（25点）
    fcf   = latest.get("free_cash_flow")
    ocf_m = latest.get("ocf_margin")
    cs    = 0
    if not pd.isna(fcf):
        cs += 15 if float(fcf) > 0 else 3
    if not pd.isna(ocf_m):
        v = float(ocf_m)
        cs += 10 if v >= 10 else 7 if v >= 5 else 4 if v >= 0 else 0
    scores["CF力"] = min(max(cs, 0), 25)

    total = sum(scores.values())
    if   total >= 80: grade, color, comment = "A",  C_SUCCESS, "財務的に非常に健全な状態です。収益性・安全性・成長性・CF力がバランスよく揃っています。"
    elif total >= 65: grade, color, comment = "B",  C_ACCENT,  "全体的に良好な財務状態です。一部に改善余地はありますが、安定した経営基盤といえます。"
    elif total >= 50: grade, color, comment = "C",  C_WARNING, "平均的な財務状態です。特定の指標に弱点が見られます。詳細分析による原因究明を推奨します。"
    elif total >= 35: grade, color, comment = "D",  C_WARNING, "いくつかの財務指標に懸念があります。業界環境・経営方針と合わせた慎重な判断が必要です。"
    else:             grade, color, comment = "E",  C_DANGER,  "財務的なリスクが複数存在します。詳細な調査と継続的なモニタリングが必要です。"

    return total, grade, color, comment, scores

# ============================================================
# グラフ描画関数（ダークテーマ対応）
# ============================================================

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(color=C_TEXT, size=12),
    margin=dict(l=50, r=20, t=50, b=50),
    height=320,
)
DARK_GRID = dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")

def _apply_dark(fig):
    """Plotly図にダークテーマを適用する共通処理"""
    fig.update_layout(**DARK_LAYOUT)
    fig.update_xaxes(**DARK_GRID)
    fig.update_yaxes(**DARK_GRID)
    return fig

def plot_time_series(metrics_df, col, title, y_label, color=C_ACCENT, is_percent=False):
    """単一指標の時系列グラフ（棒＋線）"""
    if not check_column(metrics_df, col):
        return None
    valid = metrics_df[["year", col]].dropna()
    if valid.empty:
        return None

    fig = go.Figure()
    # 棒グラフ（グラデーション的に透明度をかける）
    fig.add_trace(go.Bar(
        x=valid["year"].astype(str), y=valid[col],
        marker_color=color,
        marker_line=dict(color=color, width=1.5),
        name=title, showlegend=False,
    ))
    # トレンドライン
    fig.add_trace(go.Scatter(
        x=valid["year"].astype(str), y=valid[col],
        mode="lines+markers",
        line=dict(color="#FFFFFF", width=1.5, dash="dot"),
        marker=dict(size=7, color=color, line=dict(color="#fff", width=1.5)),
        showlegend=False,
    ))
    fig.update_layout(title=dict(text=f"{title}（{y_label}）", font=dict(size=13, color=C_MUTED)),
                      yaxis_title="",
                      yaxis_ticksuffix="%" if is_percent else "")
    return _apply_dark(fig)

def plot_cashflow(metrics_df):
    """キャッシュフロー3本柱グラフ"""
    cols_def = [
        ("operating_cash_flow", "営業CF",  C_SUCCESS),
        ("investing_cash_flow", "投資CF",  C_DANGER),
        ("financing_cash_flow", "財務CF",  C_ACCENT),
    ]
    available = [(c, l, col) for c, l, col in cols_def if check_column(metrics_df, c)]
    if not available:
        return None

    valid = metrics_df[["year"] + [c for c, _, _ in available]].dropna(
        subset=[c for c, _, _ in available], how="all"
    )
    if valid.empty:
        return None

    fig = go.Figure()
    for col, label, color in available:
        fig.add_trace(go.Bar(
            name=label, x=valid["year"].astype(str), y=valid[col],
            marker_color=color, marker_line_width=0,
        ))
    fig.update_layout(barmode="group",
                      title=dict(text="キャッシュフロー推移（百万円）", font=dict(size=13, color=C_MUTED)),
                      yaxis_title="",
                      legend=dict(orientation="h", y=-0.2, font=dict(color=C_MUTED)))
    return _apply_dark(fig)

def plot_radar(metrics_df):
    """財務健全性レーダーチャート（最新年度）"""
    latest = metrics_df.iloc[-1]

    def s_om(v):  return min(max((v or 0) / 10 * 100, 0), 100) if not pd.isna(v) else 50
    def s_eq(v):  return min(max((v or 0) / 50 * 100, 0), 100) if not pd.isna(v) else 50
    def s_cr(v):  return min(max((v or 0) / 200 * 100, 0), 100) if not pd.isna(v) else 50
    def s_roe(v): return min(max((v or 0) / 15 * 100, 0), 100) if not pd.isna(v) else 50
    def s_ocf(v): return min(max((v or 0) / 10 * 100, 0), 100) if not pd.isna(v) else 50

    cats   = ["収益性", "安全性", "流動性", "ROE", "CF力"]
    values = [
        s_om(latest.get("operating_margin")),
        s_eq(latest.get("equity_ratio")),
        s_cr(latest.get("current_ratio")),
        s_roe(latest.get("roe")),
        s_ocf(latest.get("ocf_margin")),
    ]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]], theta=cats + [cats[0]],
        fill="toself",
        fillcolor=f"rgba(0,212,255,0.1)",
        line=dict(color=C_ACCENT, width=2),
        marker=dict(size=8, color=C_ACCENT),
    ))
    fig.update_layout(
        title=dict(text="財務健全性レーダー（最新年度）", font=dict(size=13, color=C_MUTED)),
        polar=dict(
            bgcolor="rgba(255,255,255,0.02)",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="rgba(255,255,255,0.08)",
                            tickfont=dict(color=C_MUTED, size=9)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)",
                             tickfont=dict(color=C_MUTED, size=11)),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C_TEXT),
        height=380,
        margin=dict(l=60, r=60, t=60, b=40),
    )
    return fig

def plot_score_gauge(total_score, grade_color):
    """総合スコアのゲージ図（数値テキストはチャート外に分離して重なりを防ぐ）"""
    fig = go.Figure(go.Indicator(
        mode="gauge",           # "number" を外してチャート内の数値表示を消す
        value=total_score,
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": C_MUTED,
                "tickfont": {"color": C_MUTED, "size": 10},
            },
            "bar": {"color": grade_color, "thickness": 0.28},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  35], "color": "rgba(255,77,109,0.12)"},
                {"range": [35, 50], "color": "rgba(255,140,66,0.12)"},
                {"range": [50, 65], "color": "rgba(255,179,71,0.12)"},
                {"range": [65, 80], "color": "rgba(0,212,255,0.12)"},
                {"range": [80,100], "color": "rgba(0,200,150,0.18)"},
            ],
            "threshold": {
                "line": {"color": grade_color, "width": 3},
                "thickness": 0.8,
                "value": total_score,
            },
        },
    ))
    fig.update_layout(
        height=160,                          # ゲージのみなのでコンパクトに
        margin=dict(l=20, r=20, t=10, b=0), # 下余白をゼロにして下のテキストと隙間を詰める
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": C_TEXT},
    )
    return fig

# ============================================================
# UI コンポーネント関数
# ============================================================

def render_company_banner(company_name, metrics_df):
    """会社情報バナー"""
    initial  = company_name[0] if company_name else "?"
    yr_min   = int(metrics_df["year"].min())
    yr_max   = int(metrics_df["year"].max())
    n_years  = len(metrics_df)
    latest   = metrics_df.iloc[-1]
    sales_v  = latest.get("sales", np.nan)
    emp_v    = latest.get("employees", np.nan)
    sales_str = format_number(float(sales_v)) if not pd.isna(sales_v) else "—"
    emp_str   = f"{int(emp_v):,}人" if not pd.isna(emp_v) else "—"

    st.markdown(f"""
    <div class="company-banner">
      <div class="company-initial">{initial}</div>
      <div>
        <div class="company-name">{company_name}</div>
        <div class="company-meta">
          分析期間: {yr_min}〜{yr_max}年度 &nbsp;|&nbsp; {n_years}期分データ
          &nbsp;|&nbsp; 最新売上高: {sales_str}
          &nbsp;|&nbsp; 従業員数: {emp_str}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_row(metrics_df):
    """上段KPIカード（6つ）"""
    latest   = metrics_df.iloc[-1]
    prev     = metrics_df.iloc[-2] if len(metrics_df) >= 2 else None

    # (列名, ラベル, フォーマット種別, delta反転フラグ)
    kpis = [
        ("sales",            "売上高",       "num", False),
        ("operating_margin", "営業利益率",   "pct", False),
        ("roe",              "ROE",          "pct", False),
        ("equity_ratio",     "自己資本比率", "pct", False),
        ("free_cash_flow",   "フリーCF",     "num", False),
        ("current_ratio",    "流動比率",     "pct", False),
    ]

    cols = st.columns(len(kpis))
    for c, (key, label, fmt, inv) in zip(cols, kpis):
        val  = latest.get(key, np.nan)
        pval = prev.get(key, np.nan) if prev is not None else np.nan

        if pd.isna(val):
            disp = "N/A"
        elif fmt == "pct":
            disp = f"{float(val):.1f}%"
        else:
            disp = format_number(float(val))

        if not pd.isna(val) and not pd.isna(pval) and float(pval) != 0:
            delta_raw = float(val) - float(pval)
            delta_str = f"{delta_raw:+.1f}%" if fmt == "pct" else f"{delta_raw / abs(float(pval)) * 100:+.1f}%"
            # Streamlit の delta_color は "normal"(正が緑) / "inverse"(正が赤) / "off"
            dc = "inverse" if inv else "normal"
        else:
            delta_str = None
            dc = "normal"

        with c:
            st.metric(label=label, value=disp, delta=delta_str, delta_color=dc)

def render_metric_table_with_explain(metrics_df):
    """財務指標テーブル（全インラインスタイル版 - CSS クラス不使用で確実に描画）"""
    groups = [
        ("成長性", "📈", [
            ("sales_growth",        "売上高成長率",          "%"),
            ("op_profit_growth",    "営業利益成長率",        "%"),
            ("net_income_growth",   "純利益成長率",          "%"),
            ("total_assets_growth", "総資産成長率",          "%"),
        ]),
        ("収益性", "💰", [
            ("operating_margin", "営業利益率",              "%"),
            ("net_margin",       "純利益率",                "%"),
            ("roa",              "ROA（総資産利益率）",      "%"),
            ("roe",              "ROE（自己資本利益率）",    "%"),
        ]),
        ("安全性", "🛡", [
            ("equity_ratio",  "自己資本比率",               "%"),
            ("debt_ratio",    "負債比率",                   "%"),
            ("current_ratio", "流動比率",                   "%"),
            ("ibd_ratio",     "有利子負債依存度",            "%"),
        ]),
        ("効率性", "⚙️", [
            ("asset_turnover",      "総資産回転率",          "回"),
            ("receivable_turnover", "売上債権回転率",        "回"),
            ("inventory_turnover",  "棚卸資産回転率",        "回"),
        ]),
        ("キャッシュフロー", "💧", [
            ("ocf_margin",        "営業CFマージン",          "%"),
            ("free_cash_flow",    "フリーキャッシュフロー",  "百万円"),
            ("ocf_vs_net_income", "営業CF－純利益",          "百万円"),
        ]),
    ]

    years = metrics_df["year"].tolist()

    # 色定数（CSS変数非依存でインラインに直接埋め込む）
    COL_TEXT    = "#E8ECF1"
    COL_MUTED   = "#8B92A5"
    COL_DANGER  = "#FF4D6D"
    COL_BORDER  = "rgba(255,255,255,0.05)"
    COL_HEAD_BG = "rgba(0,212,255,0.07)"
    COL_HEAD_BD = "rgba(0,212,255,0.15)"
    COL_NA      = "rgba(255,255,255,0.25)"

    # 中立指標（大小で良悪を判断しない）
    NEUTRAL_COLS = {"debt_ratio", "ibd_ratio",
                    "asset_turnover", "receivable_turnover", "inventory_turnover"}

    # インラインスタイル定義（文字列として保持）
    S_WRAP  = "overflow-x:auto;border:1px solid rgba(255,255,255,0.08);border-radius:12px;margin-bottom:20px;"
    S_TABLE = "width:100%;border-collapse:collapse;font-size:0.855rem;"
    S_TH_BASE = ("padding:10px 16px;text-align:left;font-size:0.72rem;font-weight:700;"
                 "letter-spacing:0.07em;text-transform:uppercase;"
                 "border-bottom:1px solid " + COL_HEAD_BD + ";")
    S_TH_NAME    = S_TH_BASE + "white-space:nowrap;min-width:150px;color:" + COL_MUTED + ";"
    S_TH_EXPLAIN = S_TH_BASE + "min-width:340px;color:" + COL_MUTED + ";"
    S_TH_VAL     = S_TH_BASE + "text-align:right;white-space:nowrap;min-width:90px;color:" + COL_MUTED + ";"
    S_TD_BASE    = "padding:10px 16px;vertical-align:top;border-bottom:1px solid " + COL_BORDER + ";"
    S_TD_NAME    = S_TD_BASE + "white-space:nowrap;font-weight:600;color:" + COL_TEXT + ";"
    S_TD_EXPLAIN = S_TD_BASE + ("min-width:340px;max-width:520px;white-space:normal;"
                                "word-break:break-word;line-height:1.6;font-size:0.82rem;color:" + COL_MUTED + ";")
    S_TD_VAL     = S_TD_BASE + ("text-align:right;white-space:nowrap;font-weight:500;"
                                "font-variant-numeric:tabular-nums;color:" + COL_TEXT + ";")
    S_TD_NEG     = S_TD_BASE + ("text-align:right;white-space:nowrap;font-weight:500;"
                                "font-variant-numeric:tabular-nums;color:" + COL_DANGER + ";")
    S_TD_NA      = S_TD_BASE + ("text-align:right;white-space:nowrap;font-size:0.78rem;"
                                "color:" + COL_NA + ";")

    def _fmt_val(col, val, unit):
        """(表示文字列, td インラインスタイル) を返す"""
        if pd.isna(val):
            return "計算不可", S_TD_NA
        fval = float(val)
        if unit == "%":
            text = f"{fval:.1f}%"
        elif unit == "回":
            text = f"{fval:.2f}回"
        else:
            text = format_number(fval)
        td_style = S_TD_VAL if (col in NEUTRAL_COLS or fval >= 0) else S_TD_NEG
        return text, td_style

    for group_name, icon, indicators in groups:
        # グループヘッダー（既存 CSS クラスを使用）
        st.markdown(
            '<div class="indicator-group-header">'
            f'<div class="indicator-group-icon">{icon}</div>'
            f'<div class="indicator-group-name">{group_name}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ---- HTML を文字列連結で組み立てる（f-string ネストを排除）----
        parts = []
        parts.append('<div style="' + S_WRAP + '">')
        parts.append('<table style="' + S_TABLE + '">')

        # thead
        parts.append('<thead><tr style="background:' + COL_HEAD_BG + ';">')
        parts.append('<th style="' + S_TH_NAME    + '">指標</th>')
        parts.append('<th style="' + S_TH_EXPLAIN + '">💡 初心者向け説明</th>')
        for yr in years:
            parts.append('<th style="' + S_TH_VAL + '">' + str(yr) + '年度</th>')
        parts.append('</tr></thead>')

        # tbody
        parts.append('<tbody>')
        last_i = len(indicators) - 1
        for row_i, (col, label, unit) in enumerate(indicators):
            explain = METRIC_EXPLANATIONS.get(col, "")
            # 最終行はボーダーなし
            no_border = "border-bottom:none;"
            td_name    = S_TD_NAME.replace(COL_BORDER, "transparent") if row_i == last_i else S_TD_NAME
            td_explain = S_TD_EXPLAIN.replace(COL_BORDER, "transparent") if row_i == last_i else S_TD_EXPLAIN

            parts.append('<tr>')
            parts.append('<td style="' + td_name    + '">' + label   + '</td>')
            parts.append('<td style="' + td_explain + '">' + explain  + '</td>')
            for yr in years:
                yr_data = metrics_df[metrics_df["year"] == yr]
                if yr_data.empty:
                    td_s = S_TD_NA.replace(COL_BORDER, "transparent") if row_i == last_i else S_TD_NA
                    parts.append('<td style="' + td_s + '">—</td>')
                else:
                    raw = yr_data.iloc[0].get(col, np.nan)
                    text, td_s = _fmt_val(col, raw, unit)
                    if row_i == last_i:
                        td_s = td_s.replace(COL_BORDER, "transparent")
                    parts.append('<td style="' + td_s + '">' + text + '</td>')
            parts.append('</tr>')
        parts.append('</tbody>')

        parts.append('</table></div>')

        # 1回の st.markdown で出力（unsafe_allow_html=True を確実に渡す）
        st.markdown("".join(parts), unsafe_allow_html=True)

def render_analysis_comment_dark(comment):
    """分析コメントをダークカードで表示"""
    verdict     = comment.get("verdict", "warning")
    verdict_text = comment.get("verdict_text", "")
    css_class   = {"good": "comment-card-good", "warning": "comment-card-warning", "danger": "comment-card-danger"}.get(verdict, "comment-card-warning")
    badge_class = {"good": "badge-good", "warning": "badge-warning", "danger": "badge-danger"}.get(verdict, "badge-warning")
    emoji       = {"good": "✅", "warning": "⚠️", "danger": "🔴"}.get(verdict, "ℹ️")

    with st.expander(f"{emoji}  {comment['title']}", expanded=True):
        # 左ボーダー付きカード
        col_body, col_badge = st.columns([6, 1])
        with col_badge:
            st.markdown(f'<div style="text-align:right; padding-top:4px;"><span class="{badge_class}">{verdict_text}</span></div>', unsafe_allow_html=True)

        # 事実
        st.markdown("##### 観察された事実")
        border_color = {"good": C_SUCCESS, "warning": C_WARNING, "danger": C_DANGER}.get(verdict, C_WARNING)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.04); border-left:3px solid {border_color};
                    border-radius:0 8px 8px 0; padding:12px 16px; margin-bottom:14px;
                    font-size:0.9rem; color:{C_TEXT}; line-height:1.6;">
          {comment['fact']}
        </div>
        """, unsafe_allow_html=True)

        col_poss, col_check = st.columns(2)
        with col_poss:
            st.markdown("##### 考えられる可能性")
            for p in comment["possibilities"]:
                st.markdown(f"<div class='comment-list-item'>▸ {p}</div>", unsafe_allow_html=True)

        with col_check:
            st.markdown("##### 追加で確認すべき情報")
            for c in comment["check"]:
                st.markdown(f"<div class='comment-list-item'>📋 {c}</div>", unsafe_allow_html=True)

def render_score_section(metrics_df, key_prefix="score"):
    """総合評価セクション（ゲージ＋カテゴリスコア）"""
    total, grade, color, comment, scores = calculate_overall_score(metrics_df)

    col_gauge, col_detail = st.columns([1, 2])

    with col_gauge:
        # ゲージ（数値なし）
        st.plotly_chart(plot_score_gauge(total, color), use_container_width=True, key=f"{key_prefix}_gauge")
        # スコア数値とグレードをゲージの下に独立表示（重なりゼロ）
        grade_label = {"A": "優秀", "B": "良好", "C": "普通", "D": "注意", "E": "要注意"}.get(grade, "")
        st.markdown(f"""
        <div style="text-align:center; margin-top:-8px; padding-bottom:12px;">
          <div style="font-size:3.4rem; font-weight:900; color:{color}; line-height:1; letter-spacing:-0.04em;">
            {total}
            <span style="font-size:1.2rem; font-weight:400; color:{C_MUTED}; letter-spacing:0;">&nbsp;/ 100</span>
          </div>
          <div style="margin-top:8px;">
            <span style="font-size:1.5rem; font-weight:800; color:{color}; margin-right:8px;">{grade}</span>
            <span style="font-size:0.88rem; color:{C_MUTED}; font-weight:500; letter-spacing:0.06em; text-transform:uppercase;">{grade_label}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_detail:
        st.markdown("#### カテゴリ別スコア")
        cat_colors = {
            "収益性": C_ACCENT, "安全性": C_SUCCESS,
            "成長性": C_PURPLE, "CF力": C_WARNING,
        }
        for cat, score in scores.items():
            cc = cat_colors.get(cat, C_ACCENT)
            pct = score / 25
            bar_html = f"""
            <div class="score-bar-wrap">
              <div class="score-bar-label">
                <span style="color:{C_TEXT}; font-weight:600;">{cat}</span>
                <span style="color:{cc}; font-weight:700;">{score}/25</span>
              </div>
              <div style="background:rgba(255,255,255,0.07); border-radius:99px; height:8px; overflow:hidden;">
                <div style="width:{pct*100:.0f}%; height:100%; background:linear-gradient(90deg,{cc},{cc}aa); border-radius:99px; transition:width 0.5s;"></div>
              </div>
            </div>
            """
            st.markdown(bar_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info(comment)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                border-radius:12px; padding:16px 20px; margin-top:16px; font-size:0.83rem; color:{C_MUTED};">
      <strong style="color:{C_TEXT};">⚠️ ご注意</strong>
      このスコアはCSVデータのみに基づくルールベース評価です。
      業界特性・定性情報（経営陣・技術力・ブランド力）は反映されていません。
      投資判断には必ず有価証券報告書・決算短信の精読をおすすめします。
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# アップロード前のヒーロー画面
# ============================================================

def render_hero_screen():
    """CSVアップロード前のランディング画面"""
    st.markdown("""
    <div class="upload-hero">
      <div class="fin-section-label">Financial Analysis Platform</div>
      <h1>FinSight</h1>
      <p>CSVをアップロードするだけで、財務諸表を多角的に分析。<br>
         数字の裏にある「複数の可能性」を可視化し、想定外を減らします。</p>
      <div class="feature-grid">
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div style="font-size:0.88rem; font-weight:600; color:#E8ECF1; margin-bottom:3px;">15+指標 自動計算</div>
          <div class="feature-label">収益・安全・成長・効率・CF</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🎯</div>
          <div style="font-size:0.88rem; font-weight:600; color:#E8ECF1; margin-bottom:3px;">多角的 分析コメント</div>
          <div class="feature-label">1つの変化に複数の仮説を提示</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔮</div>
          <div style="font-size:0.88rem; font-weight:600; color:#E8ECF1; margin-bottom:3px;">3シナリオ 分析</div>
          <div class="feature-label">良い・標準・悪いシナリオを自動生成</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### CSVフォーマット")
    sample = pd.DataFrame({
        "company": ["サンプル株式会社", "サンプル株式会社"],
        "year":    [2023, 2024],
        "sales":   [50000, 55000],
        "operating_profit": [3000, 3600],
        "net_income":       [2000, 2400],
        "total_assets":     [80000, 85000],
        "equity":           [30000, 33000],
        "... (他列)":       ["", ""],
    })
    st.dataframe(sample, use_container_width=True, hide_index=True)
    st.caption("数値は百万円単位推奨。列が一部なくても動作します（不足列は「計算不可」と表示）。")

# ============================================================
# サイドバー
# ============================================================

def render_sidebar(df=None):
    """サイドバー描画"""
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 8px 0 20px;">
          <div style="font-size:1.5rem; font-weight:900; background:linear-gradient(90deg,{C_ACCENT},{C_PURPLE});
                      -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            📊 FinSight
          </div>
          <div style="font-size:0.75rem; color:{C_MUTED}; margin-top:2px;">財務分析プラットフォーム</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 使い方")
        steps = [
            ("1", "CSVをアップロード",     "必須: company, year 列"),
            ("2", "会社を選択",           "複数社データにも対応"),
            ("3", "概要タブで確認",        "KPI・スコア・レーダー"),
            ("4", "分析コメントを読む",    "複数の可能性を提示"),
            ("5", "シナリオ分析で議論",    "3シナリオで将来を考える"),
        ]
        for num, title, sub in steps:
            st.markdown(f"""
            <div style="display:flex; align-items:flex-start; gap:10px; padding:7px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
              <div style="width:22px; height:22px; background:linear-gradient(135deg,{C_ACCENT},{C_PURPLE});
                          border-radius:6px; display:flex; align-items:center; justify-content:center;
                          font-size:0.7rem; font-weight:800; color:#fff; flex-shrink:0; margin-top:1px;">{num}</div>
              <div>
                <div style="font-size:0.85rem; font-weight:600; color:{C_TEXT};">{title}</div>
                <div style="font-size:0.75rem; color:{C_MUTED};">{sub}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### CSV 列名対応表")
        cols_df = pd.DataFrame([{"列名(英)": k, "意味(日)": v} for k, v in COLUMN_LABELS.items()])
        st.dataframe(cols_df, hide_index=True, use_container_width=True)

        if df is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### データ概要")
            c1, c2 = st.columns(2)
            c1.metric("会社数", df["company"].nunique())
            c2.metric("レコード数", len(df))
            st.caption(f"年度範囲: {df['year'].min()} 〜 {df['year'].max()}")

        st.markdown(f"""
        <div style="position:fixed; bottom:16px; font-size:0.72rem; color:{C_MUTED};">
          FinSight v2.0 | ルールベース分析ツール<br>
          <span style="color:rgba(255,255,255,0.2);">本ツールは参考情報です</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# メインアプリケーション
# ============================================================

def main():
    render_sidebar()

    # --- CSVアップロードエリア ---
    uploaded_file = st.file_uploader(
        "📁  財務諸表CSVをここにドロップ、またはクリックして選択",
        type=["csv"],
        label_visibility="collapsed",
        help="UTF-8 / Shift-JIS 形式対応"
    )

    if uploaded_file is None:
        render_hero_screen()
        st.stop()

    # データ読み込み
    df = load_csv(uploaded_file)
    if df is None:
        st.stop()

    # サイドバーにデータ概要を反映
    render_sidebar(df)

    # --- 会社選択 ---
    companies        = sorted(df["company"].unique().tolist())
    selected_company = st.selectbox("分析する会社を選択", companies, label_visibility="visible")

    df_company = df[df["company"] == selected_company].copy().reset_index(drop=True)
    if df_company.empty:
        st.warning("選択した会社のデータがありません。")
        st.stop()

    metrics_df = calculate_metrics(df_company)

    # 会社情報バナー
    render_company_banner(selected_company, metrics_df)

    # ============================================================
    # タブ構成
    # ============================================================
    tab_overview, tab_metrics, tab_charts, tab_comments, tab_scenario = st.tabs([
        "📌  概要",
        "📋  財務指標",
        "📈  グラフ",
        "🔍  分析コメント",
        "🔮  シナリオ分析",
    ])

    # ----------------------------------------------------------------
    # タブ1: 概要
    # ----------------------------------------------------------------
    with tab_overview:
        st.markdown("#### 主要KPI（最新年度）")
        render_kpi_row(metrics_df)

        st.markdown("<hr class='fin-divider'>", unsafe_allow_html=True)

        col_radar, col_score = st.columns([1, 1])
        with col_radar:
            st.markdown("#### 財務健全性レーダー")
            fig_r = plot_radar(metrics_df)
            if fig_r:
                st.plotly_chart(fig_r, use_container_width=True, key="radar")

        with col_score:
            st.markdown("#### 総合スコア")
            render_score_section(metrics_df, key_prefix="overview")

        # 元データプレビュー
        with st.expander("📂 アップロードデータを確認", expanded=False):
            st.dataframe(df_company.rename(columns=COLUMN_LABELS), use_container_width=True)

    # ----------------------------------------------------------------
    # タブ2: 財務指標
    # ----------------------------------------------------------------
    with tab_metrics:
        st.markdown(
            f"<div style='font-size:0.85rem; color:{C_MUTED}; margin-bottom:16px;'>"
            "各指標の年度別推移と、初心者向け説明を表示します。<br>"
            "「計算不可」はCSVにデータがない列です。"
            "</div>",
            unsafe_allow_html=True
        )
        render_metric_table_with_explain(metrics_df)

    # ----------------------------------------------------------------
    # タブ3: グラフ
    # ----------------------------------------------------------------
    with tab_charts:
        chart_configs = [
            ("sales",              "売上高推移",           "百万円", "#4FC3F7", False),
            ("operating_profit",   "営業利益推移",         "百万円", C_SUCCESS, False),
            ("net_income",         "純利益推移",           "百万円", C_PURPLE,  False),
            ("operating_margin",   "営業利益率推移",       "%",      C_WARNING, True),
            ("roe",                "ROE推移",              "%",      C_DANGER,  True),
            ("equity_ratio",       "自己資本比率推移",     "%",      C_ACCENT,  True),
            ("operating_cash_flow","営業キャッシュフロー推移", "百万円", C_SUCCESS, False),
            ("free_cash_flow",     "フリーCF推移",         "百万円", "#FF8A65", False),
        ]

        pairs = [chart_configs[i:i+2] for i in range(0, len(chart_configs), 2)]
        for pair in pairs:
            c1, c2 = st.columns(2)
            for ui_col, (col_name, title, y_label, color, is_pct) in zip([c1, c2], pair):
                with ui_col:
                    fig = plot_time_series(metrics_df, col_name, title, y_label, color, is_pct)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True, key=f"ts_{col_name}")
                    else:
                        st.markdown(
                            f"<div style='background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.1);"
                            f"border-radius:12px; padding:32px; text-align:center; color:{C_MUTED}; font-size:0.85rem;'>"
                            f"📭 {title}<br>データ不足</div>",
                            unsafe_allow_html=True
                        )

        st.markdown("<hr class='fin-divider'>", unsafe_allow_html=True)
        cf_col, _ = st.columns([2, 1])
        with cf_col:
            fig_cf = plot_cashflow(metrics_df)
            if fig_cf:
                st.plotly_chart(fig_cf, use_container_width=True, key="cashflow")
            else:
                st.warning("キャッシュフローデータが不足しています。")

    # ----------------------------------------------------------------
    # タブ4: 分析コメント
    # ----------------------------------------------------------------
    with tab_comments:
        st.markdown(
            f"<div style='font-size:0.9rem; color:{C_MUTED}; line-height:1.7; margin-bottom:20px;'>"
            "各指標の変化について、<strong style='color:{C_TEXT};'>複数の可能性</strong>を提示します。"
            "「良い・悪い」の二択ではなく、背景にある複数の仮説を持って数字を読みましょう。"
            "</div>",
            unsafe_allow_html=True
        )

        all_comments = (
            analyze_profitability(metrics_df) +
            analyze_safety(metrics_df) +
            analyze_cashflow(metrics_df) +
            analyze_efficiency(metrics_df)
        )

        if all_comments:
            good_c    = [c for c in all_comments if c["verdict"] == "good"]
            warning_c = [c for c in all_comments if c["verdict"] == "warning"]
            danger_c  = [c for c in all_comments if c["verdict"] == "danger"]

            # サマリーバッジ
            st.markdown(
                f"<div style='display:flex; gap:10px; margin-bottom:20px;'>"
                f"<span class='badge-good'>✅ 良好 {len(good_c)}件</span>"
                f"<span class='badge-warning'>⚠️ 注意 {len(warning_c)}件</span>"
                f"<span class='badge-danger'>🔴 要確認 {len(danger_c)}件</span>"
                f"</div>",
                unsafe_allow_html=True
            )

            for comment in all_comments:
                render_analysis_comment_dark(comment)
        else:
            st.info("分析コメントを生成するためには2年分以上のデータが推奨されます。")

    # ----------------------------------------------------------------
    # タブ5: シナリオ分析
    # ----------------------------------------------------------------
    with tab_scenario:
        st.markdown(
            f"<div style='font-size:0.9rem; color:{C_MUTED}; line-height:1.7; margin-bottom:20px;'>"
            "現在の財務データから読み取れる3つのシナリオを提示します。"
            "これは機械的な予測ではなく、<strong style='color:{C_TEXT};'>可能性の整理</strong>です。"
            "</div>",
            unsafe_allow_html=True
        )

        scenarios = generate_scenario_analysis(metrics_df, selected_company)
        col_g, col_m, col_b = st.columns(3)

        with col_g:
            items_html = "".join(
                f"<div class='scenario-item'>✅ {p}</div>" for p in scenarios["good"]
            )
            st.markdown(f"""
            <div class="scenario-card-good">
              <div class="scenario-title" style="color:{C_SUCCESS};">🌟 良いシナリオ</div>
              {items_html}
              <div style="margin-top:12px; font-size:0.75rem; color:rgba(255,255,255,0.3);">数字を前向きに解釈した場合</div>
            </div>
            """, unsafe_allow_html=True)

        with col_m:
            items_html = "".join(
                f"<div class='scenario-item'>➡️ {p}</div>" for p in scenarios["standard"]
            )
            st.markdown(f"""
            <div class="scenario-card-neutral">
              <div class="scenario-title" style="color:{C_ACCENT};">📊 標準シナリオ</div>
              {items_html}
              <div style="margin-top:12px; font-size:0.75rem; color:rgba(255,255,255,0.3);">現状トレンドが継続した場合</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            items_html = "".join(
                f"<div class='scenario-item'>🔴 {p}</div>" for p in scenarios["bad"]
            )
            st.markdown(f"""
            <div class="scenario-card-bad">
              <div class="scenario-title" style="color:{C_DANGER};">⚠️ 悪いシナリオ</div>
              {items_html}
              <div style="margin-top:12px; font-size:0.75rem; color:rgba(255,255,255,0.3);">リスクを重く見た場合</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
                    border-radius:12px; padding:16px 20px; font-size:0.83rem; color:{C_MUTED}; line-height:1.7;">
          <strong style="color:{C_TEXT};">💡 シナリオ分析の使い方</strong><br>
          どのシナリオが現実になるかは、業界環境・経営陣の能力・マクロ経済・競合の動向など
          CSVデータだけでは判断できない要素にかかっています。<br>
          有価証券報告書・決算短信・業界ニュースと組み合わせて検討してください。
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='fin-divider'>", unsafe_allow_html=True)
        st.markdown("#### 総合評価")
        render_score_section(metrics_df, key_prefix="scenario")


if __name__ == "__main__":
    main()
