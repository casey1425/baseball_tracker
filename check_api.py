import json

with open("relay_sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

result = data.get("result", {})
relay_data = result.get("textRelayData", {})

print("=== 라인업 데이터 탐색 ===")
home_lineup = relay_data.get("homeLineup", {})
away_lineup = relay_data.get("awayLineup", {})

print(f"홈 라인업 키: {list(home_lineup.keys()) if isinstance(home_lineup, dict) else type(home_lineup)}")
print(f"원정 라인업 키: {list(away_lineup.keys()) if isinstance(away_lineup, dict) else type(away_lineup)}")

# 타자 / 투수 샘플 출력
if isinstance(home_lineup, dict):
    batters = home_lineup.get("batter", [])
    pitchers = home_lineup.get("pitcher", [])
    
    if batters:
        print("\n[타자 데이터 샘플 (홈팀 1번타자)]")
        print(json.dumps(batters[0], indent=2, ensure_ascii=False))
        
    if pitchers:
        print("\n[투수 데이터 샘플 (홈팀 선발투수)]")
        print(json.dumps(pitchers[0], indent=2, ensure_ascii=False))