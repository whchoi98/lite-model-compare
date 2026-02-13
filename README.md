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
| Qwen 3 32B | $0.50 | $1.50 |
| Nova 2 Lite | $0.06 | $0.24 |
| Llama 3.2 11B | $0.16 | $0.16 |
| Ministral 8B | $0.10 | $0.10 |

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

## 최근 테스트 결과 (2026-02-13, max_tokens=4096)

### 속도 순위 (5개 테스트 평균)

| 순위 | 모델 | 평균 Latency | 평균 토큰 |
|------|------|-------------|----------|
| 1 | Ministral 8B | 8.85s | 2,416 |
| 2 | Nova 2 Lite | 11.86s | 1,990 |
| 3 | Claude Haiku 4.5 | 16.19s | 2,912 |
| 4 | Qwen 3 32B | 17.51s | 1,691 |
| 5 | Llama 3.2 11B | 24.98s | 4,285 |

### 비용 순위 (5개 테스트 총합)

| 순위 | 모델 | 총 비용 |
|------|------|--------|
| 1 | Ministral 8B | $0.001208 |
| 2 | Nova 2 Lite | $0.002183 |
| 3 | Llama 3.2 11B | $0.003428 |
| 4 | Qwen 3 32B | $0.011596 |
| 5 | Claude Haiku 4.5 | $0.066961 |

### Complex Reasoning 품질 평가 (Opus 4.6 채점)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 | 코멘트 요약 |
|------|--------|--------|--------|--------|------|------------|
| Ministral 8B | 7 | 8 | 9 | 7 | 7.8 | 체계적이고 풍부한 기술 스택, DB 혼용 근거 불명확·QUIC/WebSocket 병행 논리 부족 |
| Claude Haiku 4.5 | 7 | 8 | 8 | 6 | 7.2 | 구체적 코드 예시 포함하나 Priority 2까지만 작성되고 응답 잘림 |
| Nova 2 Lite | 7 | 7 | 9 | 6 | 7.2 | 체계적 구조·가독성 우수하나 지역명 오기, Aurora 글로벌 DB 한계 미언급 |
| Qwen 3 32B | 6 | 6 | 8 | 5 | 6.2 | 구조 우수하나 GDPR 등 구체 법규 미언급, 장애조치 설계 부족 |
| Llama 3.2 11B | 4 | 3 | 2 | 3 | 3.0 | 핵심 주제 피상적, 후반부 동일 문장 수십 회 반복 오류 |

> Haiku 4.5, Llama 3.2 11B, Ministral 8B는 4096 토큰 한도에 도달하여 응답이 잘렸습니다. Qwen 3 32B와 Nova 2 Lite는 자연 종료되었습니다.

### 테스트별 상세 결과

#### 1. Complex Reasoning (복합 추론 — 글로벌 협업 플랫폼 아키텍처 설계)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Nova 2 Lite | 13.20s | 1,817 | 4,547자 | $0.000449 | 자연 종료 |
| Ministral 8B | 18.26s | 4,096 | 10,721자 | $0.000427 | **한도 도달** |
| Llama 3.2 11B | 25.27s | 4,096 | 10,364자 | $0.000683 | **한도 도달** |
| Claude Haiku 4.5 | 25.90s | 4,096 | 10,861자 | $0.020767 | **한도 도달** |
| Qwen 3 32B | 26.02s | 2,287 | 4,589자 | $0.003537 | 자연 종료 |

- **최고 속도**: Nova 2 Lite (13.20s)
- **최저 비용**: Ministral 8B ($0.000427)
- **최고 품질**: Ministral 8B (Opus 4.6 평균 7.8점)
- 3개 모델(Haiku, Llama, Ministral)이 4096 한도 도달 — 복합 추론은 토큰 소모가 큼

#### 2. Advanced Code Generation (코드 생성 — LRU 캐시 Python 구현)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 6.94s | 1,903 | 6,604자 | $0.000205 | 자연 종료 |
| Nova 2 Lite | 13.90s | 2,284 | 7,312자 | $0.000559 | 자연 종료 |
| Claude Haiku 4.5 | 18.01s | 4,096 | 10,969자 | $0.020712 | **한도 도달** |
| Qwen 3 32B | 23.47s | 2,043 | 6,183자 | $0.003145 | 자연 종료 |
| Llama 3.2 11B | 25.32s | 4,096 | 9,313자 | $0.000678 | **한도 도달** |

- **최고 속도**: Ministral 8B (6.94s)
- **최저 비용**: Ministral 8B ($0.000205)
- Haiku 4.5와 Llama만 4096 한도 도달, 나머지는 자연 종료

#### 3. Multi-dimensional Analysis (다각도 분석 — B2B SaaS 전환)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 14.01s | 3,952 | 8,726자 | $0.000420 | 자연 종료 |
| Llama 3.2 11B | 24.81s | 4,096 | 7,358자 | $0.000696 | **한도 도달** |
| Nova 2 Lite | 24.59s | 3,791 | 8,113자 | $0.000927 | 자연 종료 |
| Claude Haiku 4.5 | 28.88s | 4,096 | 5,986자 | $0.020871 | **한도 도달** |
| Qwen 3 32B | 33.42s | 2,573 | 4,053자 | $0.004005 | 자연 종료 |

- **최고 속도**: Ministral 8B (14.01s)
- **최저 비용**: Ministral 8B ($0.000420)
- Haiku 4.5와 Llama만 4096 한도 도달

#### 4. Technical Translation 한→영 (CAP 정리 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 0.95s | 104 | 587자 | $0.000273 | 자연 종료 |
| Ministral 8B | 1.78s | 376 | 1,807자 | $0.000058 | 자연 종료 |
| Nova 2 Lite | 3.88s | 500 | 1,632자 | $0.000135 | 자연 종료 |
| Claude Haiku 4.5 | 4.22s | 275 | 941자 | $0.001716 | 자연 종료 |
| Llama 3.2 11B | 25.51s | 4,096 | 8,076자 | $0.000688 | **한도 도달** |

- **최고 속도**: Qwen 3 32B (0.95s)
- **최저 비용**: Ministral 8B ($0.000058)
- 번역 태스크는 대부분 모델이 짧은 출력으로 자연 종료
- Llama 3.2만 4096 한도 도달 — 번역 후 불필요한 부연 설명을 대량 생성

#### 5. Technical Translation EN-KO 영→한 (Observability 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 3.25s | 813 | 1,718자 | $0.000100 | 자연 종료 |
| Qwen 3 32B | 3.68s | 362 | 585자 | $0.000637 | 자연 종료 |
| Nova 2 Lite | 3.73s | 418 | 841자 | $0.000113 | 자연 종료 |
| Claude Haiku 4.5 | 3.94s | 537 | 579자 | $0.002895 | 자연 종료 |
| Llama 3.2 11B | 23.99s | 4,096 | 17,135자 | $0.000683 | **한도 도달** |

- **최고 속도**: Ministral 8B (3.25s)
- **최저 비용**: Ministral 8B ($0.000100)
- Llama 3.2만 한도 도달 (17,135자 중 대부분이 번역 외 부가 콘텐츠)

### 처리량 분석 (출력 토큰/초)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | 평균 |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | 224.3 | 274.2 | 282.1 | 211.2 | 250.2 | **248.4** |
| Nova 2 Lite | 137.7 | 164.3 | 154.2 | 128.9 | 112.1 | **139.4** |
| Llama 3.2 11B | 162.1 | 161.7 | 165.1 | 160.6 | 170.7 | **164.0** |
| Claude Haiku 4.5 | 158.1 | 227.4 | 141.8 | 65.2 | 136.3 | **145.8** |
| Qwen 3 32B | 87.9 | 87.0 | 77.0 | 109.5 | 98.4 | **91.9** |

- **Ministral 8B**이 전 테스트에서 가장 높은 처리량 (평균 248.4 tok/s)
- **Qwen 3 32B**는 파라미터가 큰 만큼 처리량이 가장 낮음 (평균 91.9 tok/s)

### 비용 효율성 분석 (품질점/달러, Complex Reasoning 기준)

| 모델 | 비용 | 품질 평균 | 점수/$ |
|------|------|----------|--------|
| Ministral 8B | $0.000427 | 7.8 | **18,267** |
| Nova 2 Lite | $0.000449 | 7.2 | **16,036** |
| Llama 3.2 11B | $0.000683 | 3.0 | 4,392 |
| Qwen 3 32B | $0.003537 | 6.2 | 1,753 |
| Claude Haiku 4.5 | $0.020767 | 7.2 | 347 |

- **Ministral 8B**가 달러당 품질점에서 1위
- **Nova 2 Lite**가 근소한 차이로 2위, 비용 대비 품질이 우수
- **Haiku 4.5**는 품질 자체는 상위권이나 출력 단가($5/1M)가 높아 효율이 최하위

### 테스트 유형별 우승 모델

| 기준 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| 최고 속도 | Nova 2 Lite | Ministral 8B | Ministral 8B | Qwen 3 32B | Ministral 8B |
| 최저 비용 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |

- **속도**: Ministral 8B가 5개 중 3개 1위, Qwen 3 32B가 번역 한→영 1위, Nova 2 Lite가 Complex Reasoning 1위
- **비용**: 전 테스트에서 Ministral 8B가 최저 비용

### Complex Reasoning 품질 평가 상세 (Opus 4.6 코멘트 전문)

**Ministral 8B** (정확성 7 / 구체성 8 / 구조화 9 / 실용성 7)
> 체계적인 구조와 풍부한 기술 스택 제시가 돋보이나, 지역별 DB를 PostgreSQL/CockroachDB/MongoDB로 혼용한 근거가 불명확하고, QUIC과 WebSocket의 역할 구분 및 병행 사용의 구체적 논리가 부족하며, 일부 기술적 깊이와 실현 가능성 검증이 미흡합니다.

**Claude Haiku 4.5** (정확성 7 / 구체성 8 / 구조화 8 / 실용성 6)
> 데이터 주권과 고가용성에 대해 구체적인 기술 스택과 코드 예시를 잘 제시했으나, 응답이 Priority 2까지만 작성되고 잘린 점(Priority 3 성능/확장성의 200만 동시접속 대응, Priority 4 레이턴시 최적화, Priority 5 레거시 통합이 모두 누락)이 가장 큰 약점입니다.

**Nova 2 Lite** (정확성 7 / 구체성 7 / 구조화 9 / 실용성 6)
> 전체적으로 체계적이고 가독성 높은 구조이나, 북미 데이터센터 지역명 오기, WebRTC 설명 중 러시아어 혼입, Aurora 글로벌 DB를 3개 지역 동시 쓰기에 사용 시의 지연 한계 미언급 등 실무 적용 시 깊이가 아쉬운 부분이 있다.

**Qwen 3 32B** (정확성 6 / 구체성 6 / 구조화 8 / 실용성 5)
> 전체 구조와 가독성은 우수하나, 데이터 주권 구현 전략(GDPR vs PIPL vs 미국 규제 등 구체 법규 미언급), 99.99% 가용성 달성을 위한 구체적 장애조치 설계(Active-Active, RTO/RPO 수치 등)가 부족하며, 기술적 깊이와 정확성에서 아쉬움이 있다.

**Llama 3.2 11B** (정확성 4 / 구체성 3 / 구조화 2 / 실용성 3)
> 핵심 주제들을 피상적으로만 다루고 있으며, 멀티리전 아키텍처·CDN·CRDT·Auto Scaling·GDPR 등 구체적 전략이 부재하고, 응답 후반부에 동일 문장이 수십 회 반복되는 치명적 생성 오류가 응답의 신뢰성을 크게 훼손합니다.

### 종합 분석

**가성비 최강 — Ministral 8B**: 5개 테스트 중 3개에서 최고 속도, 전 테스트 최저 비용, Complex Reasoning 품질 평가 1위(7.8점). 8B 파라미터로 가장 작은 모델이지만, 한국어 복합 추론에서 32B Qwen을 능가하는 결과를 보여 경량 모델의 한계를 재정의함. 처리량(248.4 tok/s)도 압도적 1위.

**균형형 — Nova 2 Lite**: 속도 2위, 비용 2위, 품질 공동 2위(7.2점). 출력 단가($0.24/1M)가 저렴하여 대량 호출에 적합. Complex Reasoning에서 최고 속도(13.20s)를 기록하며, 응답이 자연 종료되는 비율이 높아 불필요한 토큰 낭비가 적음.

**품질 투자형 — Claude Haiku 4.5**: 코드 예시, 의사 코드 등 가장 풍부한 포맷의 응답을 생성하며 품질 공동 2위(7.2점). 그러나 출력 단가($5/1M)가 타 모델 대비 20~50배 높고, 비용 효율(347 점/$)은 최하위. 품질이 최우선인 프로덕션 환경에서 고려.

**구조화 특화 — Qwen 3 32B**: 구조화 점수 8점으로 양호. 번역 한→영에서 최고 속도(0.95s). 그러나 32B 파라미터 대비 추론·분석 태스크에서의 품질 우위가 뚜렷하지 않으며(6.2점), 처리량(91.9 tok/s)이 가장 낮아 대량 처리에는 비효율적.

**주의 필요 — Llama 3.2 11B**: 5개 테스트 전부에서 4096 토큰 한도에 도달. Complex Reasoning에서 동일 문장 수십 회 반복 오류, 번역에서 불필요한 부연 설명 과다 생성(17,135자) 등 출력 제어 능력이 부족. 비용은 3위지만 품질(3.0점) 대비 효율이 낮음.

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
