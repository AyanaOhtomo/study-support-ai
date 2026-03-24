import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# .env の内容を読み込む
load_dotenv()

# LangChain で使う LLM を作成
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


def build_weekly_report_prompt():
    """
    週間フィードバック生成用のプロンプトテンプレートを作成する

    Returns:
        PromptTemplate: LangChain用プロンプトテンプレート
    """
    template = """
あなたはプログラミング学習を支援する優秀なAIコーチです。
以下の学習記録サマリーをもとに、学習者向けの週間フィードバックを日本語で作成してください。

【要件】
- やさしく前向きなトーンで書く
- 今週の取り組みを簡潔に振り返る
- 良かった点を1つ以上入れる
- 改善点や次週のアドバイスを入れる
- 200〜300文字程度でまとめる

【今週の学習サマリー】
- 合計学習時間: {total_study_time} 分
- 学習回数: {total_logs} 回
- 平均理解度: {average_understanding} / 5
- 最も学習したテーマ: {top_category}

【つまずいたポイント】
{blocking_points_text}

【次回やること】
{next_actions_text}
"""
    return PromptTemplate(
        input_variables=[
            "total_study_time",
            "total_logs",
            "average_understanding",
            "top_category",
            "blocking_points_text",
            "next_actions_text"
        ],
        template=template
    )


def generate_weekly_report(summary):
    """
    LangChain を使って週間フィードバックを生成する

    Args:
        summary (dict): 今週の学習サマリー

    Returns:
        str: AIが生成した週間フィードバック
    """
    blocking_points_text = "\n".join(
        [f"- {point}" for point in summary["blocking_points"]]
    ) if summary["blocking_points"] else "なし"

    next_actions_text = "\n".join(
        [f"- {action}" for action in summary["next_actions"]]
    ) if summary["next_actions"] else "なし"

    prompt = build_weekly_report_prompt()

    chain = prompt | llm

    response = chain.invoke({
        "total_study_time": summary["total_study_time"],
        "total_logs": summary["total_logs"],
        "average_understanding": summary["average_understanding"],
        "top_category": summary["top_category"],
        "blocking_points_text": blocking_points_text,
        "next_actions_text": next_actions_text
    })

    return response.content


def build_ai_coaching_chat_prompt():
    """
    AIコーチとの対話用プロンプトテンプレートを作成する

    Returns:
        PromptTemplate: LangChain用プロンプトテンプレート
    """
    template = """
あなたはプログラミング学習を支援する優秀なAIコーチです。
以下の今週の学習状況を踏まえて、学習者の質問に日本語で回答してください。

【重要ルール】
- 最初の1回だけ軽い挨拶をする（例：「学習おつかれさまです!」）
- 2回目以降は挨拶を省略して回答する
- 毎回同じ表現を繰り返さない
- 自然な会話を意識する

【回答ルール】
- やさしく前向きな口調
- 学習者を責めない
- 今週の記録に基づいて具体的に答える
- 必要なら次にやるべきことを提案する
- 回答は150〜250文字程度

【今週の学習サマリー】
- 合計学習時間: {total_study_time} 分
- 学習回数: {total_logs} 回
- 平均理解度: {average_understanding} / 5
- 最も学習したテーマ: {top_category}

【つまずいたポイント】
{blocking_points_text}

【次回やること】
{next_actions_text}

【チャット履歴】
{chat_history_text}

【学習者の質問】
{user_message}
"""
    return PromptTemplate(
        input_variables=[
            "total_study_time",
            "total_logs",
            "average_understanding",
            "top_category",
            "blocking_points_text",
            "next_actions_text",
            "user_message"
        ],
        template=template
    )


def generate_ai_coaching_reply(summary, user_message, chat_history_text):
    """
    LangChain を使って AIコーチのチャット回答を生成する

    Args:
        summary (dict): 今週の学習サマリー
        user_message (str): ユーザーの質問
        chat_history_text (str): チャット履歴

    Returns:
        str: AIコーチの回答
    """
    blocking_points_text = "\n".join(
        [f"- {point}" for point in summary["blocking_points"]]
    ) if summary["blocking_points"] else "なし"

    next_actions_text = "\n".join(
        [f"- {action}" for action in summary["next_actions"]]
    ) if summary["next_actions"] else "なし"

    prompt = build_ai_coaching_chat_prompt()

    chain = prompt | llm

    response = chain.invoke({
        "total_study_time": summary["total_study_time"],
        "total_logs": summary["total_logs"],
        "average_understanding": summary["average_understanding"],
        "top_category": summary["top_category"],
        "blocking_points_text": blocking_points_text,
        "next_actions_text": next_actions_text,
        "chat_history_text": chat_history_text,
        "user_message": user_message
    })

    return response.content