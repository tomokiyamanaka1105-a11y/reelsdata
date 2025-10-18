# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ==============================
# タイトル
# ==============================
st.set_page_config(page_title="AI仕入れ分析ツール", layout="wide")
st.title("📊 AI仕入れ分析ツール（無料版）")
st.caption("CSVをアップロードして、販売傾向・仕入れ適正価格・予想利益を自動分析")

# ==============================
# ファイルアップロード
# ==============================
uploaded_file = st.file_uploader("👇 オークファン形式のCSVファイルをアップロード", type="csv")

if uploaded_file is not None:
    try:
        # ==============================
        # CSV読込
        # ==============================
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSVファイルを読み込みました！")
        st.write("データプレビュー（先頭5行）:")
        st.dataframe(df.head())

        # ==============================
        # データ整形
        # ==============================
        df["年式"] = df["メーカー名"].str.extract(r"(20\d{2}|不明)")
        df["モデル"] = df["メーカー名"].str.extract(r"(アルデバラン\sBFS\s\w+|ヴァンキッシュ\s\w+|メタニウム\s\w+)")
        df["メーカー"] = df["メーカー名"].str.extract(r"(SHIMANO|DAIWA|ABU|その他)")

        # 欠損値対策
        df["年式"] = df["年式"].fillna("不明")
        df["モデル"] = df["モデル"].fillna("不明")

        # ==============================
        # 分析集計
        # ==============================
        result = (
            df.groupby(["メーカー", "モデル", "年式"])
            .agg(
                平均落札=("落札価格", "mean"),
                最安=("落札価格", "min"),
                最高=("落札価格", "max"),
                入札平均=("入札数", "mean"),
                平均開始価格=("開始価格", "mean")
            )
            .reset_index()
        )

        # ==============================
        # AI風 仕入れ・利益分析
        # ==============================
        result["仕入れ上限"] = (result["平均落札"] * 0.75).round(0)
        result["予想販売"] = (result["平均落札"] * 1.05).round(0)
        result["予想利益"] = (result["予想販売"] - result["仕入れ上限"]).round(0)
        result["人気スコア"] = (result["入札平均"] / result["入札平均"].max() * 5).round(1)

        # ==============================
        # 検索フィルタ
        # ==============================
        st.write("### 🔍 モデル検索")
        search = st.text_input("キーワードを入力（例：アルデバラン、ヴァンキッシュ など）")

        filtered = result[result["モデル"].str.contains(search, case=False, na=False)] if search else result

        # ==============================
        # 結果表示
        # ==============================
        st.write("### 📈 分析結果")
        st.dataframe(filtered, use_container_width=True)

        # ==============================
        # グラフ表示
        # ==============================
        st.write("### 📊 平均落札価格（モデル別）")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(filtered["モデル"], filtered["平均落札"], color="skyblue")
        ax.set_xlabel("モデル")
        ax.set_ylabel("平均落札価格（円）")
        ax.set_title("モデル別 平均落札価格")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

        # ==============================
        # CSVダウンロード
        # ==============================
        csv = filtered.to_csv(index=False)
        st.download_button(
            label="📥 分析結果をCSVでダウンロード",
            data=csv,
            file_name="ai_auction_analysis.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"❌ エラーが発生しました: {e}")

else:
    st.info("左のボタンからCSVファイルをアップロードしてください。")