from google_play_scraper import reviews, Sort
import pandas as pd
import traceback
from datetime import datetime, timedelta

try:
    print("리뷰 수집을 시작합니다...")
    app_package = "com.goqual"
    lang = 'ko'
    country = 'kr'

    # 오늘 날짜 기준
    today = datetime.now()

    # 이번 달 1일
    first_day_this_month = today.replace(day=1)

    # 지난달 마지막 날
    last_day_prev_month = first_day_this_month - timedelta(days=1)

    # 지난달 1일
    first_day_prev_month = last_day_prev_month.replace(day=1)

    print("필터링 기간:", first_day_prev_month, "~", last_day_prev_month)

    # 리뷰 수집 (지난달 리뷰가 충분히 포함되도록 넉넉히 수집)
    result, _ = reviews(
        app_package,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=800    # 필요한 경우 1000 이상도 가능
    )

    df = pd.DataFrame(result)

    # 날짜 변환
    df['at'] = pd.to_datetime(df['at'])

    # 지난달 데이터만 필터링
    df_filtered = df[(df['at'] >= first_day_prev_month) & (df['at'] <= last_day_prev_month)]

    print(f"전체 수집 리뷰: {len(df)}개")
    print(f"지난달 리뷰만 필터링: {len(df_filtered)}개")

    # 필요한 컬럼만 선택
    df2 = df_filtered[['reviewId','userName','content','score','at','reviewCreatedVersion']]

    # 저장 파일명
    filename = f"hejhome_reviews_googleplay_{first_day_prev_month.strftime('%Y%m')}.csv"

    df2.to_csv(filename, index=False, encoding='utf-8-sig')
    print("저장 완료:", filename)

except Exception as e:
    print(f"오류 발생: {e}")
    traceback.print_exc()
