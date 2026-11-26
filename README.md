
# 성적 CSV 검증 프로그램

## ① What (무엇을 하는가?)

성적 CSV 파일을 읽어 유효한 점수 목록과 잘못된 데이터의 제외 사유를 반환하는 프로그램이다.

## ② Why (왜 만들었는가?)

성적 CSV 데이터를 처리할 때 빈 점수, 정수가 아닌 점수, 0~100 범위를 벗어난 점수 등이 포함되면 정확한 결과를 얻기 어렵다. 따라서 유효한 데이터만 추출하고 제외된 데이터의 원인을 확인할 수 있도록 구성하였다. 또한 0점과 100점 같은 경계값 및 예외 상황을 테스트 코드로 검증하여 프로그램을 수정하더라도 기존 기능이 정상적으로 작동하는지 확인하고자 하였다.

## ③ How (어떻게 실행하는가?)

### 필요한 라이브러리 설치

python -m pip install pytest pytest-cov

### 프로그램 실행

python load_scores.py scores.csv

## ④ 테스트 방법 및 결과

### 일반 테스트 실행

python -m pytest test_load_scores.py test_ai_A.py test_ai_B.py -q

### 커버리지 측정

python -m pytest test_load_scores.py --cov=load_scores --cov-report=term-missing

### 실제 실험 결과

- 기본 테스트: 13개 통과, 커버리지 100%
- AI A 코드 제공: 13개 통과, 커버리지 80%
- AI B 명세 제공: 13개 통과, 커버리지 100%
- 전체 일반 테스트: 39 passed in 0.67s

### 함정 실험 (별도 실행)

python -m pytest test_ai_bug.py -v

- 2 failed, 5 passed
- 마지막 원소를 검사하지 않는 논리 오류 발견
- 버그 굳힘 여부: X

## ⑤ 파일 구성

| 파일명 | 역할 |
|---|---|
| load_scores.py | 성적 CSV 검증 프로그램 |
| bug3_logic.py | 논리 오류 실험 대상 |
| scores.csv | 일반 성적 데이터 |
| empty.csv | 헤더만 존재하는 데이터 |
| weird.csv | 비정상 성적 데이터 |
| test_load_scores.py | 기본 단위 테스트 |
| test_ai_A.py | 코드 제공 방식의 AI 테스트 |
| test_ai_B.py | 명세 제공 방식의 AI 테스트 |
| test_ai_bug.py | 버그 굳힘 여부 확인 |
| README.md | 프로그램 사용 설명서 |
| LICENSE | MIT 라이선스 |
| .gitignore | Git 추적 제외 파일 설정 |

## ⑥ 만든 사람 및 AI 활용

- 만든 사람: 김윤호
- 소속: 기계공학부 1학년
- 학번: 2026100118
- 활용한 AI: ChatGPT
- AI 활용 범위: 테스트 코드 생성, 오류 분석, 문서화 지원
- 직접 수행한 내용: A/B 및 함정 실험 실행, 커버리지 측정, GitHub 저장소 생성 및 커밋과 push
- 직접 판단한 내용: 실험 결과에 대한 판단: A와 B의 통과 개수는 같았지만 B가 더 넓은 실행 범위를 검증하였다. 함정 실험에서는 잘못된 기대값을 정답으로 고정하지 않고 마지막 원소 누락 오류를 발견하였다. 따라서 테스트 통과 개수뿐 아니라 경계값과 기대값의 타당성도 확인하는 것이 중요하다.

## License

MIT License (LICENSE 파일 참조)