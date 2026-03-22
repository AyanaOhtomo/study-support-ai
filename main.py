import streamlit as st
import database as db
import components as cp
import constants as ct
import utils as ut

# ==========================================
# 1. 初期設定
# ==========================================
db.initialize_db()

st.set_page_config(
    page_title=ct.APP_TITLE,
    page_icon=ct.APP_ICON,
    layout="centered"
)

# ==========================================
# 2. タイトル表示
# ==========================================
cp.display_app_title()

# ==========================================
# 3. サイドバー表示
# ==========================================
selected_page = cp.display_sidebar()

# ==========================================
# 4. ページごとの表示切り替え
# ==========================================

# ダッシュボード
if selected_page == ct.PAGE_DASHBOARD:
    summary = db.get_dashboard_summary()
    category_df = db.get_category_study_time()
    cp.display_dashboard(summary, category_df)

# 学習記録入力
elif selected_page == ct.PAGE_STUDY_LOG:
    (
        study_date,
        category,
        study_time,
        content,
        understanding,
        blocking_point,
        next_action,
        submit_button
    ) = cp.display_study_log_form()

    if submit_button:
        db.insert_study_log(
            study_date,
            category,
            study_time,
            content,
            understanding,
            blocking_point,
            next_action
        )
        st.success(ct.SUCCESS_MESSAGE)

# 学習履歴
elif selected_page == ct.PAGE_HISTORY:
    logs_df = db.get_all_study_logs()
    cp.display_study_logs(logs_df)

# 週間レポート
elif selected_page == ct.PAGE_AI_COACHING:
    weekly_summary = db.get_weekly_summary()
    cp.display_weekly_report(weekly_summary)

    # 週間レポートのAI生成は、今週の学習記録がある場合のみ行う
    if weekly_summary["total_logs"] > 0:
        try:
            ai_report = ut.generate_weekly_report(weekly_summary)
            cp.display_ai_weekly_report(ai_report)
        except Exception:
            st.error(ct.WEEKLY_REPORT_ERROR_MESSAGE)

            # チャット履歴の初期化
            if "ai_coach_messages" not in st.session_state:
                st.session_state.ai_coach_messages = [
                    {
                        "role": "assistant",
                        "content": ct.AI_COACH_INITIAL_MESSAGE
                    }
                ]

            # チャット履歴表示
            cp.display_ai_chat_messages(st.session_state.ai_coach_messages)

            # チャット入力
            user_message = st.chat_input(ct.AI_CHAT_INPUT_PLACEHOLDER)

            if user_message:
                # ユーザー発言を履歴追加
                st.session_state.ai_coach_messages.append(
                    {"role": "user", "content": user_message}
                )

                try:
                    ai_reply = utils.generate_ai_coaching_reply(
                        weekly_summary,
                        user_message
                    )

                    # AI回答を履歴追加
                    st.session_state.ai_coach_messages.append(
                        {"role": "assistant", "content": ai_reply}
                    )

                    st.rerun()

                except Exception:
                    st.error(ct.AI_CHAT_ERROR_MESSAGE)
        else:
            st.info(ct.NO_WEEKLY_DATA_MESSAGE)       