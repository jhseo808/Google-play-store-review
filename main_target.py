from google_play_scraper import reviews, Sort
import pandas as pd
import traceback
from datetime import datetime, timedelta

try:
    print("리뷰 수집을 시작합니다...")

    # ---------------------------
    # 수집하고 싶은 연도/월 입력
    # ---------------------------
    target_year = 2025        # 예: 2025
    target_month = 11         # 예: 11 (11월)
    # ---------------------------

    app_package = "com.goqual"
    lang = 'ko'
    country = 'kr'

    # target 월 1일
    first_day_target = datetime(target_year, target_month, 1)

    # target 월 마지막 날 = 다음 달 1일 - 1일
    if target_month == 12:
        first_day_next = datetime(target_year + 1, 1, 1)
    else:
        first_day_next = datetime(target_year, target_month + 1, 1)

    last_day_target = first_day_next - timedelta(days=1)

    print("필터링 기간:", first_day_target, "~", last_day_target)

    # 리뷰 수집
    result, _ = reviews(
        app_package,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=1000    # 필요한 경우 늘려도 됨
    )

    df = pd.DataFrame(result)

    # 날짜 변환
    df['at'] = pd.to_datetime(df['at'])

    # 선택한 월 데이터만 필터링
    df_filtered = df[(df['at'] >= first_day_target) & (df['at'] <= last_day_target)]

    print(f"전체 수집 리뷰: {len(df)}개")
    print(f"{target_year}-{target_month} 리뷰만 필터링: {len(df_filtered)}개")

    # 필요한 컬럼만 선택
    df2 = df_filtered[['reviewId','userName','content','score','at','reviewCreatedVersion']]

    # 신규 컬럼 추가
    df2['analyze_flag'] = 0  
    df2['label'] = ""        
    df2['AI분석'] = ""       

    # 저장 파일명
    filename = f"hejhome_reviews_googleplay_{target_year}{str(target_month).zfill(2)}.csv"

    df2.to_csv(filename, index=False, encoding='utf-8-sig')
    print("저장 완료:", filename)

except Exception as e:
    print(f"오류 발생: {e}")
    traceback.print_exc()
