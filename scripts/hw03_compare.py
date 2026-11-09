"""第3回 宿題（基礎）: INSTRUCTIONS / docstring を1か所ずつ変えて、同じ質問の --trace を比べる。

使い方（リポジトリ直下、GEMINI_API_KEY 設定済みで）:
    uv run python scripts/hw03_compare.py > hw03_results.txt

app/ のファイルは書き換えず、変種ごとにエージェントを組み立て直す
（agent.py の INSTRUCTIONS / tools.py の docstring を手で書き換えるのと同じ効果）。
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # リポジトリ直下を import 対象に

from pydantic_ai import Agent, Tool

from app import tools
from app.agent import INSTRUCTIONS, build_model, print_trace

SEARCH_LINE = "- 用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。\n"
DOC_ONE = "query には調べたい用語を1つだけ入れる（例: \"LoRA\"）。"
DOC_MANY = "query には調べたい用語をまとめて入れる（例: \"LoRA QLoRA\"）。"

VARIANTS = {
    "A_baseline": (INSTRUCTIONS, tools.search_glossary.__doc__),
    "B_no_search_rule": (INSTRUCTIONS.replace(SEARCH_LINE, ""), tools.search_glossary.__doc__),
    "C_doc_batch_terms": (INSTRUCTIONS, tools.search_glossary.__doc__.replace(DOC_ONE, DOC_MANY)),
}

QUESTIONS = [
    "LoRAとQLoRAの違いは？",
    "AIE2026の講座で使う「lecNN-start タグ」とは何ですか？",
]


def build(instructions: str, search_doc: str) -> Agent:
    agent = Agent(instructions=instructions)
    agent.tool_plain(tools.search_glossary, description=search_doc)
    agent.tool_plain(tools.get_lecture_summary)
    return agent


def main() -> None:
    model = build_model()
    for name, (instr, doc) in VARIANTS.items():
        assert instr != INSTRUCTIONS or doc != tools.search_glossary.__doc__ or name.startswith("A")
        agent = build(instr, doc)
        for q in QUESTIONS:
            print(f"\n===== {name} | Q: {q} =====")
            result = agent.run_sync(q, model=model)
            print(result.output)
            print_trace(result)
            time.sleep(8)  # 無料枠のレート制限対策


if __name__ == "__main__":
    main()
