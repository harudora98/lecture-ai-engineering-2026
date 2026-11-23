#!/bin/bash
# 宿題（実装）: 同じ質問・同じモデルで、通常検索（AIE_RAG_NEIGHBORS=0）と前後1ページ付き（=1）を各2回 --trace 実行する。
# APIキーは環境変数 GEMINI_API_KEY から読む（ファイルには書かない）。
cd "$(dirname "$0")/../../.."
OUT=lectures/05/hw_runs
Q1='第2回の説明では、LoRAは何を固定し何を学習しますか？ QLoRAは何を加えますか？'
Q2='第1回の例題（講義中の大量の質問にAIで答える）で、問題設定からデプロイまでどう進めますか？'
Q3='MCPとは何ですか？'
i=0
for q in "$Q1" "$Q2" "$Q3"; do
  i=$((i+1))
  for rep in 1 2; do
    for nb in 0 1; do
      f="$OUT/q${i}_nb${nb}_run${rep}.txt"
      echo "[question] $q" > "$f"
      echo "[AIE_RAG_NEIGHBORS] $nb" >> "$f"
      AIE_RAG_NEIGHBORS=$nb uv run python -m app.agent --trace "$q" >> "$f" 2>&1
      echo "$f rc=$?"
      sleep 5
    done
  done
done
