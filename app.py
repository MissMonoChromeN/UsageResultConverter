import streamlit as st
import pandas as pd

st.set_page_config(page_title="Wi-Fiデータ集計ツール", layout="centered")

st.title("📶 容量実績変換ツール")
st.write("CSVをアップロードするだけで、自動で単位を判別してGBに変換します。")

uploaded_file = st.file_uploader("CSVファイルをアップロード・ドラッグ＆ドロップしてください", type="csv")

if uploaded_file is not None:
    try:
        # CSV読み込み
        df = pd.read_csv(uploaded_file)
        cols = df.columns.tolist()

        # 自動判定ロジック
        template = "手動設定"
        date_col, usage_col, unit = cols[0], cols[0], "MB" # 初期値

        if 'Usaged_Byte' in cols:
            template, date_col, usage_col, unit = "GlocalMe形式", "Date", "Usaged_Byte", "Byte"
        elif 'Usaged' in cols:
            template, date_col, usage_col, unit = "MB形式", "Date", "Usaged", "MB"

        # 設定の確認
        with st.expander(f"判定: {template} (クリックで調整)", expanded=(template=="手動設定")):
            date_col = st.selectbox("日付の列", cols, index=cols.index(date_col) if date_col in cols else 0)
            usage_col = st.selectbox("データ量の列", cols, index=cols.index(usage_col) if usage_col in cols else 0)
            unit = st.radio("元の単位", ["Byte", "MB", "GB"], index=["Byte", "MB", "GB"].index(unit))

        if st.button("計算・集計を実行"):
            df_res = df.copy()
            df_res[date_col] = pd.to_datetime(df_res[date_col]).dt.date
            
            # GB変換
            div = {"Byte": 1024**3, "MB": 1024, "GB": 1}[unit]
            df_res['利用量(GB)'] = (df_res[usage_col] / div).round(3)

            # 結果表示
            st.success(f"✅ 合計: {df_res['利用量(GB)'].sum():.2f} GB")
            st.dataframe(df_res[[date_col, usage_col, '利用量(GB)']], use_container_width=True)

            # ダウンロード
            csv = df_res.to_csv(index=False).encode('utf-8-sig')
            st.download_button("結果を保存", data=csv, file_name="converted.csv")
    except Exception as e:
        st.error(f"エラー: {e}")