import streamlit as st
import pandas as pd

st.set_page_config(page_title="容量実績変換ツール", layout="centered")

st.title("📶 容量実績変換ツール")
st.write("CSVをアップロードして、データ利用量をGB単位に変換・集計します。")

uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # --- 文字コード対策を施した読み込み ---
    try:
        # まずは標準のUTF-8で試す
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        # エラーが出たら日本語用（cp932/Shift-JIS）で開き直す
        uploaded_file.seek(0) # 読み込み位置を最初に戻す
        df = pd.read_csv(uploaded_file, encoding='cp932')
    
    try:
        cols = df.columns.tolist()

        # --- 自動判定ロジック ---
        template = "手動設定"
        date_col, usage_col, unit = cols[0], cols[0], "MB" 

        if 'Usaged_Byte' in cols and 'IMEI' in cols:
            template, date_col, usage_col, unit = "GlocalMe形式", "Date", "Usaged_Byte", "Byte"
        
        elif '合計パケット(byte)' in cols and '対象明細日付' in cols:
            template, date_col, usage_col, unit = "NWC形式", "対象明細日付", "合計パケット(byte)", "Byte"
        
        elif 'Usaged' in cols:
            template, date_col, usage_col, unit = "MB形式", "Date", "Usaged", "MB"

        # --- 設定の確認・調整 ---
        with st.expander(f"判定結果: {template} (必要ならここを調整)", expanded=(template=="手動設定")):
            date_col = st.selectbox("日付の列", cols, index=cols.index(date_col) if date_col in cols else 0)
            usage_col = st.selectbox("データ量の列", cols, index=cols.index(usage_col) if usage_col in cols else 0)
            unit = st.radio("元の単位", ["Byte", "MB", "GB"], index=["Byte", "MB", "GB"].index(unit))

        # --- 計算処理 ---
        if st.button("変換・集計を実行"):
            df_res = df.copy()
            
            # 日付の処理
            df_res[date_col] = pd.to_datetime(df_res[date_col], format='mixed').dt.date
            
            # GBに統一計算
            div = {"Byte": 1024**3, "MB": 1024, "GB": 1}[unit]
            df_res['GB'] = (df_res[usage_col] / div).round(2)

            # 結果表示
            st.success(f"✅ {template} として集計完了！ 合計: {df_res['GB'].sum():.2f} GB")
            
            display_df = df_res[[date_col, 'GB']].copy()
            display_df.columns = ['日付', '利用量(GB)']
            
            st.dataframe(display_df, use_container_width=True)

            csv = display_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("結果を保存 (CSV)", data=csv, file_name=f"容量実績_{template}.csv")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
