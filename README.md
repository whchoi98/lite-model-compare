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
| 1 | Ministral 8B | 8.23s | 2,393 |
| 2 | Nova 2 Lite | 12.67s | 2,142 |
| 3 | Qwen 3 32B | 14.16s | 1,677 |
| 4 | Claude Haiku 4.5 | 18.70s | 2,909 |
| 5 | Llama 3.2 11B | 42.66s | 4,285 |

### 비용 순위 (5개 테스트 총합)

| 순위 | 모델 | 총 비용 |
|------|------|--------|
| 1 | Ministral 8B | $0.001197 |
| 2 | Nova 2 Lite | $0.002365 |
| 3 | Llama 3.2 11B | $0.003428 |
| 4 | Qwen 3 32B | $0.011495 |
| 5 | Claude Haiku 4.5 | $0.066891 |

### Complex Reasoning 품질 평가 (Opus 4.6 채점)

| 모델 | 정확성 | 구체성 | 구조화 | 실용성 | 평균 | 코멘트 요약 |
|------|--------|--------|--------|--------|------|------------|
| Ministral 8B | 7 | 8 | 9 | 7 | 7.8 | 체계적이고 광범위하나 SLA 다운타임 표기 오류, 멀티클라우드 트레이드오프 분석 부족 |
| Nova 2 Lite | 7 | 7 | 9 | 7 | 7.5 | 포괄적 구조로 핵심 요소 정리 우수하나 데이터 주권·동기화 간 트레이드오프 심층 분석 부재 |
| Claude Haiku 4.5 | 7 | 8 | 8 | 6 | 7.3 | 기술 스택과 코드 예시 포함하나 Active-Active 충돌 해결 전략 부재, 응답 잘림 |
| Qwen 3 32B | 7 | 6 | 9 | 6 | 7.0 | 구조화 우수하나 실시간 협업 핵심 기술(WebSocket/CRDT) 미언급, 용어 오타 |
| Llama 3.2 11B | 4 | 3 | 2 | 3 | 3.0 | PlantUML 다이어그램 무한 반복 오류로 응답 신뢰성 크게 훼손 |

> Haiku 4.5와 Llama 3.2 11B는 4096 토큰 한도에 도달하여 응답이 잘렸습니다. 나머지 모델은 자연 종료되었습니다.

### 테스트별 상세 결과

#### 1. Complex Reasoning (복합 추론 — 글로벌 협업 플랫폼 아키텍처 설계)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 13.19s | 3,707 | 10,112자 | $0.000388 | 자연 종료 |
| Nova 2 Lite | 18.55s | 2,585 | 5,554자 | $0.000633 | 자연 종료 |
| Llama 3.2 11B | 24.66s | 4,096 | 20,678자 | $0.000683 | **한도 도달** |
| Qwen 3 32B | 25.79s | 2,299 | 4,302자 | $0.003555 | 자연 종료 |
| Claude Haiku 4.5 | 26.87s | 4,096 | 10,419자 | $0.020767 | **한도 도달** |

- **최고 속도**: Ministral 8B (13.19s)
- **최저 비용**: Ministral 8B ($0.000388)
- **최고 품질**: Ministral 8B (Opus 4.6 평균 7.8점)
- **최다 출력**: Llama 3.2 11B (20,678자) — 단, PlantUML 다이어그램 반복으로 유효 콘텐츠는 적음

#### 2. Advanced Code Generation (코드 생성 — LRU 캐시 Python 구현)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 9.52s | 2,652 | 10,091자 | $0.000279 | 자연 종료 |
| Nova 2 Lite | 9.73s | 1,627 | 5,798자 | $0.000401 | 자연 종료 |
| Qwen 3 32B | 13.55s | 1,896 | 6,188자 | $0.002924 | 자연 종료 |
| Llama 3.2 11B | 24.13s | 4,096 | 10,320자 | $0.000678 | **한도 도달** |
| Claude Haiku 4.5 | 24.63s | 4,096 | 10,696자 | $0.020712 | **한도 도달** |

- **최고 속도**: Ministral 8B (9.52s)
- **최저 비용**: Ministral 8B ($0.000279)
- 코드 생성에서는 Haiku 4.5와 Llama가 가장 많은 토큰을 사용 (4096 한도 도달)

#### 3. Multi-dimensional Analysis (다각도 분석 — B2B SaaS 전환)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Ministral 8B | 12.84s | 3,612 | 7,674자 | $0.000386 | 자연 종료 |
| Llama 3.2 11B | 24.53s | 4,096 | 7,938자 | $0.000696 | **한도 도달** |
| Nova 2 Lite | 25.64s | 4,096 | 7,257자 | $0.001001 | **한도 도달** |
| Qwen 3 32B | 27.03s | 2,667 | 4,253자 | $0.004146 | 자연 종료 |
| Claude Haiku 4.5 | 33.37s | 4,096 | 4,884자 | $0.020871 | **한도 도달** |

- **최고 속도**: Ministral 8B (12.84s)
- **최저 비용**: Ministral 8B ($0.000386)
- 분석 유형에서는 3개 모델(Haiku, Nova, Llama)이 4096 한도 도달 — 복잡한 다관점 분석은 토큰 소모가 큼

#### 4. Technical Translation 한→영 (CAP 정리 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 1.07s | 101 | 586자 | $0.000268 | 자연 종료 |
| Ministral 8B | 1.29s | 180 | 915자 | $0.000038 | 자연 종료 |
| Nova 2 Lite | 4.12s | 488 | 1,746자 | $0.000132 | 자연 종료 |
| Claude Haiku 4.5 | 4.62s | 265 | 956자 | $0.001666 | 자연 종료 |
| Llama 3.2 11B | 84.50s | 4,096 | 9,235자 | $0.000688 | **한도 도달** |

- **최고 속도**: Qwen 3 32B (1.07s)
- **최저 비용**: Ministral 8B ($0.000038)
- 번역 태스크는 대부분 모델이 짧은 출력으로 자연 종료
- Llama 3.2는 번역 후 불필요한 부연 설명을 대량 생성하여 84.50s 소요 (이상치)

#### 5. Technical Translation EN-KO 영→한 (Observability 기술 문서)

| 모델 | Latency | 출력 토큰 | 응답 길이 | 비용 | 비고 |
|------|---------|----------|----------|------|------|
| Qwen 3 32B | 3.38s | 339 | 578자 | $0.000602 | 자연 종료 |
| Claude Haiku 4.5 | 3.98s | 533 | 590자 | $0.002875 | 자연 종료 |
| Ministral 8B | 4.30s | 877 | 1,881자 | $0.000106 | 자연 종료 |
| Nova 2 Lite | 5.29s | 774 | 1,515자 | $0.000199 | 자연 종료 |
| Llama 3.2 11B | 55.45s | 4,096 | 10,897자 | $0.000683 | **한도 도달** |

- **최고 속도**: Qwen 3 32B (3.38s)
- **최저 비용**: Ministral 8B ($0.000106)
- 영→한 번역도 Llama 3.2만 한도 도달 — 번역 외 부가 콘텐츠를 과다 생성하는 패턴

### 처리량 분석 (출력 토큰/초)

| 모델 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 | 평균 |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| Ministral 8B | 281.0 | 278.6 | 281.3 | 139.5 | 203.9 | **236.9** |
| Llama 3.2 11B | 166.1 | 169.8 | 166.9 | 48.5 | 73.9 | **125.0** |
| Nova 2 Lite | 139.4 | 167.2 | 159.7 | 118.4 | 146.3 | **146.2** |
| Qwen 3 32B | 89.1 | 139.9 | 98.7 | 94.4 | 100.3 | **104.5** |
| Claude Haiku 4.5 | 152.4 | 166.3 | 122.7 | 57.4 | 133.9 | **126.5** |

- **Ministral 8B**이 전 테스트에서 가장 높은 처리량 (평균 236.9 tok/s)
- **Llama 3.2 11B**는 토큰 자체는 많이 생성하지만 latency가 길어 번역 태스크에서 처리량 급감

### 비용 효율성 분석 (품질점/달러, Complex Reasoning 기준)

| 모델 | 비용 | 품질 평균 | 점수/$ |
|------|------|----------|--------|
| Ministral 8B | $0.000388 | 7.8 | **20,103** |
| Llama 3.2 11B | $0.000683 | 3.0 | 4,392 |
| Nova 2 Lite | $0.000633 | 7.5 | **11,848** |
| Qwen 3 32B | $0.003555 | 7.0 | 1,969 |
| Claude Haiku 4.5 | $0.020767 | 7.3 | 351 |

- **Ministral 8B**가 달러당 품질점에서 압도적 1위
- **Nova 2 Lite**가 2위로, 비용 대비 품질이 우수
- **Haiku 4.5**는 품질 자체는 상위권이나 출력 단가($5/1M)가 높아 효율이 낮음

### 테스트 유형별 우승 모델

| 기준 | Complex Reasoning | Code Gen | Analysis | 번역 한→영 | 번역 영→한 |
|------|:-:|:-:|:-:|:-:|:-:|
| 최고 속도 | Ministral 8B | Ministral 8B | Ministral 8B | Qwen 3 32B | Qwen 3 32B |
| 최저 비용 | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B | Ministral 8B |

- **속도**: Ministral 8B가 추론·코드·분석에서 1위, 번역에서는 Qwen 3 32B가 1위
- **비용**: 전 테스트에서 Ministral 8B가 최저 비용

### Complex Reasoning 품질 평가 상세 (Opus 4.6 코멘트 전문)

**Ministral 8B** (정확성 7 / 구체성 8 / 구조화 9 / 실용성 7)
> 전체적으로 체계적이고 광범위한 기술 스택을 다루고 있으나, 99.99% SLA의 허용 다운타임을 ~53분(실제 ~52.6분/년)으로 잘못 표기했고, 멀티클라우드(EKS/GKE/AKS 혼용) 전략의 운영 복잡성과 비용에 대한 현실적 트레이드오프 분석이 부족하며, CockroachDB의 대륙 간 쓰기 레이턴시가 100ms 이하를 충족하기 어려운 점 등 일부 기술적 깊이와 실현 가능성 검증이 미흡합니다.

**Nova 2 Lite** (정확성 7 / 구체성 7 / 구조화 9 / 실용성 7)
> 체계적이고 포괄적인 구조로 핵심 요소들을 잘 정리했으나, CRDT와 CQRS의 혼용, 멀티클라우드와 AWS 단일 의존의 모순, Active-Active 구성에서의 데이터 주권과 동기화 간 트레이드오프 분석 부족, 99.99% SLA 달성을 위한 구체적 장애 시나리오 및 RTO/RPO 수치 미제시, 레이턴시 100ms 달성 근거(네트워크 홉별 지연 분석) 부재 등 실무 적용 시 깊이가 아쉬운 부분이 있다.

**Claude Haiku 4.5** (정확성 7 / 구체성 8 / 구조화 8 / 실용성 6)
> 다중 지역 아키텍처와 기술 스택을 체계적으로 제시하고 코드 예시까지 포함했으나, Active-Active 구성에서의 충돌 해결(CRDT 등) 전략 부재, 레거시 통합(우선순위 4)에 대한 구체적 설명 누락, 의사 코드 수준의 혼합 언어(Python 주석 안에 Node.js 코드) 등 실무 적용 시 보완이 필요하며 응답이 중간에 잘려 완결성이 떨어집니다.

**Qwen 3 32B** (정확성 7 / 구체성 6 / 구조화 9 / 실용성 6)
> 체계적인 구조와 포괄적인 범위 커버는 우수하나, 99.99% 가용성 달성을 위한 구체적 failover/DR 전략(멀티리전 active-active, RTO/RPO 수치 등)이 부족하고, 레이턴시 100ms 달성을 위한 WebSocket/CRDT 등 실시간 협업 핵심 기술 언급이 없으며, 셰딩/셸들링 등 오타와 부정확한 용어 사용, Aurora Global DB의 쓰기 지연 한계 미언급 등 기술적 깊이와 정확성에서 아쉬움이 있다.

**Llama 3.2 11B** (정확성 4 / 구체성 3 / 구조화 2 / 실용성 3)
> 핵심 요소들을 나열했으나 우선순위 제시가 없고, 각 기술 스택을 3대 클라우드별로 단순 나열하는 수준에 그쳤으며, 99.99% 가용성 달성을 위한 구체적 설계(멀티리전 페일오버, CRDT, 데이터 복제 전략 등)와 100ms 레이턴시 보장 전략이 부재하고, PlantUML 다이어그램이 무한 반복되는 치명적 생성 오류가 응답의 신뢰성을 크게 훼손합니다.

### 종합 분석

**가성비 최강 — Ministral 8B**: 5개 테스트 중 3개에서 최고 속도, 전 테스트 최저 비용, Complex Reasoning 품질 평가에서도 1위. 8B 파라미터로 가장 작은 모델이지만, 한국어 복합 추론에서 32B Qwen을 능가하는 결과를 보여 경량 모델의 한계를 재정의함.

**균형형 — Nova 2 Lite**: 속도 2위, 비용 2위, 품질 2위로 전 영역에서 안정적 상위권. 출력 단가($0.24/1M)가 저렴하여 대량 호출에 적합. 응답이 자연 종료되는 비율이 높아 불필요한 토큰 낭비가 적음.

**구조화 특화 — Qwen 3 32B**: 구조화 점수 9점으로 최고. 번역 태스크에서 가장 빠른 응답(1.07s). 그러나 32B 파라미터 대비 추론·분석 태스크에서의 품질 우위가 뚜렷하지 않아, 구조화된 출력이 필요한 특정 유스케이스에 적합.

**품질 투자형 — Claude Haiku 4.5**: 코드 예시, 의사 코드 등 가장 풍부한 포맷의 응답을 생성하지만, 출력 단가($5/1M)가 타 모델 대비 20~50배 높음. 응답 품질 자체는 상위권이나 비용 효율(351 점/$)은 최하위. 품질이 최우선인 프로덕션 환경에서 고려.

**주의 필요 — Llama 3.2 11B**: 모든 테스트에서 4096 토큰 한도에 도달하며, 번역 태스크에서 84.50s(최장)를 기록. Complex Reasoning에서 PlantUML 다이어그램 무한 반복 오류, 번역에서 불필요한 부연 설명 과다 생성 등 출력 제어 능력이 부족. 비용은 저렴하나 품질 대비 효율이 낮음.

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
