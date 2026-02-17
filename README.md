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

## 최근 테스트 결과 (2026-02-15, max_tokens=4096)

### 속도 순위 (5개 테스트 평균)

| 순위 | 모델 | 평균 Latency | 평균 토큰 |
|------|------|-------------|----------|
| 1 | Ministral 8B | 9.37s | 2,302 |
| 2 | Nova 2 Lite | 9.67s | 1,774 |
| 3 | Qwen 3 32B | 13.74s | 1,622 |
| 4 | Claude Haiku 4.5 | 15.87s | 2,860 |
| 5 | Llama 3.2 11B | 23.92s | 4,285 |

### 비용 순위 (5개 테스트 총합)

| 순위 | 모델 | 총 비용 |
|------|------|--------|
| 1 | Ministral 8B | $0.001726 |
| 2 | Llama 3.2 11B | $0.003428 |
| 3 | Qwen 3 32B | $0.004377 |
| 4 | Nova 2 Lite | $0.019670 |
| 5 | Claude Haiku 4.5 | $0.065651 |

### Complex Reasoning 품질 평가 (Opus 4.6 채점)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 | 코멘트 요약 |
|------|--------|--------|--------|--------|------|------------|
| Ministral 8B | 7 | 8 | 9 | 7 | 7.8 | 체계적 구조·풍부한 기술 스택, PDPA/CPRA 혼용·SLA 계산·RTO/RPO 명시 미흡 |
| Claude Haiku 4.5 | 7 | 8 | 9 | 6 | 7.5 | 코드 예시 인상적, CockroachDB 적합성 논거 부족·Redis 메모리 산정 비현실적 |
| Qwen 3 32B | 7 | 6 | 9 | 6 | 7.0 | 가독성 높은 구조, 장애 복구 전략·레이턴시 정량 분석·CRDT/OT 알고리즘 누락 |
| Nova 2 Lite | 6 | 5 | 8 | 5 | 6.0 | 체계적이나 '펜들리損失' 오류, CDN 다이어그램 위치 비논리적, 트레이드오프 분석 미흡 |
| Llama 3.2 11B | 4 | 3 | 3 | 3 | 3.2 | 피상적 내용, 핵심 기술 누락, 후반부 빈 '###' 수백 개 반복 오류 |

> Haiku 4.5와 Llama 3.2 11B는 Complex Reasoning에서 4096 토큰 한도에 도달하여 응답이 잘렸습니다. 나머지 모델은 자연 종료되었습니다.

### 테스트별 상세 결과

#### 1. Complex Reasoning (복합 추론 — 글로벌 협업 플랫폼 아키텍처 설계)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Nova 2 Lite | 12.61s | 1,986 | 4,157자 | $0.005029 | 자연 종료 |
| Ministral 8B | 16.34s | 3,671 | 10,191자 | $0.000576 | 자연 종료 |
| Qwen 3 32B | 22.51s | 2,090 | 4,116자 | $0.001286 | 자연 종료 |
| Llama 3.2 11B | 23.79s | 4,096 | 11,087자 | $0.000683 | **한도 도달** |
| Claude Haiku 4.5 | 24.78s | 4,096 | 9,366자 | $0.020767 | **한도 도달** |

- **최고 속도**: Nova 2 Lite (12.61s)
- **최저 비용**: Ministral 8B ($0.000576)
- **최고 품질**: Ministral 8B (Opus 4.6 평균 7.8점)
- 2개 모델(Haiku, Llama)이 4096 한도 도달

#### 2. Advanced Code Generation (코드 생성 — LRU 캐시 Python 구현)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 6.10s | 1,655 | 6,263자 | $0.000270 | 자연 종료 |
| Nova 2 Lite | 10.34s | 1,894 | 6,463자 | $0.004788 | 자연 종료 |
| Qwen 3 32B | 14.82s | 2,046 | 6,525자 | $0.001252 | 자연 종료 |
| Claude Haiku 4.5 | 17.72s | 3,831 | 9,644자 | $0.019387 | 자연 종료 |
| Llama 3.2 11B | 24.53s | 4,096 | 14,002자 | $0.000678 | **한도 도달** |

- **최고 속도**: Ministral 8B (6.10s)
- **최저 비용**: Ministral 8B ($0.000270)
- Llama 3.2 11B만 4096 한도 도달, 나머지는 자연 종료

#### 3. Multi-dimensional Analysis (다각도 분석 — B2B SaaS 전환)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Nova 2 Lite | 18.03s | 2,720 | 4,966자 | $0.006888 | 자연 종료 |
| Ministral 8B | 18.31s | 4,096 | 7,844자 | $0.000651 | **한도 도달** |
| Llama 3.2 11B | 24.01s | 4,096 | 7,333자 | $0.000696 | **한도 도달** |
| Qwen 3 32B | 26.76s | 2,406 | 3,981자 | $0.001487 | 자연 종료 |
| Claude Haiku 4.5 | 30.59s | 4,096 | 5,450자 | $0.020871 | **한도 도달** |

- **최고 속도**: Nova 2 Lite (18.03s)
- **최저 비용**: Ministral 8B ($0.000651)
- 3개 모델(Haiku, Llama, Ministral)이 4096 한도 도달

#### 4. Technical Translation 한→영 (CAP 정리 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 0.95s | 108 | 596자 | $0.000100 | 자연 종료 |
| Ministral 8B | 1.88s | 311 | 1,368자 | $0.000077 | 자연 종료 |
| Claude Haiku 4.5 | 2.55s | 281 | 1,025자 | $0.001746 | 자연 종료 |
| Nova 2 Lite | 4.25s | 719 | 3,476자 | $0.001870 | 자연 종료 |
| Llama 3.2 11B | 23.62s | 4,096 | 8,637자 | $0.000688 | **한도 도달** |

- **최고 속도**: Qwen 3 32B (0.95s)
- **최저 비용**: Ministral 8B ($0.000077)
- 번역 태스크는 대부분 모델이 짧은 출력으로 자연 종료
- Llama 3.2만 4096 한도 도달 — 번역 후 불필요한 부연 설명을 대량 생성

#### 5. Technical Translation EN-KO 영→한 (Observability 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Nova 2 Lite | 3.14s | 412 | 863자 | $0.001095 | 자연 종료 |
| Qwen 3 32B | 3.65s | 374 | 621자 | $0.000252 | 자연 종료 |
| Claude Haiku 4.5 | 3.69s | 534 | 566자 | $0.002880 | 자연 종료 |
| Ministral 8B | 4.20s | 836 | 1,793자 | $0.000153 | 자연 종료 |
| Llama 3.2 11B | 23.65s | 4,096 | 16,857자 | $0.000683 | **한도 도달** |

- **최고 속도**: Nova 2 Lite (3.14s)
- **최저 비용**: Ministral 8B ($0.000153)
- Llama 3.2만 한도 도달 (16,857자 중 대부분이 번역 외 부가 콘텐츠)

### 처리량 분석 (출력 토큰/초)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | 평균 |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | 224.7 | 271.3 | 223.7 | 165.4 | 199.0 | **216.8** |
| Llama 3.2 11B | 172.2 | 167.0 | 170.6 | 173.4 | 173.2 | **171.3** |
| Nova 2 Lite | 157.5 | 183.2 | 150.9 | 169.2 | 131.2 | **158.4** |
| Claude Haiku 4.5 | 165.3 | 216.2 | 133.9 | 110.2 | 144.7 | **154.1** |
| Qwen 3 32B | 92.8 | 138.1 | 89.9 | 113.7 | 102.5 | **107.4** |

- **Ministral 8B**이 전 테스트에서 가장 높은 처리량 (평균 216.8 tok/s)
- **Qwen 3 32B**는 파라미터가 큰 만큼 처리량이 가장 낮음 (평균 107.4 tok/s)

### 비용 효율성 분석 (품질점/달러, Complex Reasoning 기준)

| 모델 | 비용 | 품질 평균 | 점수/$ |
|------|------|----------|--------|
| Ministral 8B | $0.000576 | 7.8 | **13,542** |
| Qwen 3 32B | $0.001286 | 7.0 | **5,443** |
| Llama 3.2 11B | $0.000683 | 3.2 | 4,685 |
| Nova 2 Lite | $0.005029 | 6.0 | 1,193 |
| Claude Haiku 4.5 | $0.020767 | 7.5 | 361 |

- **Ministral 8B**가 달러당 품질점에서 압도적 1위
- **Qwen 3 32B**가 2위, 가격 대비 품질 균형이 우수
- **Nova 2 Lite**는 출력 단가($2.50/1M)로 인해 비용 효율 4위
- **Haiku 4.5**는 품질 자체는 2위이나 출력 단가($5/1M)가 높아 효율 최하위

### 테스트 유형별 우승 모델

| 기준 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| 최고 속도 | Nova 2 Lite | Ministral 8B | Nova 2 Lite | Qwen 3 32B | Nova 2 Lite |
| 최저 비용 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |

- **속도**: Nova 2 Lite가 5개 중 3개 1위, Ministral 8B가 Code Gen 1위, Qwen 3 32B가 번역 한→영 1위
- **비용**: 전 테스트에서 Ministral 8B가 최저 비용

### Complex Reasoning 품질 평가 상세 (Opus 4.6 코멘트 전문)

**Ministral 8B** (정확성 7 / 구체성 8 / 구조화 9 / 실용성 7)
> 체계적인 구조와 풍부한 기술 스택 제시가 돋보이나, 일부 기술적 부정확성(PDPA/CPRA를 아시아 법규로 혼용, 그라디언트 캐싱이라는 비표준 용어 사용, CockroachDB의 cross-region 100ms 이하 보장은 과장)과 레거시 통합 시 구체적 마이그레이션 리스크 분석 부재, 99.99% 가용성 달성을 위한 구체적 SLA 계산 및 장애 복구 시간(RTO/RPO) 명시가 없는 점이 아쉽고, 다중 클라우드 전략의 현실적 복잡성과 비용에 대한 고려가 부족합니다.

**Claude Haiku 4.5** (정확성 7 / 구체성 8 / 구조화 9 / 실용성 6)
> 체계적 구조와 코드 예시가 인상적이나, CockroachDB의 실시간 협업 적합성 논거 부족, Redis 메모리 산정(200만 동시접속에 32GB)이 비현실적으로 낮고, 레거시 통합 5순위 항목의 구체적 설계가 누락되었으며, 멀티클라우드 전략과 GDPR/개인정보보호법 등 구체적 법규 매핑이 부재하여 실무 즉시 적용에는 보완이 필요합니다.

**Qwen 3 32B** (정확성 7 / 구체성 6 / 구조화 9 / 실용성 6)
> 체계적이고 가독성 높은 구조로 핵심 요소를 잘 정리했으나, 99.99% 가용성 달성을 위한 구체적 장애 복구 전략(Active-Active 페일오버, 멀티리전 DR 등)이 부족하고, 레이턴시 100ms 달성을 위한 정량적 분석(네트워크 홉별 지연 예산 등)이 없으며, 멀티클라우드 전략의 복잡성과 현실적 트레이드오프에 대한 깊이 있는 논의가 미흡하고, CRDT/OT 같은 실시간 협업 핵심 동기화 알고리즘 언급이 빠져 있어 실무 적용 시 추가 설계가 상당히 필요합니다.

**Nova 2 Lite** (정확성 6 / 구체성 5 / 구조화 8 / 실용성 5)
> 체계적인 구조와 폭넓은 기술 스택 나열은 우수하나, '펜들리損失' 같은 의미불명 오류, 99.99% 다운타임 계산 오류(52분→실제 약 52.6분이지만 '가용성 허용'이라는 표현 부적절), 멀티클라우드 전략의 구체적 비교 부재, 다이어그램에서 CDN 위치가 비논리적(최하단 배치), 레이턴시 100ms 달성을 위한 구체적 수치 기반 분석 부족, 데이터 주권과 cross-region 동기화 간 트레이드오프 심층 분석 미흡 등 실무 적용에는 상당한 보완이 필요합니다.

**Llama 3.2 11B** (정확성 4 / 구체성 3 / 구조화 3 / 실용성 3)
> 우선순위 설정이 부적절하고(99.99% 가용성이 '중'으로 분류), 기술 스택이 피상적이며(CDN, 멀티리전 배포, CockroachDB/Spanner 등 핵심 기술 누락), 100ms 레이턴시 달성 전략이 구체적으로 없고, 응답 후반부에 수백 개의 빈 '###'이 반복되는 심각한 출력 오류가 있어 전체적으로 실무 적용이 어려운 수준의 응답입니다.

### 종합 분석

**가성비 최강 — Ministral 8B**: 전 테스트 최저 비용, Complex Reasoning 품질 평가 1위(7.8점). 8B 파라미터로 가장 작은 모델이지만, 한국어 복합 추론에서 32B Qwen을 능가하는 결과를 보여 경량 모델의 한계를 재정의함. 처리량(216.8 tok/s) 압도적 1위, 달러당 품질점(13,542)에서도 2위 대비 2.5배 차이.

**속도 특화 — Nova 2 Lite**: 5개 테스트 중 3개에서 최고 속도, 평균 Latency 2위(9.67s). Complex Reasoning에서 최고 속도(12.61s)를 기록하며, 응답이 자연 종료되는 비율이 높아 불필요한 토큰 낭비가 적음. 그러나 출력 단가($2.50/1M)로 인해 비용 순위는 4위($0.019670). 응답 속도가 최우선인 실시간 서비스에 적합.

**품질 투자형 — Claude Haiku 4.5**: 코드 예시, 의사 코드 등 가장 풍부한 포맷의 응답을 생성하며 품질 2위(7.5점). 그러나 출력 단가($5/1M)가 타 모델 대비 2~33배 높고, 5개 테스트 총 비용($0.065651)이 최고. 비용 효율(361 점/$)은 최하위. 품질이 최우선인 프로덕션 환경에서 고려.

**비용 효율 우수 — Qwen 3 32B**: 품질 3위(7.0점), 비용 3위($0.004377). 번역 한→영에서 최고 속도(0.95s). 달러당 품질점(5,443)이 2위로 비용 대비 품질 균형이 좋음. 다만 32B 파라미터 대비 처리량(107.4 tok/s)이 가장 낮아 대량 처리에는 비효율적.

**주의 필요 — Llama 3.2 11B**: 5개 테스트 전부에서 4096 토큰 한도에 도달. Complex Reasoning에서 빈 '###' 수백 개 반복 오류, 번역에서 불필요한 부연 설명 과다 생성(16,857자) 등 출력 제어 능력이 부족. 비용은 2위($0.003428)이지만 품질(3.2점) 대비 효율이 낮음.

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
