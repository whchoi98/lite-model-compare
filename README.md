# AWS Bedrock 경량 모델 비교 테스트

AWS Bedrock에서 제공하는 5개 경량 LLM 모델을 동일한 프롬프트로 호출하여 응답 속도, 토큰 사용량, 비용, 응답 품질을 종합 비교하는 도구입니다.
전체 5개 테스트에 대해 Claude Opus 4.6이 각 모델의 응답 품질을 자동 평가합니다.

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
  ├─ 전체 테스트 결과 → Opus 4.6 품질 평가 (evaluate_quality × 5)
  │   ├─ complex_reasoning_results.json
  │   ├─ advanced_code_generation_results.json
  │   ├─ multi_dimensional_analysis_results.json
  │   ├─ technical_translation_results.json
  │   └─ technical_translation_en_ko_results.json
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

### `<test_name>_results.json` — 테스트별 상세 결과 + 품질 평가

각 테스트의 모델별 응답 전문과 Opus 4.6의 품질 평가를 포함합니다. 5개 파일이 생성됩니다:
- `complex_reasoning_results.json`
- `advanced_code_generation_results.json`
- `multi_dimensional_analysis_results.json`
- `technical_translation_results.json`
- `technical_translation_en_ko_results.json`

```
{
  "test_name": "<테스트명>",
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

### 품질 평가 (Opus 4.6 자동 채점, 전체 5개 테스트 적용)
- **정확성 (Accuracy)**: 사실 관계 및 기술적 정확성 (1~10)
- **구체성 (Specificity)**: 구체적 예시, 수치, 구현 디테일 포함 정도 (1~10)
- **구조화 (Structure)**: 논리적 구성, 가독성, 체계적 전개 (1~10)
- **실용성 (Practicality)**: 실무에서 바로 적용 가능한 정도 (1~10)
- **코멘트 (Comment)**: 강점과 약점을 요약한 한줄 평가

---

## 최근 테스트 결과 (2026-02-20, 5회 반복 평균, max_tokens=4096)

> 동일 조건으로 5회 반복 실행한 결과의 평균값입니다. 표준편차(±)를 함께 표기하여 결과의 안정성을 보여줍니다.
> 전체 5개 테스트에 대해 Opus 4.6 품질 평가를 수행했습니다 (1회당 25회 Opus 호출, 5회 반복 총 125회).

### 속도 순위 (5개 테스트 × 5회 반복 평균)

| 순위 | 모델 | 평균 Latency | 표준편차 | 평균 토큰 |
|------|------|-------------|---------|----------|
| 1 | Ministral 8B | 9.81s | ±0.58s | 2,312 |
| 2 | Nova 2 Lite | 13.87s | ±1.08s | 2,227 |
| 3 | Qwen 3 32B | 14.61s | ±0.58s | 1,673 |
| 4 | Claude Haiku 4.5 | 16.57s | ±0.54s | 2,866 |
| 5 | Llama 3.2 11B | 23.43s | ±0.72s | 4,147 |

### 비용 순위 (5개 테스트 총합, 5회 반복 평균)

| 순위 | 모델 | 평균 총 비용 | 최소 | 최대 |
|------|------|------------|------|------|
| 1 | Ministral 8B | $0.001735 | $0.001629 | $0.001885 |
| 2 | Llama 3.2 11B | $0.003318 | $0.002879 | $0.003428 |
| 3 | Qwen 3 32B | $0.004531 | $0.004415 | $0.004732 |
| 4 | Nova 2 Lite | $0.025333 | $0.024353 | $0.025786 |
| 5 | Claude Haiku 4.5 | $0.065817 | $0.064256 | $0.067076 |

### 전체 테스트 품질 평가 (Opus 4.6 채점, 5회 반복 평균)

#### 1. Complex Reasoning (복합 추론)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 |
|------|--------|--------|--------|--------|------|
| Claude Haiku 4.5 | 6.8 | 8.0 | 8.4 | 6.0 | **7.3** |
| Ministral 8B | 6.4 | 7.2 | 9.0 | 6.0 | **7.2** |
| Qwen 3 32B | 7.0 | 6.0 | 9.0 | 6.0 | **7.0** |
| Nova 2 Lite | 6.4 | 6.4 | 8.8 | 6.0 | **6.9** |
| Llama 3.2 11B | 3.0 | 2.0 | 1.8 | 2.0 | **2.2** |

#### 2. Advanced Code Generation (코드 생성)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 |
|------|--------|--------|--------|--------|------|
| Claude Haiku 4.5 | 7.2 | 8.0 | 8.8 | 7.0 | **7.8** |
| Qwen 3 32B | 4.0 | 6.2 | 8.0 | 3.2 | **5.4** |
| Ministral 8B | 3.8 | 6.2 | 7.5 | 3.5 | **5.2** |
| Nova 2 Lite | 3.6 | 6.2 | 7.2 | 3.0 | **5.0** |
| Llama 3.2 11B | 2.8 | 3.6 | 2.8 | 2.0 | **2.8** |

#### 3. Multi-dimensional Analysis (다각도 분석)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 |
|------|--------|--------|--------|--------|------|
| Claude Haiku 4.5 | 5.6 | 8.0 | 8.6 | 6.0 | **7.0** |
| Qwen 3 32B | 5.2 | 6.0 | 8.4 | 5.6 | **6.3** |
| Nova 2 Lite | 4.5 | 6.2 | 8.2 | 4.8 | **5.9** |
| Ministral 8B | 4.2 | 6.2 | 7.6 | 4.2 | **5.5** |
| Llama 3.2 11B | 2.2 | 1.6 | 1.6 | 1.0 | **1.6** |

#### 4. Technical Translation 한→영 (기술 번역)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 |
|------|--------|--------|--------|--------|------|
| Nova 2 Lite | 9.0 | 8.0 | 9.2 | 8.6 | **8.7** |
| Qwen 3 32B | 9.0 | 7.2 | 9.0 | 8.6 | **8.4** |
| Claude Haiku 4.5 | 9.0 | 7.2 | 9.0 | 8.2 | **8.3** |
| Ministral 8B | 7.8 | 7.0 | 8.8 | 8.2 | **8.0** |
| Llama 3.2 11B | 4.8 | 2.6 | 1.0 | 2.6 | **2.8** |

#### 5. Technical Translation EN-KO 영→한 (기술 번역)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 |
|------|--------|--------|--------|--------|------|
| Claude Haiku 4.5 | 8.8 | 8.2 | 8.6 | 8.0 | **8.4** |
| Qwen 3 32B | 7.4 | 8.0 | 8.4 | 7.4 | **7.8** |
| Nova 2 Lite | 7.4 | 7.6 | 8.8 | 7.2 | **7.8** |
| Ministral 8B | 6.0 | 7.2 | 8.2 | 6.2 | **6.9** |
| Llama 3.2 11B | 4.2 | 4.4 | 1.8 | 2.6 | **3.2** |

### 전체 테스트 품질 종합 (5개 테스트 평균)

| 순위 | 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | **종합 평균** |
|------|------|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Claude Haiku 4.5 | 7.3 | 7.8 | 7.0 | 8.3 | 8.4 | **7.8** |
| 2 | Qwen 3 32B | 7.0 | 5.4 | 6.3 | 8.4 | 7.8 | **7.0** |
| 3 | Nova 2 Lite | 6.9 | 5.0 | 5.9 | 8.7 | 7.8 | **6.9** |
| 4 | Ministral 8B | 7.2 | 5.2 | 5.5 | 8.0 | 6.9 | **6.6** |
| 5 | Llama 3.2 11B | 2.2 | 2.8 | 1.6 | 2.8 | 3.2 | **2.5** |

> Haiku 4.5가 5개 테스트 중 4개에서 품질 1위. 번역 한→영에서만 Nova 2 Lite가 1위.
> 코드 생성에서 Haiku 4.5(7.8)와 2위(5.4) 간 격차가 가장 큼 — Haiku의 코드 능력이 두드러짐.
> Llama 3.2 11B는 전 테스트에서 최하위 (1.6~3.2점).

### 테스트별 성능 상세 (5회 반복 평균)

#### 1. Complex Reasoning (복합 추론 — 글로벌 협업 플랫폼 아키텍처 설계)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Nova 2 Lite | 14.13s (±2.18) | 2,094 | 4,539자 | $0.005300 | 자연 종료 |
| Ministral 8B | 15.33s (±2.41) | 3,377 | 8,879자 | $0.000532 | 자연 종료 |
| Qwen 3 32B | 23.29s (±2.94) | 2,159 | 4,800자 | $0.001328 | 자연 종료 |
| Claude Haiku 4.5 | 25.73s (±1.68) | 4,096 | 10,285자 | $0.020767 | **한도 도달 5/5회** |
| Llama 3.2 11B | 26.47s (±5.40) | 4,096 | 8,381자 | $0.000683 | **한도 도달 5/5회** |

- **최고 속도**: Nova 2 Lite (14.13s) / **최저 비용**: Ministral 8B ($0.000532)
- **최고 품질**: Claude Haiku 4.5 (7.3점)

#### 2. Advanced Code Generation (코드 생성 — LRU 캐시 Python 구현)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 10.31s (±2.09) | 2,246 | 7,433자 | $0.000358 | 자연 종료 |
| Nova 2 Lite | 15.98s (±1.45) | 2,634 | 9,127자 | $0.006637 | 자연 종료 |
| Qwen 3 32B | 17.77s (±4.25) | 2,056 | 6,873자 | $0.001258 | 자연 종료 |
| Claude Haiku 4.5 | 17.84s (±1.06) | 3,872 | 10,572자 | $0.019592 | **한도 도달 2/5회** |
| Llama 3.2 11B | 23.55s (±0.26) | 4,096 | 9,846자 | $0.000678 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (10.31s) / **최저 비용**: Ministral 8B ($0.000358)
- **최고 품질**: Claude Haiku 4.5 (7.8점) — 2위(5.4) 대비 압도적 차이

#### 3. Multi-dimensional Analysis (다각도 분석 — B2B SaaS 전환)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 17.36s (±1.81) | 3,820 | 7,511자 | $0.000610 | **한도 도달 3/5회** |
| Llama 3.2 11B | 23.84s (±1.05) | 4,096 | 7,077자 | $0.000696 | **한도 도달 5/5회** |
| Nova 2 Lite | 26.78s (±2.77) | 3,812 | 8,185자 | $0.009618 | **한도 도달 2/5회** |
| Qwen 3 32B | 27.31s (±4.64) | 2,593 | 4,285자 | $0.001599 | 자연 종료 |
| Claude Haiku 4.5 | 30.85s (±1.10) | 4,096 | 5,074자 | $0.020871 | **한도 도달 5/5회** |

- **최고 속도**: Ministral 8B (17.36s) / **최저 비용**: Ministral 8B ($0.000610)
- **최고 품질**: Claude Haiku 4.5 (7.0점)
- 4개 모델이 한도에 도달 — 분석 태스크는 토큰 소모가 큼

#### 4. Technical Translation 한→영 (CAP 정리 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 1.03s (±0.10) | 103 | 593자 | $0.000097 | 자연 종료 |
| Ministral 8B | 2.08s (±0.20) | 370 | 1,673자 | $0.000085 | 자연 종료 |
| Claude Haiku 4.5 | 3.79s (±1.15) | 284 | 988자 | $0.001761 | 자연 종료 |
| Nova 2 Lite | 4.45s (±1.24) | 612 | 2,328자 | $0.001604 | 자연 종료 |
| Llama 3.2 11B | 23.46s (±0.51) | 4,096 | 7,823자 | $0.000688 | **한도 도달 5/5회** |

- **최고 속도**: Qwen 3 32B (1.03s) / **최저 비용**: Ministral 8B ($0.000085)
- **최고 품질**: Nova 2 Lite (8.7점) — 유일하게 번역에서 1위
- Llama 3.2만 매회 한도 도달 — 번역 후 불필요한 부연 설명을 대량 생성

#### 5. Technical Translation EN-KO 영→한 (Observability 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 3.66s (±0.13) | 369 | 647자 | $0.000250 | 자연 종료 |
| Ministral 8B | 3.96s (±1.48) | 809 | 1,646자 | $0.000149 | 자연 종료 |
| Claude Haiku 4.5 | 4.63s (±0.77) | 523 | 571자 | $0.002826 | 자연 종료 |
| Nova 2 Lite | 8.02s (±4.71) | 844 | 1,723자 | $0.002174 | 자연 종료 |
| Llama 3.2 11B | 19.80s (±8.67) | 3,410 | 11,681자 | $0.000573 | **한도 도달 4/5회** |

- **최고 속도**: Qwen 3 32B (3.66s) / **최저 비용**: Ministral 8B ($0.000149)
- **최고 품질**: Claude Haiku 4.5 (8.4점)

### 처리량 분석 (출력 토큰/초, 5회 반복 평균)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | 평균 |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | 220.2 | 217.8 | 220.0 | 178.0 | 204.3 | **207.6** |
| Llama 3.2 11B | 154.7 | 173.9 | 171.8 | 174.6 | 172.2 | **169.8** |
| Nova 2 Lite | 148.2 | 164.8 | 142.4 | 137.5 | 105.2 | **143.0** |
| Claude Haiku 4.5 | 159.1 | 217.1 | 132.8 | 74.9 | 113.0 | **141.3** |
| Qwen 3 32B | 92.7 | 115.7 | 95.0 | 100.0 | 100.8 | **102.3** |

- **Ministral 8B**이 전 테스트에서 가장 높은 처리량 (평균 207.6 tok/s)
- **Qwen 3 32B**는 파라미터가 큰 만큼 처리량이 가장 낮음 (평균 102.3 tok/s)

### 비용 효율성 분석 (품질점/달러, 테스트별 5회 평균 기준)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | **13,534** | **14,525** | **9,016** | 94,118 | **46,309** |
| Qwen 3 32B | 5,271 | 4,293 | 3,940 | **86,598** | 31,200 |
| Llama 3.2 11B | 3,221 | 4,130 | 2,299 | 4,070 | 5,585 |
| Nova 2 Lite | 1,302 | 753 | 613 | 5,424 | 3,588 |
| Claude Haiku 4.5 | 352 | 398 | 335 | 4,713 | 2,972 |

- **Ministral 8B**가 5개 중 4개 테스트에서 비용 효율 1위
- **번역 한→영**에서만 Qwen 3 32B가 1위 (짧은 응답 + 저렴한 단가)
- **Haiku 4.5**는 품질 최상위이나 비용 효율은 전 테스트 최하위

### 테스트 유형별 우승 모델

| 기준 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| 최고 속도 | Nova 2 Lite | Ministral 8B | Ministral 8B | Qwen 3 32B | Qwen 3 32B |
| 최저 비용 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |
| 최고 품질 | Haiku 4.5 | Haiku 4.5 | Haiku 4.5 | Nova 2 Lite | Haiku 4.5 |
| 비용 효율 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |

- **품질**: Claude Haiku 4.5가 5개 중 4개 1위, Nova 2 Lite가 번역 한→영 1위
- **속도**: Ministral 8B 2개, Qwen 3 32B 2개, Nova 2 Lite 1개로 분산
- **비용·비용 효율**: 전 테스트에서 Ministral 8B가 1위

### 종합 분석

**품질 최강 — Claude Haiku 4.5**: 5개 테스트 종합 품질 1위(7.8점). 코드 생성(7.8)에서 2위(5.4) 대비 2.4점 격차로 압도적. 구체성(8.0~8.2)과 구조화(8.4~9.0) 점수가 일관되게 높음. 그러나 출력 단가($5/1M)가 타 모델 대비 2~33배 높고, 5회 평균 총 비용($0.065817)이 최고. 비용 효율은 전 테스트 최하위. Complex Reasoning과 Analysis에서 매회 4096 한도 도달로 응답이 잘리는 것이 일관된 약점. 품질이 최우선인 프로덕션 환경에 적합.

**균형형 — Qwen 3 32B**: 종합 품질 2위(7.0점), 비용 3위($0.004531). 번역 한→영에서 최고 속도(1.03s)와 품질 2위(8.4). 구조화 점수(8.0~9.0)가 전 테스트에서 높음. 처리량(102.3 tok/s)이 가장 낮지만 응답 편차가 작아(±0.58s) 안정적. 비용 대비 품질 균형이 좋은 범용 모델.

**가성비 최강 — Ministral 8B**: 전 테스트 최저 비용($0.001735), 비용 효율 4/5 테스트 1위. 처리량(207.6 tok/s) 압도적 1위. Complex Reasoning 품질 2위(7.2)로 추론 능력도 양호하나, 코드 생성(5.2)·분석(5.5)에서는 중위권. 종합 품질 4위(6.6)로 단순 태스크에 최적, 복잡한 태스크에는 품질 저하 주의.

**번역 특화 — Nova 2 Lite**: 종합 품질 3위(6.9점). 번역 한→영에서 유일하게 품질 1위(8.7). 평균 Latency 2위(13.87s). 그러나 출력 단가($2.50/1M)로 인해 비용 순위 4위. 코드 생성(5.0)·분석(5.9)에서 하위권. 번역·속도가 중요한 서비스에 적합.

**주의 필요 — Llama 3.2 11B**: 종합 품질 최하위(2.5점). 전 테스트에서 높은 빈도로 4096 한도 도달(24/25회). 동일 내용 반복, 빈 헤딩 스팸, 참고자료 링크 루프 등 심각한 출력 제어 오류가 일관 발생. 비용은 2위($0.003318)로 저렴하나 품질이 실무 수준에 미달.

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
├── README.md                                  # 이 문서
├── bedrock_model_comparison.py                # 메인 스크립트
├── aggregate_results.py                       # 5회 반복 결과 집계 스크립트
├── run_5_tests.sh                             # 5회 반복 실행 + 집계 자동화 스크립트
├── comparison_results.json                    # 전체 테스트 결과 (실행 후 생성)
├── complex_reasoning_results.json             # Complex Reasoning 상세 + 품질 평가
├── advanced_code_generation_results.json      # Code Generation 상세 + 품질 평가
├── multi_dimensional_analysis_results.json    # Analysis 상세 + 품질 평가
├── technical_translation_results.json         # 번역 한→영 상세 + 품질 평가
├── technical_translation_en_ko_results.json   # 번역 영→한 상세 + 품질 평가
└── aggregated_results.json                    # 5회 반복 집계 결과
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

### 5회 반복 실행

`run_5_tests.sh`를 실행하면 자동으로 5회 반복 후 집계합니다:

```bash
bash run_5_tests.sh
```

> 1회 실행 시 Opus 4.6 품질 평가 25회(5모델×5테스트) 포함. 5회 반복 시 총 125회 Opus 호출이 발생하므로 비용에 유의하세요.
