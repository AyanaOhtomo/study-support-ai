import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date
import constants as ct


def display_sidebar():
    """
    サイドバーにページ選択メニューを表示する

    Returns:
        str: 選択中のページ名
    """
    with st.sidebar:
        st.markdown("## メニュー")
        selected_page = st.radio(
            "表示ページを選択",
            [
                ct.PAGE_GOAL,
                ct.PAGE_STUDY_LOG,
                ct.PAGE_AI_COACHING,
                ct.PAGE_HISTORY,
                ct.PAGE_DASHBOARD
            ],
            label_visibility="collapsed"
        )

    return selected_page

def display_app_title():
    """
    アプリのタイトルと説明を表示する
    """
    st.title(f"🎓 {ct.APP_TITLE}")

def display_study_log_form():
    """
    学習記録入力フォームを表示する

    Returns:
        tuple:
            study_date, category, study_time, content,
            understanding, blocking_point, next_action, submit_button
    """
    st.divider()
    st.subheader("学習記録")
    st.markdown("学習した内容や感じたことを記録しましょう！")

    with st.form(key="study_log_form"):
        st.subheader("学習記録を入力")

        study_date = st.date_input("学習日", value=date.today())

        category = st.selectbox(
            "学習テーマ",
            ct.CATEGORIES
        )

        study_time = st.number_input(
            "学習時間（分）",
            min_value=1,
            max_value=1440,
            value=60
        )

        content = st.text_area(
            "学習内容",
            placeholder="今日学んだことや感じたことを記録しましょう！"
        )

        understanding = st.slider(
            "理解度",
            min_value=1,
            max_value=5,
            value=3
        )

        blocking_point = st.text_area(
            "つまずいたポイント",
            placeholder="学習中につまずいたことや疑問点を記録しましょう！"
        )

        next_action = st.text_area(
            "次回やること",
            placeholder="次回の学習で取り組みたいことや改善点を記録しましょう！"
        )

        col1, col2, col3 = st.columns([6, 2, 2])
        with col3:
            submit_button = st.form_submit_button(
                label="記録を保存",
                type="primary"
            )

    return (
        study_date,
        category,
        study_time,
        content,
        understanding,
        blocking_point,
        next_action,
        submit_button
    )


def display_dashboard(summary, category_df, daily_df=None, streak=0, current_goal=None, weekly_summary=None):
    """
    ダッシュボードを表示する

    Args:
        summary (dict): 集計結果（合計学習時間・回数・平均理解度）
        category_df (pd.DataFrame): 学習テーマ別学習時間
        daily_df (pd.DataFrame or None): 日付ごとの学習時間（折れ線グラフ用）
        streak (int): 連続学習日数
        current_goal (dict or None): 現在の目標（target_minutes, goal_description）
        weekly_summary (dict or None): 今週の学習サマリー（目標達成率の計算用）
    """
    st.divider()
    st.subheader("ダッシュボード")
    st.markdown("学習状況をサマリーとグラフで確認できます。")

    # ── メトリクス（4列）──────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("合計学習時間", f"{summary['total_study_time']} 分")
    with col2:
        st.metric("学習回数", f"{summary['total_logs']} 回")
    with col3:
        st.metric("平均理解度", f"{summary['average_understanding']} / 5")
    with col4:
        st.metric("連続学習日数", f"{streak} 日")

    # ── 目標達成率（目標が設定されている場合のみ表示）──────
    if current_goal and weekly_summary:
        target = current_goal["target_minutes"]
        actual = weekly_summary["total_study_time"]
        rate = min(actual / target, 1.0) if target > 0 else 0.0

        st.markdown("#### 今週の目標達成率")
        st.caption(f"目標：{target} 分　／　今週の実績：{actual} 分")
        st.progress(rate, text=f"{int(rate * 100)} %")

    # ── 日別学習時間（折れ線グラフ）──────────────────
    if daily_df is not None and not daily_df.empty:
        st.markdown("#### 日別学習時間")

        fig_line = px.line(
            daily_df,
            x="study_date",
            y="学習時間",
            markers=True
        )

        fig_line.update_layout(
            xaxis_title="日付",
            yaxis_title="学習時間（分）",
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_line, use_container_width=True)

    # ── 学習テーマ別の学習時間（棒グラフ・既存）──────────
    if not category_df.empty:
        st.markdown("#### 学習テーマ別の学習時間")

        fig_bar = px.bar(
            category_df,
            x="学習テーマ",
            y="学習時間",
            text="学習時間"
        )

        fig_bar.update_traces(textposition="outside")

        fig_bar.update_layout(
            xaxis_title="学習テーマ",
            yaxis_title="学習時間（分）",
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info(ct.NO_CHART_DATA_MESSAGE)


def display_study_logs(logs_df):
    """
    学習記録一覧を表示する

    Args:
        logs_df (pd.DataFrame): 学習記録一覧
    """
    st.divider()
    st.subheader("学習記録一覧")
    st.markdown("今までの学習記録を振り返りましょう!")

    if logs_df.empty:
        st.info(ct.NO_DATA_MESSAGE)
    else:
        # 【追加】日付比較用に文字列の study_date を日付型にそろえる（絞り込みはリネーム前の列名で行う）
        study_dates = pd.to_datetime(logs_df["study_date"])
        date_min = study_dates.min().date()
        date_max = study_dates.max().date()

        # 【追加】絞り込み用の見出し（なくても動くが、どこがフィルタ欄か分かりやすくする）
        st.markdown("###### 絞り込み")

        # 【追加】フィルタ1: 日付範囲（デフォルトはデータにある最小日〜最大日）
        date_range = st.date_input(
            "表示期間（開始〜終了）",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
        )

        # 【追加】date_input の戻り値を正規化する
        # ・範囲選択: (開始日, 終了日)
        # ・途中の操作で (1日だけ,) のような「長さ1のタプル」になることがある
        # ・単一選択: date そのもの
        if isinstance(date_range, (tuple, list)):
            if len(date_range) >= 2:
                range_start, range_end = date_range[0], date_range[1]
            elif len(date_range) == 1:
                single = date_range[0]
                range_start = range_end = single
            else:
                range_start, range_end = date_min, date_max
        else:
            range_start = range_end = date_range

        # 【追加】フィルタ2: 学習テーマ（データに実際に存在する category から候補を作る）
        theme_options = ["すべて"] + sorted(logs_df["category"].dropna().unique().tolist())
        selected_theme = st.selectbox("学習テーマ", options=theme_options)

        # 【追加】フィルタ3: 学習時間が指定分数「以上」の行だけ残す（0 なら下限なし）
        min_study_minutes = st.number_input(
            "学習時間（○分以上）",
            min_value=0,
            value=0,
        )

        # 【追加】条件ごとに True/False を並べ、& でつなげて一行ずつ「全部の条件を満たすか」を判定する
        mask = pd.Series(True, index=logs_df.index)
        mask &= (study_dates >= pd.Timestamp(range_start)) & (
            study_dates <= pd.Timestamp(range_end)
        )
        if selected_theme != "すべて":
            mask &= logs_df["category"] == selected_theme
        mask &= logs_df["study_time"] >= min_study_minutes

        # 【追加】英語列名のまま絞り込んだ結果を、以降の表示処理に渡す
        filtered_df = logs_df.loc[mask]

        # 【既存と同じ】一覧表示用に列を整理してから表を出す
        filtered_df = filtered_df.drop(columns=["id", "created_at"])
        filtered_df = filtered_df.rename(columns=ct.LABELS)

        if filtered_df.empty:
            st.info("条件に合う学習記録がありません。")
        else:
            st.dataframe(filtered_df, width="stretch", hide_index=True)

            st.download_button(
                label="CSVでダウンロード",
                data=filtered_df.to_csv(index=False, encoding="utf-8-sig"),
                file_name="study_logs.csv",
                mime="text/csv"
            )

def display_goal_page(current_goal):
    """
    目標設定ページを表示する

    Args:
        current_goal (dict or None): 現在の目標情報
    Returns:
        tuple: (target_minutes, goal_description, submit_button)
    """
    st.divider()
    st.subheader("目標設定")
    st.markdown("学習の方向性と週間の目標時間を設定しましょう。")

    # 現在の目標を表示
    if current_goal:
        with st.expander("📌 現在の目標", expanded=True):
            st.markdown(f"**学習目標：** {current_goal['goal_description']}")
            st.markdown(f"**週間目標時間：** {current_goal['target_minutes']} 分")
    else:
        st.info(ct.NO_GOAL_MESSAGE)

    st.markdown("---")
    st.markdown("#### 新しい目標を設定する")

    with st.form(key="goal_form"):
        goal_description = st.text_area(
            "学習目標（どこを目指して学ぶか）",
            placeholder=ct.GOAL_DESCRIPTION_PLACEHOLDER,
            height=100
        )

        target_minutes = st.number_input(
            "週間の目標学習時間（分）",
            min_value=1,
            max_value=10080,
            value=current_goal["target_minutes"] if current_goal else 300
        )

        col1, col2, col3 = st.columns([6, 2, 2])
        with col3:
            submit_button = st.form_submit_button(label="目標を保存", type="primary")

    return target_minutes, goal_description, submit_button


def display_weekly_report(summary, points_summary=None):
    """
    今週の学習サマリーを表示する

    Args:
        summary (dict): 今週の学習サマリー
        points_summary (dict or None): LLMが生成したつまずき・次回やることのサマリー
            {"blocking_summary": "...", "next_actions_summary": "..."}
            None の場合はカテゴリ別の箇条書きにフォールバック
    """
    st.divider()
    st.subheader("AIコーチング")
    st.markdown("AIコーチがあなたの学習状況を分析し、改善提案を行います。")

    if summary["total_logs"] == 0:
        st.info(ct.NO_WEEKLY_DATA_MESSAGE)
        return

    with st.expander("📘 今週の学習サマリーを見る", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("合計学習時間", f"{summary['total_study_time']} 分")
        col2.metric("学習回数", f"{summary['total_logs']} 回")
        col3.metric("平均理解度", f"{summary['average_understanding']} / 5")

        st.write(f"**最も学習したテーマ**：{summary['top_category']}")

        st.markdown("**つまずいたポイント**")
        if points_summary:
            st.write(points_summary["blocking_summary"])
        elif summary["blocking_points_by_category"]:
            for category, points in summary["blocking_points_by_category"].items():
                st.markdown(f"**{category}**")
                for point in points:
                    st.markdown(f"- {point}")
        else:
            st.write(ct.NO_DATA_MESSAGE)

        st.markdown("**次回やること**")
        if points_summary:
            st.write(points_summary["next_actions_summary"])
        elif summary["next_actions_by_category"]:
            for category, actions in summary["next_actions_by_category"].items():
                st.markdown(f"**{category}**")
                for action in actions:
                    st.markdown(f"- {action}")
        else:
            st.write(ct.NO_DATA_MESSAGE)

def display_ai_weekly_report(report_text):
    """
    AIが生成した週間レポートを表示する

    Args:
        report_text (str): AIが生成したレポート本文
    """
    st.markdown("#### 🤖 AIコーチからの週間フィードバック")
    st.success(report_text)

def display_ai_chat_messages(messages):
    """
    AIコーチとのチャット履歴を表示する

    Args:
        messages (list): チャットメッセージ一覧
    """
    st.markdown("#### 💬 AIコーチに相談する")

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])