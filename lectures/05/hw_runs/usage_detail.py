"""同じトークン数で推定費用が違った理由を調べるため、usage の内訳（キャッシュ読み出し等）を表示する。"""
import sys
from app.agent import agent, build_model
r = agent.run_sync(sys.argv[1], model=build_model())
u = r.usage
print("input", u.input_tokens, "output", u.output_tokens, "cache_read", u.cache_read_tokens, "requests", u.requests)
print("details", dict(u.details))
print("cost", u.cost)
