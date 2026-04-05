import streamlit as st
import database as db
import components as cp
import constants as ct
import utils as ut

# ==========================================
# 0. パスワード認証
# ==========================================
def check_password():
    if st.session_state.get("authenticated"):
        return
    st.title("Study Support AI")
    st.caption("デモ用ログイン画面です。README に記載のアカウント情報をご利用ください。")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if (username == st.secrets.get("DEMO_USERNAME", "")
                and password == st.secrets.get("DEMO_PASSWORD", "")):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが違います")
    st.stop()

check_password()

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
    daily_df = db.get_daily_study_time()
    streak = db.get_study_streak()
    current_goal = db.get_current_goal()
    weekly_summary = db.get_weekly_summary()
    cp.display_dashboard(summary, category_df, daily_df, streak, current_goal, weekly_summary)

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

# AIコーチング
elif selected_page == ct.PAGE_AI_COACHING:
    weekly_summary = db.get_weekly_summary()
    current_goal = db.get_current_goal()

    # つまずき・次回やることのサマリーを生成（記録がある場合のみ）
    points_summary = None
    if weekly_summary["total_logs"] > 0:
        try:
            points_summary = ut.generate_points_summary(
                weekly_summary["blocking_points_by_category"],
                weekly_summary["next_actions_by_category"]
            )
        except Exception:
            pass  # 失敗しても既存表示にフォールバックするため握りつぶす

    cp.display_weekly_report(weekly_summary, points_summary)

    # 今週の学習記録がある場合はAIコーチング機能を表示
    if weekly_summary["total_logs"] > 0:
        try:
            ai_report = ut.generate_weekly_report(weekly_summary, current_goal)
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

            # 履歴を文字列に変換
            chat_history_text = "\n".join([
                f"{m['role']}: {m['content']}"
                for m in st.session_state.ai_coach_messages
            ])

            try:
                ai_reply = ut.generate_ai_coaching_reply(
                    weekly_summary,
                    user_message,
                    chat_history_text,
                    current_goal
                )

                # AI回答を履歴追加
                st.session_state.ai_coach_messages.append(
                    {"role": "assistant", "content": ai_reply}
                )

                st.rerun()

            except Exception:
                st.error(ct.AI_CHAT_ERROR_MESSAGE)

# 目標設定
elif selected_page == ct.PAGE_GOAL:
    current_goal = db.get_current_goal()
    target_minutes, goal_description, submit_button = cp.display_goal_page(current_goal)

    if submit_button:
        if goal_description.strip():
            db.save_goal(target_minutes, goal_description)
            st.success(ct.GOAL_SAVE_SUCCESS_MESSAGE)
            st.rerun()
        else:
            st.warning("学習目標を入力してください。")