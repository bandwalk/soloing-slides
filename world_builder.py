# -*- coding: utf-8 -*-
import json
import sys
import os
import requests
import random
from pathlib import Path

def generate_random_world(genre=None, keyword=None):
    """
    Gemini API를 활용하여 정형화된 가이드형 세계관 JSON 데이터를 자율 생성합니다.
    """
    # 템플릿 장르 정의
    genres = ["아포칼립스 생존", "중세 다크 판타지", "사이버 범죄 스릴러", "스페이스 오페라", "동양 무협"]
    selected_genre = genre or random.choice(genres)
    
    keywords_dict = {
        "아포칼립스 생존": ["버려진 지하철 궤도", "통제 불능의 침수된 방주", "방사능 피난처"],
        "중세 다크 판타지": ["피가 스며든 고문실", "안개 낀 망령의 고성", "부서진 불꽃의 예배당"],
        "사이버 범죄 스릴러": ["네온사인 뒤편의 고물상", "익명의 다크웹 서버실", "불법 임플란트 수술실"],
        "스페이스 오페라": ["추락 중인 공중 전함의 브리지", "소행성 광산의 산소 공급소", "정체불명의 에일리언 번식처"],
        "동양 무협": ["은둔한 천살성의 죽림", "화산파의 버려진 비급 연마굴", "피로 물든 객잔의 지하 밀실"]
    }
    
    possible_keywords = keywords_dict.get(selected_genre, ["알 수 없는 암흑의 밀실"])
    selected_keyword = keyword or random.choice(possible_keywords)

    print(f"장르: {selected_genre} | 키워드: {selected_keyword} 기반 세계관 빌딩 개시...")

    # 구조화된 JSON 생성을 위한 시스템 프롬프트 정의
    prompt = f"""
    당신은 세계관 빌더 엔진입니다. 다음 조건에 정합하는 텍스트 RPG 세계관 스펙을 정밀한 JSON 포맷으로 단독 출력하십시오.
    
    장르: {selected_genre}
    키워드: {selected_keyword}

    출력할 JSON 스키마 구조:
    {{
        "world_name": "세계관 명칭",
        "description": "세계관의 전체 서사적 배경 묘사 (소설체 2~3줄)",
        "stats": [
            {{
                "name": "스탯 이름 (영어)",
                "label": "스탯 한글명",
                "initial_value": 100,
                "description": "해당 스탯이 나타내는 물리/정서적 의미"
            }}
        ],
        "nodes": [
            {{
                "id": "node_1",
                "name": "시작 구역 명칭",
                "description": "이 공간에 대한 정밀한 묘사",
                "available_actions": [
                    "행동 선택지 1",
                    "행동 선택지 2",
                    "행동 선택지 3"
                ]
            }}
        ]
    }}

    주의: 오직 순수한 JSON 문자열만 반환해야 하며, 마크다운 코드 블록(```json)이나 다른 설명 텍스트를 절대로 섞지 마십시오.
    """

    api_success = False
    world_data = None
    api_key = None

    # 대표이사 파울로의 API Key 대피 검색 (Hermes config.yaml 파싱)
    try:
        import yaml
        with open(os.path.expanduser("~/.hermes/config.yaml"), "r") as f:
            cfg = yaml.safe_load(f)
            api_key = cfg.get("credentials", {}).get("gemini", {}).get("api_key")
    except Exception as e:
        pass

    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                # json 파싱 시도전 마크다운 백틱 제거
                if raw_text.startswith("```"):
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                world_data = json.loads(raw_text)
                api_success = True
                print("Gemini API를 통해 실시간으로 세계관을 성공적으로 창조했습니다.")
        except Exception as e:
            print(f"API 호출 중 예외 발생: {e}. 백업 로컬 모킹 엔진을 기동합니다.")

    if not api_success:
        print("[Honest Alert] 외부 API 연결 불가 또는 키 누락으로 인해, 로컬 룰 베이스 모킹 생성기로 전환하여 세계관을 빌딩합니다.")
        
        # 장르별 정교한 수동 생성 로직
        if selected_genre == "아포칼립스 생존":
            world_data = {
                "world_name": "침수된 강남역 지하방주",
                "description": "2030년 세계 대홍수 이후 지하철 궤도를 막아 만든 가상의 지하 방주. 탁한 오수와 생존자들의 거친 숨소리만이 녹슨 전철 안에 가득합니다.",
                "stats": [
                    {"name": "hp", "label": "생존력", "initial_value": 100, "description": "물리적인 신체 무결성 지표"},
                    {"name": "oxygen", "label": "산소농도", "initial_value": 75, "description": "지하 방주 내 잔여 산소 수치"},
                    {"name": "rations", "label": "전투식량", "initial_value": 30, "description": "남아있는 비상 보급 캔의 수량"}
                ],
                "nodes": [
                    {
                        "id": "node_1",
                        "name": "2호선 환승 통로 초소",
                        "description": "빗물이 천장 금 사이로 뚝뚝 떨어지는 초소 앞. 녹슨 드럼통 속 불빛 하나가 유일한 온기입니다. 저 멀리 침수된 궤도 끝에서 정체 모를 수중 괴물의 마찰음이 들려옵니다.",
                        "available_actions": [
                            "🔋 드럼통 주변의 철조망을 수색해 부러진 배터리를 회수한다",
                            "🔇 소리를 죽이고 물이 들어찬 전철 밑 공간으로 무소음 은신한다",
                            "📻 무전기 다이얼을 돌려 다른 구역 초소에 지원 요청을 타전한다"
                        ]
                    }
                ]
            }
        elif selected_genre == "중세 다크 판타지":
            world_data = {
                "world_name": "망령이 깃든 안개의 성채",
                "description": "오래전 신성한 왕국이 무너진 자리, 영원히 걷히지 않는 보랏빛 안개 속에 갇힌 유적지. 성벽 틈새로 죽은 자들의 흐느낌이 바람을 타고 스며듭니다.",
                "stats": [
                    {"name": "health", "label": "생명력", "initial_value": 100, "description": "육체의 생존 지표"},
                    {"name": "sanity", "label": "정신 오염도", "initial_value": 90, "description": "안개 속에서 심연에 오염되지 않은 저항력"},
                    {"name": "blood", "label": "핏빛 가루", "initial_value": 15, "description": "망령을 물리쳐 수집한 마법의 정수"}
                ],
                "nodes": [
                    {
                        "id": "node_1",
                        "name": "부서진 피의 예배당",
                        "description": "부서진 스테인드글라스 사이로 차가운 달빛만 쏟아지는 예배당 중앙. 녹아내린 붉은 촛농 아래로 부러진 성검의 파편이 흩어져 있습니다.",
                        "available_actions": [
                            "🗡️ 부러진 성검의 파편에 손을 얹고 정화를 기도한다",
                            "👀 가고일 석상 뒤에 몸을 숨기고 주변의 기운을 탐색한다",
                            "🍷 제단 위에 남겨진 마법 물약의 흔적을 수집한다"
                        ]
                    }
                ]
            }
        else:
            world_data = {
                "world_name": f"{selected_genre} - {selected_keyword}",
                "description": f"어둠과 서사가 정밀하게 녹아든 {selected_keyword}의 한복판. 오직 살아남는 자만이 이 거대한 세계관의 다음 챕터를 쓸 수 있습니다.",
                "stats": [
                    {"name": "hp", "label": "생존력", "initial_value": 100, "description": "기본 생존 수치"},
                    {"name": "credits", "label": "조조재산", "initial_value": 50, "description": "플랫폼 통용 재화 수치"}
                ],
                "nodes": [
                    {
                        "id": "node_1",
                        "name": f"진입 진형: {selected_keyword}",
                        "description": "공기가 무겁고 차갑게 가라앉아 소리마저 삼켜지는 정적의 구역. 당신의 발자국 소리가 유일한 소음입니다.",
                        "available_actions": [
                            "🔍 주변의 선반과 쓰레기 더미를 정밀 수색한다",
                            "🏃 소리를 내며 다음 통로를 향해 전방 돌파를 시도한다",
                            "🚪 잠긴 아치형 철문을 크랙하기 위해 해킹 툴을 시도한다"
                        ]
                    }
                ]
            }

    # 결과 파일 저장
    output_path = Path("/Users/bandwalk/soloing-slides/random_world_config.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(world_data, f, indent=4, ensure_ascii=False)
    print(f"세계관 배포 완료: {output_path}")
    return world_data

if __name__ == "__main__":
    generate_random_world()
