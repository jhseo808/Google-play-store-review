from google_play_scraper import reviews, Sort
import pandas as pd
import traceback
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import json

# GPT API 설정 (반드시 본인 API 키로 변경)
client = OpenAI(api_key="YOUR_API_KEY")

# ---------------------------------------------
# GPT 프롬프트 템플릿 (label 10개 카테고리 + 자동 개선 제안 포함)
# ---------------------------------------------
PROMPT_TEMPLATE = """
다음 사용자의 리뷰를 분석해줘.

[리뷰 내용]
{content}

아래 5가지를 JSON 형태로만 답변해:

1. label: 아래 10개 카테고리 중 가장 적합한 하나로 분류  
   ["버그", "불만", "호평", "UI/UX", "속도", "기능요청", "설치문제", "보안", "기기연결", "기타"]

2. sentiment: 리뷰의 감성 (긍정 / 부정 / 중립)

3. analysis: 리뷰 핵심 요약 (1~2줄)

4. root_cause: 사용자가 겪은 문제의 근본 원인 추정

5. improvement: 회사가 개선해야 할 구체적 제안 (1줄)

반드시 JSON 형식:
{"label": "...", "sentiment": "...", "analysis": "...", "root_cause": "...", "improvement": "..."}
"""


# ---------------------------------------------
# GPT 분석 함수 (멀티스레딩을 위해 별도 함수로 분리)
# ---------------------------------------------
def analyze_review(row):
    idx, content = row

    prompt = PROMPT_TEMPLATE.format(content=content)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.choices[0].message["content"]
        parsed = json.loads(result_text)

        return {
            "label": parsed.get("label", ""),
            "sentiment": parsed.get("sentiment", ""),
            "analysis": parsed.get("analysis", ""),
            "root_cause": parsed.get("root_cause", ""),
            "improvement": parsed.get("improvement", "")
        }

    except Exception as e:
        print(f"GPT 분석 실패(idx={idx}):", e)
        return {
            "label": "error",
            "sentiment": "",
            "analysis": "GPT 분석 실패",
            "root_cause": "",
            "improvement": ""
        }


# ---------------------------------------------
# 메인 코드
# ---------------------------------------------
try:
    print("리뷰 수집을 시작합니다...")
    app_package = "com.goqual"
    lang = 'ko'
    country = 'kr'

    # 날짜 기준
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    print("필터링 기간:", first_day_prev_month, "~", last_day_prev_month)

    # 리뷰 수집
    result, _ = reviews(
        app_package,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=800
    )

    df = pd.DataFrame(result)
    df['at'] = pd.to_datetime(df['at'])

    # 날짜 필터링
    df_filtered = df[(df['at'] >= first_day_prev_month) & (df['at'] <= last_day_prev_month)]

    print(f"전체 리뷰: {len(df)} / 지난달 리뷰: {len(df_filtered)}")

    # 분석용 DataFrame 구성
    df2 = df_filtered[['reviewId', 'userName', 'content', 'score', 'at', 'reviewCreatedVersion']]

    # 추가 컬럼
    df2['analyze_flag'] = 0
    df2['label'] = ""
    df2['sentiment'] = ""
    df2['AI분석'] = ""
    df2['root_cause'] = ""
    df2['improvement'] = ""

    # ---------------------------------------------
    # 분석 조건 필터링 (아주 중요)
    # ---------------------------------------------
    df_target = df2[
        (df2['analyze_flag'] == 1) &        # 사용자가 분석 허용한 리뷰
        (df2['score'].isin([1, 2])) &        # 점수 1~2점
        (df2['content'].str.len() >= 20)     # 리뷰 길이 20자 이상
    ]

    print(f"분석 대상 리뷰 수: {len(df_target)}")

    # ---------------------------------------------
    # 멀티스레딩으로 GPT 분석 (속도 3~5배 향상)
    # ---------------------------------------------
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = executor.map(analyze_review, df_target[['content']].itertuples())

    # 결과 업데이트
    for (idx, row), result in zip(df_target.iterrows(), futures):
        df2.at[idx, "label"] = result["label"]
        df2.at[idx, "sentiment"] = result["sentiment"]
        df2.at[idx, "AI분석"] = result["analysis"]
        df2.at[idx, "root_cause"] = result["root_cause"]
        df2.at[idx, "improvement"] = result["improvement"]


    # ---------------------------------------------
    # 결과 파일 저장
    # ---------------------------------------------
    filename = f"hejhome_reviews_googleplay_{first_day_prev_month.strftime('%Y%m')}_ANALYZED.csv"
    df2.to_csv(filename, index=False, encoding='utf-8-sig')

    print("\n분석 완료!")
    print("저장 파일:", filename)

except Exception as e:
    print("오류 발생:", e)
    traceback.print_exc()
