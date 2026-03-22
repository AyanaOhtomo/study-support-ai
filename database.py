import sqlite3
import pandas as pd
from datetime import datetime
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
    学習記録テーブルを作成する
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

    conn.commit()
    conn.close()

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

    return {
        "total_study_time": total_study_time,
        "total_logs": total_logs,
        "average_understanding": average_understanding,
        "top_category": top_category,
        "blocking_points": blocking_points,
        "next_actions": next_actions
    }