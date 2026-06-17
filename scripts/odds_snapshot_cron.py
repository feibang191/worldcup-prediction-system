"""赔率快照定时抓取 v1.0
定时任务：抓取Sporttery赔率保存到odds_snapshots表
配合盘口异动检测使用
"""
import json, sqlite3, urllib.request, ssl
from datetime import datetime

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

DB_PATH = r".\football_database.sqlite"

def capture():
    url = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchListV1.qry?clientCode=3001"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.sporttery.cn/",
        "Accept": "application/json",
    })
    resp = urllib.request.urlopen(req, timeout=10, context=ssl_context)
    data = json.loads(resp.read().decode("utf-8"))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    for biz in data.get("value", {}).get("matchInfoList", []):
        for sub in biz.get("subMatchList", []):
            h = sub.get("homeTeamAllName", "")
            a = sub.get("awayTeamAllName", "")
            mk = f"{h}VS{a}"
            row = {"win": None, "draw": None, "loss": None,
                   "hwin": None, "hdraw": None, "hloss": None, "hc": None}
            for o in sub.get("oddsList", []):
                pool = o.get("poolCode", "")
                if pool == "HHAD":
                    row["win"] = float(o.get("h", 0) or 0)
                    row["draw"] = float(o.get("d", 0) or 0)
                    row["loss"] = float(o.get("a", 0) or 0)
                elif pool == "HHAF":
                    row["hwin"] = float(o.get("h", 0) or 0)
                    row["hdraw"] = float(o.get("d", 0) or 0)
                    row["hloss"] = float(o.get("a", 0) or 0)
                    row["hc"] = float(o.get("goalLine", 0) or 0)

            conn.execute("""
                INSERT INTO odds_snapshots
                (match_key, snapshot_type, had_win, had_draw, had_loss,
                 hadn_win, hadn_draw, hadn_loss, asian_handicap, timestamp)
                VALUES (?, 'current', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mk, row["win"], row["draw"], row["loss"],
                  row["hwin"], row["hdraw"], row["hloss"], row["hc"], ts))

    conn.commit()
    conn.close()
    print(f"[{ts}] OK - 赔率快照已保存")

if __name__ == "__main__":
    capture()