"""Cold vs warm timing for POST /analyze (seeds one fake game so chess.com isn't needed)."""
import json, statistics, sys, time
import redis, requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
R = redis.from_url(sys.argv[2] if len(sys.argv) > 2 else "redis://localhost:6379")

PGN = """[Event "Test"]
[White "tester"]
[Black "opp"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Nxd5 6. Nxf7 Kxf7 7. Qf3+ Ke6 8. Nc3 Nb4 9. O-O c6 10. d4 Kd7 11. a3 Na6 12. dxe5 Nxe5 13. Bf4 Ng6 14. Bxd5 cxd5 15. Rfe1 Nxf4 16. Qxf4 Bd6 17. Qg3 Qe7 18. Nxd5 Qxe1+ 19. Rxe1 Bxg3 20. Rd1 Bxh2+ 1-0"""

summary = [{"index": 0, "opponent": "opp", "user_color": "white", "result": "win",
            "time_class": "rapid", "end_time": 0, "pgn": PGN}]
R.flushall()
R.setex("games:tester:2026:9", 7200, json.dumps(summary))

body = {"username": "tester", "year": 2026, "month": 9, "mode": "single", "index": 0}
def call():
    t = time.perf_counter()
    r = requests.post(f"{BASE}/analyze", json=body, timeout=600)
    return (time.perf_counter() - t), r.json()

cold, data = call()
res = data["results"][0]
warm = [call()[0] for _ in range(10)]
print(f"moves analysed: {len(res['moves'])}")
print(f"cold: {cold*1000:.0f} ms | warm median of 10: {statistics.median(warm)*1000:.1f} ms")
print(f"speedup: {cold/statistics.median(warm):.0f}x")
