import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import constants as ct

# SQLiteのDBファイル名
DB_NAME = "study_support_ai.db"

def get_connection():
    """
    SQLiteデータベースへの接続を取得する

    Returns:
        sqlite3.Connection: DB接続オブジェクト
    """
    return sqlite3.connect(ct.DB_NAME)

def initialize_db():
    """
    学習記録テーブル・目標テーブルを作成する
    すでに存在する場合は何もしない
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            study_date TEXT NOT NULL,
            category TEXT NOT NULL,
            study_time INTEGER NOT NULL,
            content TEXT NOT NULL,
            understanding INTEGER NOT NULL,
            blocking_point TEXT,
            next_action TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_minutes INTEGER NOT NULL,
            goal_description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_goal(target_minutes, goal_description):
    """
    目標を保存する（毎回追加し、最新の1件を有効な目標として扱う）

    Args:
        target_minutes (int): 週の目標学習時間（分）
        goal_description (str): 学習目標の説明
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO goals (target_minutes, goal_description, created_at)
        VALUES (?, ?, ?)
    """, (target_minutes, goal_description, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_current_goal():
    """
    最新の目標を取得する

    Returns:
        dict or None:
            target_minutes (int): 週の目標学習時間（分）
            goal_description (str): 学習目標の説明
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT target_minutes, goal_description
        FROM goals
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "target_minutes": row[0],
        "goal_description": row[1]
    }

def insert_study_log(
            study_date,
            category,
            study_time,
            content,
            understanding,
            blocking_point,
            next_action
    ):
        """
        学習記録をDBに追加する

        Args:
            study_date (date): 学習日
            category (str): 学習テーマ
            study_time (int): 学習時間（分）
            content (str): 学習内容
            understanding (int): 理解度
            blocking_point (str): つまずいたポイント
            next_action (str): 次回やること
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO study_logs (
                study_date,
                category,
                study_time,
                content,
                understanding,
                blocking_point,
                next_action,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(study_date),
            category,
            study_time,
            content,
            understanding,
            blocking_point,
            next_action,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

def get_all_study_logs():
    """
    学習記録をすべて取得する
    新しい学習日・新しい登録順で並べる

    Returns:
        pd.DataFrame: 学習記録一覧
    """
    conn = get_connection()

    query = """
        SELECT * 
        FROM study_logs 
        ORDER BY study_date DESC, id DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_dashboard_summary():
    """
    ダッシュボード表示用の集計値を取得する

    Returns:
        dict:
            total_study_time (int): 合計学習時間
            total_logs (int): 学習回数
            average_understanding (float): 平均理解度
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COALESCE(SUM(study_time), 0) AS total_study_time,
            count(*) AS total_logs,
            COALESCE(AVG(understanding), 0) AS average_understanding
        FROM study_logs
    """)

    result = cursor.fetchone()
    conn.close()

    return {
        "total_study_time": result[0],
        "total_logs": result[1],
        "average_understanding": round(result[2], 1)
    }

def get_category_study_time():
    """
    学習テーマごとの合計学習時間を取得する

    Returns:
        pd.DataFrame:
            学習テーマごとの学習時間集計結果
    """
    conn = get_connection()

    query = """
        SELECT 
            category AS 学習テーマ, 
            SUM(study_time) AS 学習時間
        FROM study_logs
        GROUP BY category
        ORDER BY SUM(study_time) DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_weekly_study_logs():
    """
    今週の学習記録を取得する

    Returns:
        pd.DataFrame: 今週の学習記録一覧
    """
    conn = get_connection()

    query = """
        SELECT *
        FROM study_logs
        WHERE study_date >= date('now', 'weekday 0', '-6 days')
        ORDER BY study_date DESC, id DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def get_weekly_summary():
    """
    今週の学習記録を集計する

    Returns:
        dict: 今週の学習サマリー
    """
    weekly_df = get_weekly_study_logs()

    if weekly_df.empty:
        return {
            "total_study_time": 0,
            "total_logs": 0,
            "average_understanding": 0,
            "top_category": "なし",
            "blocking_points": [],
            "next_actions": []
        }

    total_study_time = int(weekly_df["study_time"].sum())
    total_logs = int(len(weekly_df))
    average_understanding = round(float(weekly_df["understanding"].mean()), 1)

    top_category = (
        weekly_df.groupby("category")["study_time"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    blocking_points = [
        value for value in weekly_df["blocking_point"].dropna().tolist()
        if str(value).strip()
    ]

    next_actions = [
        value for value in weekly_df["next_action"].dropna().tolist()
        if str(value).strip()
    ]

    # カテゴリ別にまとめた辞書（表示用）
    blocking_points_by_category = {}
    next_actions_by_category = {}

    for _, row in weekly_df.iterrows():
        category = row["category"]

        bp = str(row["blocking_point"]).strip() if pd.notna(row["blocking_point"]) else ""
        if bp:
            blocking_points_by_category.setdefault(category, []).append(bp)

        na = str(row["next_action"]).strip() if pd.notna(row["next_action"]) else ""
        if na:
            next_actions_by_category.setdefault(category, []).append(na)

    return {
        "total_study_time": total_study_time,
        "total_logs": total_logs,
        "average_understanding": average_understanding,
        "top_category": top_category,
        "blocking_points": blocking_points,
        "next_actions": next_actions,
        "blocking_points_by_category": blocking_points_by_category,
        "next_actions_by_category": next_actions_by_category
    }


def get_daily_study_time():
    """
    日付ごとの合計学習時間を取得する（折れ線グラフ用）

    Returns:
        pd.DataFrame:
            study_date (str): 学習日
            学習時間 (int): その日の合計学習時間（分）
    """
    conn = get_connection()

    query = """
        SELECT
            study_date,
            SUM(study_time) AS 学習時間
        FROM study_logs
        GROUP BY study_date
        ORDER BY study_date ASC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def get_study_streak():
    """
    今日を起点とした連続学習日数を返す
    今日の記録がない場合は 0 を返す

    Returns:
        int: 連続学習日数
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT study_date FROM study_logs")
    rows = cursor.fetchall()
    conn.close()

    # 学習済み日付を date 型の集合に変換
    study_dates = {date.fromisoformat(row[0]) for row in rows}

    streak = 0
    check = date.today()
    while check in study_dates:
        streak += 1
        check -= timedelta(days=1)

    return streak