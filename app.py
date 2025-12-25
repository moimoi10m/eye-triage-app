from dataclasses import dataclass
from typing import Callable, Optional, Tuple


@dataclass
class Question:
    prompt: str
    handler: Callable[[str], Tuple[int, Optional[int]]]
    critical_level: Optional[int] = None


def ask_yes_no(score_yes: int, critical_level: Optional[int] = None) -> Callable[[str], Tuple[int, Optional[int]]]:
    def _ask(user_input: str) -> Tuple[int, Optional[int]]:
        answer = user_input.strip().lower()
        if answer in {"yes", "y", "はい", "はい。", "うん", "そう", "うん。"}:
            return score_yes, critical_level
        return 0, None

    return _ask


def ask_choice(options: dict) -> Callable[[str], Tuple[int, Optional[int]]]:
    normalized = {key.lower(): value for key, value in options.items()}

    def _ask(user_input: str) -> Tuple[int, Optional[int]]:
        answer = user_input.strip().lower()
        score, critical = normalized.get(answer, (0, None))
        return score, critical

    return _ask


def determine_urgency(total_score: int, critical_level: Optional[int]) -> int:
    if critical_level:
        return critical_level
    if total_score >= 16:
        return 4
    if total_score >= 10:
        return 3
    if total_score >= 6:
        return 2
    return 1


URGENCY_LABELS = {
    1: "セルフケア・経過観察",
    2: "数日以内に眼科を予約",
    3: "1〜2日以内に受診を検討",
    4: "当日受診を強く推奨",
    5: "救急外来を含む至急受診",
}


QUESTIONS = [
    Question(
        prompt="突然の視力低下や視界が真っ黒になった？（はい/いいえ）",
        handler=ask_yes_no(score_yes=10, critical_level=5),
    ),
    Question(
        prompt="強い目の痛み、または眼球を動かせないほどの痛みがある？（はい/いいえ）",
        handler=ask_yes_no(score_yes=8, critical_level=5),
    ),
    Question(
        prompt="目をぶつけた・何かが刺さった・化学物質が入った？（はい/いいえ）",
        handler=ask_yes_no(score_yes=10, critical_level=5),
    ),
    Question(
        prompt="光が走る、急に飛蚊症が増えた、カーテンがかかったように見える？（はい/いいえ）",
        handler=ask_yes_no(score_yes=7, critical_level=4),
    ),
    Question(
        prompt="視界が歪む、片頭痛のようなギザギザが見える？（はい/いいえ）",
        handler=ask_yes_no(score_yes=5),
    ),
    Question(
        prompt="コンタクト使用中に赤み・痛み・膿のような分泌物がある？（はい/いいえ）",
        handler=ask_yes_no(score_yes=6, critical_level=4),
    ),
    Question(
        prompt="糖尿病・高血圧などの持病があり視界が変わった？（はい/いいえ）",
        handler=ask_yes_no(score_yes=5),
    ),
    Question(
        prompt="目がかゆく、充血や涙が続いている？（はい/いいえ）",
        handler=ask_yes_no(score_yes=3),
    ),
    Question(
        prompt="頭痛・吐き気・虹がかかって見えるなど、急性緑内障のような症状がある？（はい/いいえ）",
        handler=ask_yes_no(score_yes=8, critical_level=5),
    ),
    Question(
        prompt="症状が始まってからどれくらい？（時間/日/週）",
        handler=ask_choice(
            {
                "時間": (6, 4),
                "日": (3, None),
                "週": (1, None),
                "hours": (6, 4),
                "days": (3, None),
                "weeks": (1, None),
            }
        ),
    ),
]


def main() -> None:
    print("🦉 緑のフクロウ: いくつか質問するね。日本語でシンプルに答えて！")
    total_score = 0
    critical_level = None

    for idx, question in enumerate(QUESTIONS, start=1):
        print(f"\n質問 {idx}/{len(QUESTIONS)}: {question.prompt}")
        user_input = input("あなたの答え: ")
        score, flagged_level = question.handler(user_input)
        total_score += score
        if flagged_level and (critical_level is None or flagged_level > critical_level):
            critical_level = flagged_level
        if idx >= 10:  # 最大10問で終了
            break
        if critical_level == 5:
            print("緊急の兆候を検知したので、これ以上の質問はスキップするよ。")
            break

    urgency = determine_urgency(total_score, critical_level)
    description = URGENCY_LABELS[urgency]

    print("\n🦉 緑のフクロウの診断: 緊急度は" f"​:codex-terminal-citation[codex-terminal-citation]{line_range_start=1 line_range_end=134 terminal_chunk_id={urgency}/5】です。")
    print(f"推奨: {description}")
    print("※これは目安です。症状が悪化したり不安があれば必ず医師に相談してください。")


if __name__ == "__main__":
    main()

