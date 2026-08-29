import json

# 이전에 저장된 relay_sample.json 로드
with open("relay_sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

result = data.get("result", {})
relay_data = result.get("textRelayData", {})

print("=== textRelayData 최상위 키 목록 ===")
if isinstance(relay_data, dict):
    print(list(relay_data.keys()))
    
    # 텍스트 릴레이 리스트 탐색
    sample_list = []
    for k, v in relay_data.items():
        if isinstance(v, list) and len(v) > 0:
            print(f"\n🔑 리스트 발견: [{k}] (총 {len(v)}개 항목)")
            sample_list = v
            break

    if sample_list:
        print("\n--- 첫 번째 샘플 항목 구조 ---")
        print(json.dumps(sample_list[0], indent=2, ensure_ascii=False))
        
        # 투구/타석 세부 항목 샘플 탐색
        for item in sample_list:
            if any(term in str(item).lower() for term in ["speed", "pitch", "strike", "ball", "삼진", "안타", "직구"]):
                print("\n--- 투구/타석 상세 데이터 샘플 ---")
                print(json.dumps(item, indent=2, ensure_ascii=False))
                break