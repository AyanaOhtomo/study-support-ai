import streamlit as st
import plotly.express as px
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


def display_dashboard(summary, category_df):
    """
    ダッシュボードを表示する

    Args:
        summary (dict): 集計結果
        category_df (pd.DataFrame): 学習テーマ別学習時間
    """
    st.divider()
    st.subheader("ダッシュボード")
    st.markdown("学習状況をサマリーとグラフで確認できます。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("合計学習時間", f"{summary['total_study_time']} 分")
    with col2:
        st.metric("学習回数", f"{summary['total_logs']} 回")
    with col3:
        st.metric("平均理解度", f"{summary['average_understanding']} / 5")

    if not category_df.empty:
        st.markdown("#### 学習テーマ別の学習時間")

        fig = px.bar(
            category_df,
            x="学習テーマ",
            y="学習時間",
            text="学習時間"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            xaxis_title="学習テーマ",
            yaxis_title="学習時間（分）",
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )

        st.plotly_chart(fig, width="stretch")
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
        logs_df = logs_df.drop(columns=["id", "created_at"])
        logs_df = logs_df.rename(columns=ct.LABELS)

        st.dataframe(logs_df, width="stretch", hide_index=True)

def display_weekly_report(summary):
    """
    今週の学習サマリーを表示する
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
        if summary["blocking_points"]:
            for point in summary["blocking_points"]:
                st.markdown(f"- {point}")
        else:
            st.write(ct.NO_DATA_MESSAGE)

        st.markdown("**次回やること**")
        if summary["next_actions"]:
            for action in summary["next_actions"]:
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