# AWS Bedrock 경량 모델 비교 테스트

AWS Bedrock에서 제공하는 5개 경량 LLM 모델을 동일한 프롬프트로 호출하여 응답 속도, 토큰 사용량, 비용, 응답 품질을 종합 비교하는 도구입니다.
Complex Reasoning 테스트에 대해서는 Claude Opus 4.6이 각 모델의 응답 품질을 자동 평가합니다.

---

## 비교 대상 모델

| 모델 | Model ID | 파라미터 | Provider |
|------|----------|----------|----------|
| Claude Haiku 4.5 | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | - | Anthropic |
| Qwen 3 32B | `qwen.qwen3-32b-v1:0` | 32B | Alibaba |
| Nova 2 Lite | `us.amazon.nova-2-lite-v1:0` | - | Amazon |
| Llama 3.2 11B | `us.meta.llama3-2-11b-instruct-v1:0` | 11B | Meta |
| Ministral 8B | `mistral.ministral-3-8b-instruct` | 8B | Mistral |

> 일부 모델은 inference profile ID(`us.` prefix)를 사용합니다.

---

## 모델 가격 (1M 토큰 기준, 2026-02 기준)

| 모델 | 입력 (USD) | 출력 (USD) |
|------|-----------|-----------|
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Qwen 3 32B | $0.15 | $0.60 |
| Nova 2 Lite | $0.30 | $2.50 |
| Llama 3.2 11B | $0.16 | $0.16 |
| Ministral 8B | $0.15 | $0.15 |

---

## 테스트 케이스 (5종)

| # | 테스트명 | 유형 | 프롬프트 언어 | 설명 |
|---|---------|------|-------------|------|
| 1 | Complex Reasoning | 복합 추론 | 한국어 | 3개 대륙 분산 실시간 협업 플랫폼 아키텍처 설계 |
| 2 | Advanced Code Generation | 코드 생성 | 한국어 | TTL/메모리제한/Thread-safe LRU 캐시 Python 구현 |
| 3 | Multi-dimensional Analysis | 다각도 분석 | 한국어 | AI 스타트업 B2B SaaS 전환 시나리오 분석 |
| 4 | Technical Translation | 기술 번역 (한→영) | 한국어 | CAP 정리·이벤트 소싱·CQRS 관련 기술 문서 영역 |
| 5 | Technical Translation EN-KO | 기술 번역 (영→한) | 영어 | 클라우드 네이티브 Observability(메트릭·로그·트레이스) 기술 문서 한역 |

---

## 실행 방법

### 사전 요구사항

```bash
pip3 install boto3
```

- Python 3.9+
- AWS 자격 증명 설정 (`~/.aws/credentials` 또는 IAM Role)
- 필요 IAM 권한: `bedrock:InvokeModel` (us-east-1 리전)
- Opus 4.6 품질 평가를 위해 `us.anthropic.claude-opus-4-6-v1` 모델 접근 권한 필요

### 실행

```bash
cd Lite-model-test
python3 bedrock_model_comparison.py
```

### 실행 흐름

```
main()
  ├─ 5개 테스트 순차 실행 (테스트 간 1초 대기)
  │   ├─ Complex Reasoning
  │   ├─ Advanced Code Generation
  │   ├─ Multi-dimensional Analysis
  │   ├─ Technical Translation (한→영)
  │   └─ Technical Translation EN-KO (영→한)
  ├─ Complex Reasoning 결과 → Opus 4.6 품질 평가 (evaluate_quality)
  ├─ complex_reasoning_results.json 별도 저장 (save_test_detail)
  ├─ print_summary() — 전체 요약 콘솔 출력
  └─ save_results() — comparison_results.json 저장
```

---

## 출력 파일

### `comparison_results.json` — 전체 테스트 결과

5개 테스트 전체의 성능 지표와 순위를 포함합니다.

```
{
  "meta": { "title", "date", "region", "max_tokens", "total_tests" },
  "models": { <모델별 ID·가격 정보> },
  "tests": [
    {
      "test_name": "...",
      "results": {
        "<model_key>": { "latency_s", "input_tokens", "output_tokens", "cost_usd", "response_chars" }
      },
      "rankings": { "fastest", "cheapest" }
    }
  ],
  "summary": {
    "average_per_model": { "<model_key>": { "avg_latency_s", "total_cost_usd", "avg_tokens" } },
    "rankings": { "by_latency": [...], "by_cost": [...] }
  }
}
```

### `complex_reasoning_results.json` — Complex Reasoning 상세 결과 + 품질 평가

Complex Reasoning 테스트의 모델별 응답 전문과 Opus 4.6의 품질 평가를 포함합니다.

```
{
  "test_name": "Complex Reasoning",
  "prompt": "...",
  "models": {
    "<model_key>": {
      "model_name": "...",
      "metrics": { "latency_s", "input_tokens", "output_tokens", "total_tokens", "cost_usd" },
      "response": "<응답 전문>",
      "quality_evaluation": {
        "accuracy": <1-10>,
        "specificity": <1-10>,
        "structure": <1-10>,
        "practicality": <1-10>,
        "comment": "<Opus 4.6 한줄 코멘트>"
      }
    }
  },
  "timestamp": "..."
}
```

---

## 측정 항목

### 성능 지표 (자동 수집)
- **Latency**: 모델 호출~응답 완료까지 소요 시간 (초)
- **Input Tokens / Output Tokens**: 입력·출력 토큰 수
- **Cost**: 토큰 수 x 모델별 단가로 산출한 비용 (USD)
- **Response Length**: 응답 텍스트 길이 (문자 수)

### 품질 평가 (Opus 4.6 자동 채점, Complex Reasoning만 적용)
- **정확성 (Accuracy)**: 사실 관계 및 기술적 정확성 (1~10)
- **구체성 (Specificity)**: 구체적 예시, 수치, 구현 디테일 포함 정도 (1~10)
- **구조화 (Structure)**: 논리적 구성, 가독성, 체계적 전개 (1~10)
- **실용성 (Practicality)**: 실무에서 바로 적용 가능한 정도 (1~10)
- **코멘트 (Comment)**: 강점과 약점을 요약한 한줄 평가

---

## 최근 테스트 결과 (2026-02-17, 5회 반복 평균, max_tokens=4096)

> 동일 조건으로 5회 반복 실행한 결과의 평균값입니다. 표준편차(±)를 함께 표기하여 결과의 안정성을 보여줍니다.

### 속도 순위 (5개 테스트 × 5회 반복 평균)

| 순위 | 모델 | 평균 Latency | 표준편차 | 평균 토큰 |
|------|------|-------------|---------|----------|
| 1 | Ministral 8B | 8.23s | ±0.58s | 2,246 |
| 2 | Nova 2 Lite | 12.14s | ±0.76s | 2,043 |
| 3 | Qwen 3 32B | 14.35s | ±1.36s | 1,651 |
| 4 | Claude Haiku 4.5 | 17.30s | ±0.57s | 2,933 |
| 5 | Llama 3.2 11B | 24.36s | ±0.77s | 4,285 |

### 비용 순위 (5개 테스트 총합, 5회 반복 평균)

| 순위 | 모델 | 평균 총 비용 | 최소 | 최대 |
|------|------|------------|------|------|
| 1 | Ministral 8B | $0.001685 | $0.001566 | $0.001847 |
| 2 | Llama 3.2 11B | $0.003428 | $0.003428 | $0.003428 |
| 3 | Qwen 3 32B | $0.004463 | $0.003950 | $0.004738 |
| 4 | Nova 2 Lite | $0.023034 | $0.022016 | $0.025318 |
| 5 | Claude Haiku 4.5 | $0.067487 | $0.066871 | $0.067871 |

### Complex Reasoning 품질 평가 (Opus 4.6 채점, 5회 반복 평균)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 | 공통 약점 요약 |
|------|--------|--------|--------|--------|------|------------|
| Ministral 8B | 6.8 | 7.2 | 9.0 | 6.2 | **7.3** | 체계적 구조 우수, SLA 계산·RTO/RPO 명시 부족, 다중 클라우드 비용 고려 미흡 |
| Qwen 3 32B | 7.0 | 6.2 | 9.0 | 6.2 | **7.1** | 가독성 높은 구조, 장애 복구·레이턴시 정량 분석·CRDT/OT 알고리즘 누락 |
| Claude Haiku 4.5 | 6.8 | 7.8 | 7.8 | 5.8 | **7.0** | 코드 예시 풍부, 응답 잘림으로 레거시 통합 등 후반 항목 누락 |
| Nova 2 Lite | 6.4 | 6.6 | 8.6 | 6.0 | **6.9** | 체계적이나 지역명 오기·부정확한 용어, 크로스리전 트레이드오프 분석 미흡 |
| Llama 3.2 11B | 3.8 | 2.8 | 2.2 | 2.8 | **2.9** | 피상적 내용, 동일 내용 반복·링크 스팸 등 심각한 생성 오류 |

> Haiku 4.5와 Llama 3.2 11B는 Complex Reasoning에서 매회 4096 토큰 한도에 도달하여 응답이 잘렸습니다 (5/5회). Ministral 8B는 Analysis에서 4/5회 한도 도달. Qwen 3 32B와 Nova 2 Lite는 전 테스트에서 자연 종료.

### 테스트별 상세 결과 (5회 반복 평균)

#### 1. Complex Reasoning (복합 추론 — 글로벌 협업 플랫폼 아키텍처 설계)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 12.75s (±2.44) | 3,407 | 8,786자 | $0.000537 | 자연 종료 |
| Nova 2 Lite | 13.48s (±3.43) | 2,008 | 4,087자 | $0.005084 | 자연 종료 |
| Qwen 3 32B | 23.96s (±1.70) | 2,154 | 4,608자 | $0.001324 | 자연 종료 |
| Llama 3.2 11B | 24.01s (±0.77) | 4,096 | 10,169자 | $0.000683 | **한도 도달 5/5회** |
| Claude Haiku 4.5 | 26.64s (±2.43) | 4,096 | 10,192자 | $0.020767 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (12.75s)
- **최저 비용**: Ministral 8B ($0.000537)
- **최고 품질**: Ministral 8B (Opus 4.6 5회 평균 7.3점)
- Haiku와 Llama는 매회 4096 한도 도달, 나머지는 전회 자연 종료

#### 2. Advanced Code Generation (코드 생성 — LRU 캐시 Python 구현)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 8.83s (±0.52) | 2,104 | 7,346자 | $0.000337 | 자연 종료 |
| Nova 2 Lite | 15.47s (±2.75) | 2,670 | 8,861자 | $0.006729 | 자연 종료 |
| Qwen 3 32B | 16.21s (±4.64) | 1,913 | 6,357자 | $0.001172 | 자연 종료 |
| Claude Haiku 4.5 | 19.72s (±0.59) | 4,096 | 10,625자 | $0.020712 | **한도 도달 5/5회** |
| Llama 3.2 11B | 24.07s (±1.00) | 4,096 | 9,584자 | $0.000678 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (8.83s)
- **최저 비용**: Ministral 8B ($0.000337)
- Haiku 4.5와 Llama만 매회 4096 한도 도달, 나머지는 자연 종료

#### 3. Multi-dimensional Analysis (다각도 분석 — B2B SaaS 전환)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 15.39s (±1.64) | 3,944 | 8,049자 | $0.000628 | **한도 도달 4/5회** |
| Nova 2 Lite | 21.49s (±3.30) | 3,207 | 5,935자 | $0.008106 | 자연 종료 |
| Llama 3.2 11B | 24.05s (±1.20) | 4,096 | 6,564자 | $0.000696 | **한도 도달 5/5회** |
| Qwen 3 32B | 26.80s (±3.20) | 2,620 | 4,484자 | $0.001615 | 자연 종료 |
| Claude Haiku 4.5 | 31.83s (±1.15) | 4,096 | 5,000자 | $0.020871 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (15.39s)
- **최저 비용**: Ministral 8B ($0.000628)
- 3개 모델(Haiku, Llama, Ministral)이 높은 빈도로 한도 도달 — 분석 태스크는 토큰 소모가 큼

#### 4. Technical Translation 한→영 (CAP 정리 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 1.07s (±0.10) | 105 | 593자 | $0.000098 | 자연 종료 |
| Ministral 8B | 1.50s (±0.26) | 244 | 1,139자 | $0.000067 | 자연 종료 |
| Claude Haiku 4.5 | 3.40s (±0.64) | 283 | 999자 | $0.001755 | 자연 종료 |
| Nova 2 Lite | 5.29s (±3.61) | 533 | 1,949자 | $0.001404 | 자연 종료 |
| Llama 3.2 11B | 23.94s (±0.34) | 4,096 | 8,907자 | $0.000688 | **한도 도달 5/5회** |

- **최고 속도**: Qwen 3 32B (1.07s)
- **최저 비용**: Ministral 8B ($0.000067)
- 번역 태스크는 대부분 모델이 짧은 출력으로 자연 종료
- Llama 3.2만 매회 4096 한도 도달 — 번역 후 불필요한 부연 설명을 대량 생성

#### 5. Technical Translation EN-KO 영→한 (Observability 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 2.70s (±0.74) | 593 | 1,224자 | $0.000116 | 자연 종료 |
| Qwen 3 32B | 3.70s (±0.18) | 377 | 641자 | $0.000254 | 자연 종료 |
| Claude Haiku 4.5 | 4.94s (±0.70) | 634 | 717자 | $0.003382 | 자연 종료 |
| Nova 2 Lite | 5.00s (±1.86) | 658 | 1,368자 | $0.001710 | 자연 종료 |
| Llama 3.2 11B | 25.73s (±3.24) | 4,096 | 10,440자 | $0.000683 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (2.70s)
- **최저 비용**: Ministral 8B ($0.000116)
- Llama 3.2만 매회 한도 도달 (10,440자 중 대부분이 번역 외 부가 콘텐츠)

### 처리량 분석 (출력 토큰/초, 5회 반복 평균)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | 평균 |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | 269.5 | 239.0 | 258.1 | 160.4 | 218.2 | **229.0** |
| Llama 3.2 11B | 170.7 | 170.4 | 170.6 | 171.2 | 161.0 | **168.8** |
| Nova 2 Lite | 148.5 | 173.0 | 149.0 | 127.1 | 130.3 | **145.6** |
| Claude Haiku 4.5 | 154.8 | 207.9 | 128.8 | 84.9 | 129.1 | **141.1** |
| Qwen 3 32B | 89.8 | 123.4 | 98.0 | 98.2 | 102.1 | **102.3** |

- **Ministral 8B**이 전 테스트에서 가장 높은 처리량 (평균 229.0 tok/s)
- **Qwen 3 32B**는 파라미터가 큰 만큼 처리량이 가장 낮음 (평균 102.3 tok/s)

### 비용 효율성 분석 (품질점/달러, Complex Reasoning 5회 평균 기준)

| 모델 | 평균 비용 | 품질 평균 | 점수/$ |
|------|----------|----------|--------|
| Ministral 8B | $0.000537 | 7.3 | **13,594** |
| Qwen 3 32B | $0.001324 | 7.1 | **5,362** |
| Llama 3.2 11B | $0.000683 | 2.9 | 4,246 |
| Nova 2 Lite | $0.005084 | 6.9 | 1,357 |
| Claude Haiku 4.5 | $0.020767 | 7.0 | 337 |

- **Ministral 8B**가 달러당 품질점에서 압도적 1위 (2위 대비 2.5배)
- **Qwen 3 32B**가 2위, 비용 대비 품질 균형이 우수
- **Nova 2 Lite**는 출력 단가($2.50/1M)로 인해 비용 효율 4위
- **Haiku 4.5**는 품질 자체는 상위권이나 출력 단가($5/1M)가 높아 효율 최하위

### 테스트 유형별 우승 모델

| 기준 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| 최고 속도 | Ministral 8B | Ministral 8B | Ministral 8B | Qwen 3 32B | Ministral 8B |
| 최저 비용 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |

- **속도**: Ministral 8B가 5개 중 4개 1위, Qwen 3 32B가 번역 한→영 1위
- **비용**: 전 테스트에서 Ministral 8B가 최저 비용

### Complex Reasoning 품질 평가 상세 (Opus 4.6 — 5회 반복 공통 패턴)

> 5회 반복 평가에서 반복적으로 지적된 공통 강점·약점을 정리했습니다.

**Ministral 8B** (평균 정확성 6.8 / 구체성 7.2 / 구조화 9.0 / 실용성 6.2)
> **공통 강점**: 체계적 구조와 풍부한 기술 스택, Mermaid 다이어그램 포함, 보안·모니터링까지 포괄적 설계. **공통 약점**: 99.99% SLA 달성을 위한 RTO/RPO 수치 부재, 지역별 DB 혼용(DynamoDB/CosmosDB/MongoDB 등)의 현실성 부족, 다중 클라우드 전략의 비용·복잡도 분석 미흡, 일부 비표준 용어와 다국어 혼입.

**Qwen 3 32B** (평균 정확성 7.0 / 구체성 6.2 / 구조화 9.0 / 실용성 6.2)
> **공통 강점**: 가독성 높은 표 기반 구조, 우선순위 정리 명확, 기술 스택 선택지 폭넓음. **공통 약점**: 99.99% 가용성을 위한 구체적 장애 복구 전략 부족, 레이턴시 100ms 달성을 위한 정량적 분석 부재, CRDT/OT 같은 실시간 협업 핵심 동기화 알고리즘 미언급, 나열 수준의 기술 스택에 트레이드오프 분석 미흡.

**Claude Haiku 4.5** (평균 정확성 6.8 / 구체성 7.8 / 구조화 7.8 / 실용성 5.8)
> **공통 강점**: 구체적 Python 코드 예시와 의사코드 풍부, 캐시 계층·장애조치 등 구현 수준의 설계. **공통 약점**: 매회 4096 토큰에서 잘려 레거시 통합 등 후반 우선순위 항목 누락, 일부 부정확한 기술 적용(동기 복제로 cross-region, 비현실적 메모리 산정), GDPR/PIPL 등 구체 법규 매핑 부재.

**Nova 2 Lite** (평균 정확성 6.4 / 구체성 6.6 / 구조화 8.6 / 실용성 6.0)
> **공통 강점**: 체계적 구성과 다양한 기술 스택, 가독성 좋은 표 활용. **공통 약점**: AWS 리전명 오기(뉴먼헨, 뉴먼펜 등 존재하지 않는 지역명 반복), 부정확한 용어(어드버서 패턴 등), CRDT 기반 충돌 해결 전략 부재, 99.99% SLA·크로스리전 동기화 트레이드오프 심층 분석 미흡.

**Llama 3.2 11B** (평균 정확성 3.8 / 구체성 2.8 / 구조화 2.2 / 실용성 2.8)
> **공통 강점**: 기본적인 기술 키워드 식별. **공통 약점**: 매회 동일 내용 반복·빈 헤딩·참고자료 링크 스팸 등 심각한 생성 루프 오류, 멀티리전 아키텍처·CDN·CRDT 등 핵심 기술 누락, 우선순위 설정 부적절(99.99% 가용성을 '중'으로 분류), 전반적으로 실무 적용이 어려운 피상적 수준.

### 종합 분석

**가성비 최강 — Ministral 8B**: 전 테스트 최저 비용($0.001685/5회 평균), 4/5 테스트에서 최고 속도, Complex Reasoning 품질 1위(7.3점). 8B 파라미터로 가장 작은 모델이지만 한국어 복합 추론에서도 최고 품질. 처리량(229.0 tok/s) 압도적 1위, 달러당 품질점(13,594)에서 2위 대비 2.5배 차이. 5회 반복에서도 결과 편차가 작아(±0.58s) 안정성도 우수.

**속도 특화 — Nova 2 Lite**: 평균 Latency 2위(12.14s). 응답이 자연 종료되는 비율이 높아 불필요한 토큰 낭비가 적음. 그러나 출력 단가($2.50/1M)로 인해 비용 순위는 4위($0.023034). 품질은 6.9점(4위)으로 지역명 오기 등 반복적 오류가 약점. 응답 속도가 최우선인 실시간 서비스에 적합.

**품질 투자형 — Claude Haiku 4.5**: 구체성(7.8)과 코드 예시 품질이 가장 높으며 품질 3위(7.0점). 그러나 출력 단가($5/1M)가 타 모델 대비 2~33배 높고, 5회 평균 총 비용($0.067487)이 최고. 비용 효율(337 점/$)은 최하위. 매회 4096 한도에 도달하여 응답이 잘리는 것이 일관된 약점. 품질이 최우선인 프로덕션 환경에서 고려.

**비용 효율 우수 — Qwen 3 32B**: 품질 2위(7.1점), 비용 3위($0.004463). 구조화 점수(9.0) 최고. 번역 한→영에서 유일하게 최고 속도(1.07s). 달러당 품질점(5,362)이 2위로 비용 대비 품질 균형이 좋음. 다만 처리량(102.3 tok/s)이 가장 낮아 대량 처리에는 비효율적. 5회 반복에서 품질 편차가 가장 작아(7.0~7.5) 응답 안정성이 높음.

**주의 필요 — Llama 3.2 11B**: 5개 테스트 × 5회 = 25회 전부에서 4096 토큰 한도에 도달. 매회 동일 내용 반복, 빈 헤딩 스팸, 참고자료 링크 루프 등 심각한 출력 제어 오류가 일관되게 발생. 비용은 2위($0.003428)로 저렴하나 품질(2.9점)이 압도적 최하위. 비용이 일정한 이유는 매회 정확히 4096 토큰을 출력하기 때문.

---

## 클래스 구조

### `BedrockModelComparison`

| 메서드 | 설명 |
|--------|------|
| `__init__(region)` | Bedrock 클라이언트 초기화, 모델 정보(ID·가격·포맷) 등록 |
| `invoke_model(model_key, prompt, max_tokens)` | 단일 모델 호출 후 latency·tokens·cost·응답 반환 |
| `run_test(prompt, test_name)` | 동일 프롬프트로 전체 모델 순차 호출, 결과 수집 |
| `compare_results(test_result)` | 단일 테스트의 모델별 비교표 콘솔 출력 |
| `evaluate_quality(test_result)` | Opus 4.6으로 각 모델 응답의 품질 평가 (4항목 채점 + 코멘트) |
| `save_test_detail(test_result, evaluations, filename)` | 단일 테스트 상세 결과를 품질 평가 포함 JSON으로 저장 |
| `save_results(filename)` | 전체 테스트 결과를 구조화된 JSON으로 저장 |
| `print_summary()` | 모델별 평균 통계 콘솔 출력 |

### 모델별 API 포맷 처리

각 provider마다 요청/응답 JSON 구조가 다르므로 `invoke_model`에서 포맷별 분기 처리합니다:

| 포맷 | 대상 모델 | 요청 형식 | 응답 파싱 |
|------|----------|----------|----------|
| `claude` | Haiku 4.5, Opus 4.6(평가용) | Messages API (`anthropic_version`) | `content[0].text` |
| `nova` | Nova 2 Lite | Messages + `inferenceConfig` | `output.message.content[0].text` |
| `llama` | Llama 3.2 11B | `prompt` + `max_gen_len` | `generation` |
| `mistral` | Ministral 8B | Messages + `max_tokens` | `choices[0].message.content` |
| `qwen` | Qwen 3 32B | Messages + `max_tokens` | `choices[0].message.content` |

---

## 프로젝트 구조

```
Lite-model-test/
├── README.md                          # 이 문서
├── bedrock_model_comparison.py        # 메인 스크립트
├── comparison_results.json            # 전체 테스트 결과 (실행 후 생성)
└── complex_reasoning_results.json     # Complex Reasoning 상세 + 품질 평가 (실행 후 생성)
```

---

## 확장 가이드

### 테스트 케이스 추가

`main()` 함수의 `test_cases` 리스트에 dict를 추가합니다:

```python
{
    'name': 'My New Test',
    'prompt': '테스트 프롬프트 내용...'
}
```

### 모델 추가

`__init__`의 `self.models` dict에 새 모델을 추가합니다:

```python
'new-model': {
    'id': 'provider.model-id',
    'name': 'Display Name',
    'input_price': 0.00,   # USD per 1M tokens
    'output_price': 0.00,
    'format': 'claude'      # claude | nova | llama | mistral | qwen
}
```

기존 포맷과 다른 API 구조라면 `invoke_model` 메서드에 새 포맷 분기를 추가해야 합니다.

### 다른 테스트에 품질 평가 적용

`main()`에서 원하는 테스트 결과에 대해 `evaluate_quality()`와 `save_test_detail()`을 호출합니다:

```python
evaluations = comparison.evaluate_quality(target_result)
comparison.save_test_detail(target_result, evaluations, 'my_detail_results.json')
```

> Opus 4.6 호출은 모델당 1회 추가 API 호출이 발생하므로 비용에 유의하세요.
