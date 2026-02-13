#!/usr/bin/env python3
"""
AWS Bedrock 경량 모델 비교 테스트 도구
AWS Bedrock Lightweight Model Comparison Test Tool

5개의 경량 LLM 모델(Haiku, Qwen, Nova, Llama, Ministral)을 동일한 프롬프트로 호출하여
응답 속도, 토큰 사용량, 비용을 비교 측정합니다.

Invokes 5 lightweight LLM models (Haiku, Qwen, Nova, Llama, Ministral) with identical
prompts and compares response latency, token usage, and cost.
"""

import boto3
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple


class BedrockModelComparison:
    """
    AWS Bedrock 모델 비교 클래스
    AWS Bedrock Model Comparison Class

    여러 Bedrock 모델을 동일 프롬프트로 호출하고, 성능 지표를 수집·비교합니다.
    Invokes multiple Bedrock models with the same prompt and collects/compares performance metrics.
    """

    def __init__(self, region='us-east-1'):
        self.client = boto3.client('bedrock-runtime', region_name=region)

        # 모델 ID 및 가격 정보 (2026년 2월 기준, 1M 토큰당 USD)
        # Model IDs and pricing (as of Feb 2026, USD per 1M tokens)
        # 일부 모델은 inference profile ID를 사용해야 합니다 (us. prefix)
        # Some models require inference profile IDs (us. prefix)
        self.models = {
            'haiku-4.5': {
                'id': 'us.anthropic.claude-haiku-4-5-20251001-v1:0',
                'name': 'Claude Haiku 4.5',
                'input_price': 1.00,
                'output_price': 5.00,
                'format': 'claude'
            },
            'qwen-3.2': {
                'id': 'qwen.qwen3-32b-v1:0',
                'name': 'Qwen 3 32B',
                'input_price': 0.50,
                'output_price': 1.50,
                'format': 'qwen'
            },
            'nova-2-lite': {
                'id': 'us.amazon.nova-2-lite-v1:0',
                'name': 'Nova 2 Lite',
                'input_price': 0.06,
                'output_price': 0.24,
                'format': 'nova'
            },
            'llama-3.2-11b': {
                'id': 'us.meta.llama3-2-11b-instruct-v1:0',
                'name': 'Llama 3.2 11B',
                'input_price': 0.16,
                'output_price': 0.16,
                'format': 'llama'
            },
            'ministral-8b': {
                'id': 'mistral.ministral-3-8b-instruct',
                'name': 'Ministral 8B',
                'input_price': 0.10,
                'output_price': 0.10,
                'format': 'mistral'
            }
        }
        
        self.results = []
    
    def invoke_model(self, model_key: str, prompt: str, max_tokens: int = 4096) -> Dict:
        """
        단일 모델을 호출하고 성능 지표를 반환합니다.
        Invokes a single model and returns performance metrics.

        Args:
            model_key: 모델 식별 키 (예: 'haiku-4.5') / Model identifier key
            prompt: 입력 프롬프트 / Input prompt
            max_tokens: 최대 출력 토큰 수 / Maximum output tokens

        Returns:
            Dict: 성공 시 latency, tokens, cost 등 포함 / On success includes latency, tokens, cost, etc.
                  실패 시 error 메시지 포함 / On failure includes error message
        """
        model_info = self.models[model_key]

        # 모델별 요청 페이로드 구성 (각 provider마다 API 형식이 다름)
        # Build request payload per model (each provider has a different API format)
        if model_info['format'] == 'claude':
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        elif model_info['format'] == 'nova':
            payload = {
                "messages": [
                    {"role": "user", "content": [{"text": prompt}]}
                ],
                "inferenceConfig": {
                    "max_new_tokens": max_tokens
                }
            }
        elif model_info['format'] == 'llama':
            payload = {
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": 0.7
            }
        elif model_info['format'] == 'mistral':
            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
        else:  # Qwen
            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens
            }
        
        # 응답 시간 측정 시작 / Start latency measurement
        start_time = time.time()

        try:
            # Bedrock InvokeModel API 호출 / Call Bedrock InvokeModel API
            response = self.client.invoke_model(
                modelId=model_info['id'],
                body=json.dumps(payload)
            )

            # 응답 시간 계산 (초) / Calculate response time (seconds)
            latency = time.time() - start_time

            # 응답 본문 파싱 / Parse response body
            response_body = json.loads(response['body'].read())

            # 모델별 응답 형식 처리 (provider마다 JSON 구조가 다름)
            # Parse model-specific response format (JSON structure differs by provider)
            if model_info['format'] == 'claude':
                output_text = response_body['content'][0]['text']
                input_tokens = response_body['usage']['input_tokens']
                output_tokens = response_body['usage']['output_tokens']
            elif model_info['format'] == 'nova':
                output_text = response_body['output']['message']['content'][0]['text']
                input_tokens = response_body['usage']['inputTokens']
                output_tokens = response_body['usage']['outputTokens']
            elif model_info['format'] == 'llama':
                output_text = response_body['generation']
                input_tokens = response_body.get('prompt_token_count', len(prompt) // 4)
                output_tokens = response_body.get('generation_token_count', len(output_text) // 4)
            elif model_info['format'] == 'mistral':
                output_text = response_body['choices'][0]['message']['content']
                input_tokens = response_body['usage']['prompt_tokens']
                output_tokens = response_body['usage']['completion_tokens']
            else:  # Qwen
                output_text = response_body['choices'][0]['message']['content']
                input_tokens = response_body['usage']['prompt_tokens']
                output_tokens = response_body['usage']['completion_tokens']
            
            # 비용 계산 (토큰 수 × 1M 토큰당 가격)
            # Calculate cost (token count × price per 1M tokens)
            input_cost = (input_tokens / 1_000_000) * model_info['input_price']
            output_cost = (output_tokens / 1_000_000) * model_info['output_price']
            total_cost = input_cost + output_cost
            
            return {
                'success': True,
                'model': model_info['name'],
                'model_key': model_key,
                'latency': latency,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                'total_cost': total_cost,
                'output_text': output_text,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'model': model_info['name'],
                'model_key': model_key,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_test(self, prompt: str, test_name: str = "Test") -> Dict:
        """
        동일한 프롬프트로 등록된 모든 모델을 순차 호출합니다.
        Runs the same prompt against all registered models sequentially.
        """
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
        print(f"{'='*60}")
        print(f"Prompt: {prompt[:100]}...")
        print()
        
        results = {}
        
        for model_key in self.models.keys():
            print(f"Testing {self.models[model_key]['name']}...")
            result = self.invoke_model(model_key, prompt)
            results[model_key] = result
            
            if result['success']:
                print(f"  Done - {result['latency']:.2f}s, {result['total_tokens']} tokens, ${result['total_cost']:.6f}")
            else:
                print(f"  Failed - {result['error']}")
        
        # 테스트 결과 저장 / Store test result
        test_result = {
            'test_name': test_name,
            'prompt': prompt,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(test_result)
        
        return test_result
    
    def compare_results(self, test_result: Dict):
        """
        단일 테스트의 모델별 결과를 비교 출력합니다 (속도, 토큰, 비용, 응답 길이).
        Prints a comparison of model results for a single test (latency, tokens, cost, response length).
        """
        print(f"\n{'='*60}")
        print("Comparison Results")
        print(f"{'='*60}")
        
        results = test_result['results']
        
        # Latency comparison
        print(f"\nLatency:")
        models_latency = []
        for key, r in results.items():
            if r.get('success'):
                print(f"  {r['model']:20}: {r['latency']:.2f}s")
                models_latency.append((r['model'], r['latency']))
        
        if models_latency:
            fastest = min(models_latency, key=lambda x: x[1])
            print(f"  Fastest: {fastest[0]}")
        
        # Token usage
        print(f"\nToken Usage:")
        for key, r in results.items():
            if r.get('success'):
                print(f"  {r['model']:20}: {r['input_tokens']} in + {r['output_tokens']} out = {r['total_tokens']} total")
        
        # Cost comparison
        print(f"\nCost:")
        models_cost = []
        for key, r in results.items():
            if r.get('success'):
                print(f"  {r['model']:20}: ${r['total_cost']:.6f}")
                models_cost.append((r['model'], r['total_cost']))
        
        if models_cost:
            cheapest = min(models_cost, key=lambda x: x[1])
            print(f"  Cheapest: {cheapest[0]}")
        
        # Response length
        print(f"\nResponse Length:")
        for key, r in results.items():
            if r.get('success'):
                print(f"  {r['model']:20}: {len(r['output_text'])} chars")
    
    def save_results(self, filename: str = 'comparison_results.json'):
        """
        테스트 결과를 구조화된 JSON 파일로 저장합니다.
        Saves test results as a structured JSON file.

        JSON 구조 / JSON structure:
          - meta: 테스트 메타 정보 / Test metadata
          - models: 모델 ID, 가격 정보 / Model IDs and pricing
          - tests: 테스트별 모델 지표 및 순위 / Per-test metrics and rankings
          - summary: 모델별 평균 통계 및 종합 순위 / Per-model averages and overall rankings
        """
        # 모델 정보 구성 / Build model info section
        models_info = {}
        for key, m in self.models.items():
            models_info[key] = {
                "name": m['name'],
                "model_id": m['id'],
                "pricing_per_1M_tokens": {
                    "input": m['input_price'],
                    "output": m['output_price']
                }
            }

        # 테스트별 결과 구성 (성공 시 지표, 실패 시 에러 메시지)
        # Build per-test results (metrics on success, error message on failure)
        tests = []
        for test in self.results:
            test_entry = {
                "test_name": test['test_name'],
                "results": {}
            }
            for model_key, r in test['results'].items():
                if r.get('success'):
                    test_entry["results"][model_key] = {
                        "latency_s": round(r['latency'], 2),
                        "input_tokens": r['input_tokens'],
                        "output_tokens": r['output_tokens'],
                        "cost_usd": round(r['total_cost'], 6),
                        "response_chars": len(r['output_text'])
                    }
                else:
                    test_entry["results"][model_key] = {
                        "error": r.get('error', 'Unknown error')
                    }

            # 테스트별 순위 산출 (성공한 모델만 대상)
            # Determine per-test rankings (only successful models)
            successful = {k: v for k, v in test_entry["results"].items() if "latency_s" in v}
            if successful:
                test_entry["rankings"] = {
                    "fastest": min(successful, key=lambda k: successful[k]["latency_s"]),
                    "cheapest": min(successful, key=lambda k: successful[k]["cost_usd"])
                }
            tests.append(test_entry)

        # 모델별 평균 통계 집계 / Aggregate per-model average statistics
        all_stats = {key: {'latency': [], 'cost': [], 'tokens': []} for key in self.models}
        for test in self.results:
            for model_key in self.models:
                r = test['results'].get(model_key, {})
                if r.get('success'):
                    all_stats[model_key]['latency'].append(r['latency'])
                    all_stats[model_key]['cost'].append(r['total_cost'])
                    all_stats[model_key]['tokens'].append(r['total_tokens'])

        avg_per_model = {}  # 모델별 평균 latency, 총 비용, 평균 토큰 / Per-model avg latency, total cost, avg tokens
        for key, stats in all_stats.items():
            if stats['latency']:
                avg_per_model[key] = {
                    "avg_latency_s": round(sum(stats['latency']) / len(stats['latency']), 2),
                    "total_cost_usd": round(sum(stats['cost']), 6),
                    "avg_tokens": round(sum(stats['tokens']) / len(stats['tokens']))
                }

        # 종합 순위표 생성 (속도순, 비용순)
        # Build overall rankings (by latency, by cost)
        by_latency = sorted(avg_per_model.items(), key=lambda x: x[1]['avg_latency_s'])
        by_cost = sorted(avg_per_model.items(), key=lambda x: x[1]['total_cost_usd'])

        output = {
            "meta": {
                "title": "AWS Bedrock 경량 모델 비교 테스트",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "region": "us-east-1",
                "max_tokens": 4096,
                "total_tests": len(self.results)
            },
            "models": models_info,
            "tests": tests,
            "summary": {
                "average_per_model": avg_per_model,
                "rankings": {
                    "by_latency": [
                        {"rank": i+1, "model": self.models[k]['name'], "avg_latency_s": v['avg_latency_s']}
                        for i, (k, v) in enumerate(by_latency)
                    ],
                    "by_cost": [
                        {"rank": i+1, "model": self.models[k]['name'], "total_cost_usd": v['total_cost_usd']}
                        for i, (k, v) in enumerate(by_cost)
                    ]
                }
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved: {filename}")

    def evaluate_quality(self, test_result: Dict) -> Dict:
        """
        Opus 4.6을 호출하여 각 모델 응답의 품질을 평가합니다.
        Calls Opus 4.6 to evaluate the quality of each model's response.

        평가 기준 / Evaluation criteria:
          - 정확성 (Accuracy): 사실 관계 및 기술적 정확성 (1~10)
          - 구체성 (Specificity): 구체적 예시와 수치 포함 정도 (1~10)
          - 구조화 (Structure): 논리적 구성 및 가독성 (1~10)
          - 실용성 (Practicality): 실무 적용 가능성 (1~10)

        Args:
            test_result: run_test()가 반환한 테스트 결과 Dict

        Returns:
            Dict: 모델 키별 평가 결과 (scores + comment)
        """
        evaluations = {}
        prompt_text = test_result['prompt']

        for model_key, result in test_result['results'].items():
            if not result.get('success'):
                evaluations[model_key] = {
                    'error': 'Model invocation failed, skipping evaluation'
                }
                continue

            model_name = result['model']
            response_text = result['output_text']

            eval_prompt = f"""당신은 AI 모델 응답 품질 평가 전문가입니다. 아래 프롬프트에 대한 모델의 응답을 평가해주세요.

## 원본 프롬프트
{prompt_text}

## 모델 응답 ({model_name})
{response_text}

## 평가 기준
다음 4가지 기준으로 1~10점 채점하고, 마지막에 한줄 코멘트를 작성해주세요.
- 정확성 (Accuracy): 사실 관계 및 기술적 정확성
- 구체성 (Specificity): 구체적 예시, 수치, 구현 디테일 포함 정도
- 구조화 (Structure): 논리적 구성, 가독성, 체계적 전개
- 실용성 (Practicality): 실무에서 바로 적용 가능한 정도

## 출력 형식 (반드시 아래 JSON 형식으로만 응답)
{{"accuracy": <점수>, "specificity": <점수>, "structure": <점수>, "practicality": <점수>, "comment": "<한줄 코멘트>"}}"""

            print(f"  Evaluating {model_name} with Opus 4.6...")
            try:
                eval_payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "messages": [
                        {"role": "user", "content": eval_prompt}
                    ]
                }
                eval_response = self.client.invoke_model(
                    modelId='us.anthropic.claude-opus-4-6-v1',
                    body=json.dumps(eval_payload)
                )
                eval_body = json.loads(eval_response['body'].read())
                eval_text = eval_body['content'][0]['text']

                # JSON 부분 추출 (응답에 부가 텍스트가 있을 수 있음)
                # Extract JSON portion (response may contain extra text)
                json_start = eval_text.find('{')
                json_end = eval_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    eval_json = json.loads(eval_text[json_start:json_end])
                    evaluations[model_key] = eval_json
                else:
                    evaluations[model_key] = {'raw_response': eval_text}

            except Exception as e:
                evaluations[model_key] = {'error': str(e)}

        return evaluations

    def save_test_detail(self, test_result: Dict, evaluations: Dict, filename: str):
        """
        단일 테스트 결과를 품질 평가 포함하여 별도 JSON으로 저장합니다.
        Saves a single test result as a separate JSON file including quality evaluations.

        포함 내용 / Contents:
          - test_name, prompt: 테스트 이름 및 프롬프트
          - models: 모델별 성능 지표, 응답 전문, Opus 4.6 품질 평가
          - timestamp: 저장 시각

        Args:
            test_result: run_test()가 반환한 테스트 결과 Dict
            evaluations: evaluate_quality()가 반환한 평가 Dict
            filename: 저장할 JSON 파일명
        """
        detail = {
            "test_name": test_result['test_name'],
            "prompt": test_result['prompt'],
            "models": {},
            "timestamp": datetime.now().isoformat()
        }

        for model_key, result in test_result['results'].items():
            entry = {"model_name": self.models[model_key]['name']}

            if result.get('success'):
                entry["metrics"] = {
                    "latency_s": round(result['latency'], 2),
                    "input_tokens": result['input_tokens'],
                    "output_tokens": result['output_tokens'],
                    "total_tokens": result['total_tokens'],
                    "cost_usd": round(result['total_cost'], 6)
                }
                entry["response"] = result['output_text']
            else:
                entry["error"] = result.get('error', 'Unknown error')

            if model_key in evaluations:
                entry["quality_evaluation"] = evaluations[model_key]

            detail["models"][model_key] = entry

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)
        print(f"\nDetail results saved: {filename}")

    def print_summary(self):
        """
        전체 테스트의 모델별 평균 통계를 콘솔에 출력합니다.
        Prints per-model average statistics across all tests to the console.
        """
        print(f"\n{'='*60}")
        print("Overall Test Summary")
        print(f"{'='*60}")

        # 모든 모델에 대해 동적으로 통계 집계
        # Dynamically aggregate statistics for all models
        all_stats = {key: {'latency': [], 'cost': [], 'tokens': []} for key in self.models}

        for test in self.results:
            for model_key in self.models:
                result = test['results'].get(model_key, {})
                if result.get('success'):
                    all_stats[model_key]['latency'].append(result['latency'])
                    all_stats[model_key]['cost'].append(result['total_cost'])
                    all_stats[model_key]['tokens'].append(result['total_tokens'])

        print(f"\nTotal tests: {len(self.results)}")

        for model_key, stats in all_stats.items():
            if stats['latency']:
                name = self.models[model_key]['name']
                print(f"\n{name} Average:")
                print(f"  Latency: {sum(stats['latency'])/len(stats['latency']):.2f}s")
                print(f"  Total cost: ${sum(stats['cost']):.6f}")
                print(f"  Avg tokens: {sum(stats['tokens'])/len(stats['tokens']):.0f}")


def main():
    """
    메인 실행 함수: 5가지 테스트 케이스로 모델을 비교하고 결과를 저장합니다.
    Main entry point: compares models with 5 test cases and saves results.
    """
    comparison = BedrockModelComparison(region='us-east-1')

    # 테스트 케이스 정의 / Define test cases
    # 1. Complex Reasoning        - 복합 추론 (아키텍처 설계)
    # 2. Advanced Code Gen        - 고급 코드 생성 (LRU 캐시)
    # 3. Multi-dim Analysis       - 다각도 분석 (B2B 전환)
    # 4. Technical Translation    - 기술 번역 (한→영)
    # 5. Technical Translation EN-KO - 기술 번역 (영→한)
    test_cases = [
        {
            'name': 'Complex Reasoning',
            'prompt': '''다음 상황을 분석하고 해결책을 제시해주세요:

한 글로벌 기업이 3개 대륙(아시아, 유럽, 북미)에 분산된 팀으로 실시간 협업 플랫폼을 구축하려 합니다.
- 각 지역마다 데이터 주권 법규가 다름
- 평균 동시 접속자 50만명, 피크 시간대 200만명
- 99.99% 가용성 요구사항
- 레이턴시는 100ms 이하 유지 필요
- 기존 레거시 시스템 3개와 통합 필요

아키텍처 설계 시 고려해야 할 핵심 요소들을 우선순위와 함께 제시하고,
각 요소에 대한 구체적인 기술 스택과 구현 전략을 설명해주세요.'''
        },
        {
            'name': 'Advanced Code Generation',
            'prompt': '''다음 요구사항을 만족하는 Python 클래스를 작성해주세요:

1. LRU(Least Recently Used) 캐시를 구현하되, 다음 기능을 포함:
   - O(1) 시간복잡도로 get/put 연산
   - TTL(Time To Live) 지원 (각 항목마다 만료 시간 설정 가능)
   - 메모리 사용량 제한 (바이트 단위)
   - 통계 정보 제공 (hit rate, miss rate, eviction count)
   - Thread-safe 구현

2. 타입 힌팅 포함
3. 주요 메서드에 대한 docstring 작성
4. 간단한 사용 예제 포함'''
        },
        {
            'name': 'Multi-dimensional Analysis',
            'prompt': '''다음 비즈니스 시나리오를 다각도로 분석해주세요:

한 AI 스타트업이 B2B SaaS 모델로 전환을 고려 중입니다.
현재 상황:
- 현재 B2C 모델, 월 활성 사용자 10만명, 무료 사용자 95%
- 연간 매출 5억원, 운영비용 8억원 (적자 3억원)
- 개발팀 15명, 마케팅팀 5명, 영업팀 2명
- 주요 경쟁사 3곳이 이미 B2B 시장 선점
- 투자 유치 필요 (Series A, 목표 100억원)

다음 관점에서 분석하고 실행 계획을 제시해주세요:
1. 재무적 타당성 (손익분기점, 예상 CAC/LTV)
2. 조직 재편 전략 (인력 구조, 채용 계획)
3. 제품 전환 로드맵 (기능 우선순위, 마이그레이션 전략)
4. 시장 진입 전략 (타겟 고객, 가격 정책)
5. 리스크 요인과 완화 방안'''
        },
        {
            'name': 'Technical Translation',
            'prompt': '''다음 기술 문서를 자연스러운 영어로 번역하되, 기술 용어의 정확성을 유지해주세요:

"분산 시스템에서 CAP 정리는 일관성(Consistency), 가용성(Availability), 분할 내성(Partition Tolerance) 중
최대 2가지만 동시에 보장할 수 있다고 명시합니다. 실제 프로덕션 환경에서는 네트워크 분할이 불가피하므로,
대부분의 시스템은 일관성과 가용성 사이에서 트레이드오프를 선택해야 합니다.
이벤트 소싱과 CQRS 패턴을 활용하면 최종 일관성(Eventual Consistency)을 달성하면서도
높은 가용성을 유지할 수 있습니다. 다만, 이 경우 비즈니스 로직에서 일시적인 불일치 상태를
처리할 수 있는 보상 트랜잭션(Compensating Transaction) 메커니즘이 필요합니다."'''
        },
        {
            'name': 'Technical Translation EN-KO',
            'prompt': '''Translate the following technical document into natural, fluent Korean while maintaining the accuracy of technical terms:

"In modern cloud-native architectures, observability is achieved through three pillars: metrics, logs, and traces.
Metrics provide quantitative measurements of system behavior over time, typically collected via time-series databases
such as Prometheus or Amazon CloudWatch. Logs capture discrete events with contextual metadata, enabling post-hoc
debugging through centralized platforms like the ELK stack or Amazon OpenSearch. Distributed tracing, implemented
through standards like OpenTelemetry, correlates requests across microservice boundaries by propagating trace context
headers. Together, these pillars enable Site Reliability Engineers (SREs) to define Service Level Objectives (SLOs),
set error budgets, and implement automated incident response workflows. The key challenge lies in balancing the
cardinality of collected telemetry data against storage costs and query performance."'''
        }
    ]
    
    # 각 테스트 실행 후 비교 결과 출력 (테스트 간 1초 대기)
    # Complex Reasoning 결과는 별도 보관하여 품질 평가에 사용
    # Run each test, print comparison, and wait 1s between tests
    # Keep Complex Reasoning result for quality evaluation
    complex_reasoning_result = None

    for test_case in test_cases:
        result = comparison.run_test(test_case['prompt'], test_case['name'])
        comparison.compare_results(result)
        if test_case['name'] == 'Complex Reasoning':
            complex_reasoning_result = result
        time.sleep(1)

    # Complex Reasoning 결과를 Opus 4.6으로 품질 평가 후 별도 JSON 저장
    # Evaluate Complex Reasoning with Opus 4.6 and save as separate JSON
    if complex_reasoning_result:
        print(f"\n{'='*60}")
        print("Opus 4.6 Quality Evaluation (Complex Reasoning)")
        print(f"{'='*60}")
        evaluations = comparison.evaluate_quality(complex_reasoning_result)
        comparison.save_test_detail(
            complex_reasoning_result, evaluations, 'complex_reasoning_results.json'
        )

    # 전체 요약 출력 / Print overall summary
    comparison.print_summary()

    # 구조화된 JSON으로 결과 저장 / Save results as structured JSON
    comparison.save_results()


if __name__ == '__main__':
    main()
