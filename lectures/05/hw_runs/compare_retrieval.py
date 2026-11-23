"""宿題（実装）: 通常検索と前後ページ付き検索の取得ページを並べて比べる（埋め込みAPIを1質問1回だけ使う）。"""
import sys
from app.retrieval import search, expand_neighbors

for q in sys.argv[1:]:
    hits = search(q)
    expanded = expand_neighbors(hits, window=1)
    print(f"\n### {q}")
    print(f"通常: {len(hits)}件 / 本文{sum(len(h['content']) for h in hits):,}文字")
    for h in hits:
        print(f"  {h['page_id']} d={h['distance']:.3f} {h['title'][:40]}")
    print(f"前後付き: {len(expanded)}件 / 本文{sum(len(h['content']) for h in expanded):,}文字")
    for h in expanded:
        tag = "hit " if h["retrieved_by"] == "search" else f"+nb({h['neighbor_of'][-4:]})"
        print(f"  {tag} {h['page_id']} {h['title'][:40]}")
