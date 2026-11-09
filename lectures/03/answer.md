# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
- `--trace` で見えたツール呼び出し（ツール名と引数）：
- 1つの質問での LLM 呼び出し回数（`requests`）：
- 追加したツールと、docstring に書いた説明：

## 宿題

- 取り組んだレベル：基礎
- やったこと：
  - `app/agent.py` の INSTRUCTIONS と `app/tools.py` の `search_glossary` の docstring を **1か所ずつ** 変え、同じ2つの質問を trace 付きで実行して比べた（モデル: gemini-3.5-flash-lite）。
  - 変えたものは次の3パターン（実行用スクリプト: `scripts/hw03_compare.py`、実行ログ: `lectures/03/hw03_results.txt`。`app/` を手で書き換えるのと同じ内容のエージェントを組み立て直して実行）。
    - A ベースライン：変更なし
    - B INSTRUCTIONS から「必ず search_glossary で用語集を確認する」の行を削除
    - C docstring の「query には調べたい用語を1つだけ入れる（例: "LoRA"）」を「まとめて入れる（例: "LoRA QLoRA"）」に変更
  - 質問：Q1「LoRAとQLoRAの違いは？」／Q2「AIE2026の講座で使う「lecNN-start タグ」とは何ですか？」
- 結果：

| パターン | 質問 | ツール呼び出し（引数） | tool_calls | requests | input_tokens |
|---|---|---|---|---|---|
| A ベースライン | Q1 | `search_glossary("LoRA")`, `search_glossary("QLoRA")` | 2 | 2 | 1198 |
| A ベースライン | Q2 | `search_glossary("lecNN-start タグ")` | 1 | 2 | 785 |
| B 検索ルール削除 | Q1 | `search_glossary("LoRA")`, `search_glossary("QLoRA")` | 2 | 2 | 1150 |
| B 検索ルール削除 | Q2 | `search_glossary("lecNN-start タグ")` | 1 | 2 | 737 |
| C docstring「まとめて」 | Q1 | `search_glossary("LoRA QLoRA")` | **1** | 2 | **893** |
| C docstring「まとめて」 | Q2 | `search_glossary("lecNN-start タグ")` | 1 | 2 | 787 |

  - B：検索ルールの行を消しても、**どちらの質問でも検索してから答えた**。回答の内容もほぼ同じで、最後に関係する回（Q1は第2回、Q2は第1回）も付いていた。入力トークンが約50減ったのは、INSTRUCTIONS が1行短くなった分。
  - C：Q1 で検索が **2回から1回** に減り、引数が `"LoRA QLoRA"` になった。`search_glossary` は空白を除いて正規化し、部分一致（名前が3文字以上で、検索語に含まれるもの）も拾うので、`"loraqlora"` から LoRA と QLoRA の両方が見つかり、回答の質は変わらなかった。入力トークンは 1198 から 893 に減った（ツールの結果を2回分モデルに戻さなくて済むため）。Q2 はもともと用語が1つなので変化なし。
  - どのパターンでも requests は2（ツールを呼ぶ回 + 回答を作る回）。A の Q1 は2つの検索を1回のリクエストで並列に呼んでいた。
- 気づき・疑問：
  - INSTRUCTIONS の「必ず検索する」を消しても検索したのは、docstring にも「答える前に使うこと」と書いてあるからだと思う。指示は INSTRUCTIONS とツールの説明文の両方からモデルに届いていて、片方だけ消しても効かないことがある。本当に効き目を確かめるなら、docstring 側の文も消して比べる必要がある。
  - docstring の1文で、引数の作り方と呼び出し回数がはっきり変わった。docstring は「ツールの説明」であると同時に「使い方の指示」として働いている。
  - 「まとめて入れる」がうまくいったのは、今回は検索語同士が部分一致する（LoRA ⊂ QLoRA）ためだと思う。たとえば「RAG と LoRA」のように関係のない用語をまとめると、`MAX_RESULTS=3` や部分一致の条件で取りこぼすかもしれない。ツールの実装と docstring を合わせておかないと、回数は減っても正確さが落ちる恐れがある（未検証）。
  - 1回ずつしか実行していないので、結果がたまたまだった可能性がある。同じ設定で何回か実行して、ばらつきも見るとよい。
