# Google Play Review Collector (Monthly Filter Version)

이 프로젝트는 **Google Play Store**에서 특정 앱의 리뷰를 수집하고,  
**실행한 날짜 기준 “지난달 1일부터 지난달 마지막 날까지” 작성된 리뷰만 자동으로 필터링하여 CSV로 저장**하는 Python 스크립트입니다.

예시:
- 2025년 12월 3일 실행 → 2025년 11월 1일 ~ 11월 30일 리뷰만 저장  
- 2026년 1월 2일 실행 → 2025년 12월 1일 ~ 12월 31일 리뷰만 저장  

자동 월 계산 방식으로, 매달 동일 스크립트를 실행해도 **항상 지난달 리뷰만 추출**합니다.

---

## 📌 Features

- Google Play 최신 리뷰 수집 (정렬: NEWEST)
- 실행일 기준 자동으로 지난달 기간 계산
- 지난달에 작성된 리뷰만 필터링
- UTF-8 BOM 인코딩으로 CSV 저장 (Excel 한글 깨짐 방지)
- 출력 파일명: `hejhome_reviews_googleplay_YYYYMM.csv`

---

## 📦 Installation

필요한 패키지를 설치합니다:

```bash
pip install google-play-scraper pandas
