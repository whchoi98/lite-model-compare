#!/usr/bin/env python3
"""Aggregate results from 5 test runs and compute averages."""
import json
import statistics

NUM_RUNS = 5
MODEL_KEYS = ['haiku-4.5', 'qwen-3.2', 'nova-2-lite', 'llama-3.2-11b', 'ministral-8b']
TEST_NAMES = ['Complex Reasoning', 'Advanced Code Generation', 'Multi-dimensional Analysis',
              'Technical Translation', 'Technical Translation EN-KO']

# 테스트명 → 품질평가 결과 파일 접두사 매핑
# Test name → quality result file prefix mapping
QUALITY_FILE_PREFIXES = {
    'Complex Reasoning': 'complex_reasoning',
    'Advanced Code Generation': 'advanced_code_generation',
    'Multi-dimensional Analysis': 'multi_dimensional_analysis',
    'Technical Translation': 'technical_translation',
    'Technical Translation EN-KO': 'technical_translation_en_ko',
}

def load_runs():
    runs = []
    for i in range(1, NUM_RUNS + 1):
        with open(f'comparison_results_run{i}.json') as f:
            runs.append(json.load(f))
    return runs

def load_quality_runs():
    """모든 테스트의 품질평가 결과를 로드합니다.
    Returns: {test_name: [run1_data, run2_data, ...]}"""
    quality_runs = {}
    for test_name, prefix in QUALITY_FILE_PREFIXES.items():
        runs = []
        for i in range(1, NUM_RUNS + 1):
            with open(f'{prefix}_results_run{i}.json') as f:
                runs.append(json.load(f))
        quality_runs[test_name] = runs
    return quality_runs

def aggregate_quality_for_test(quality_runs_for_test):
    """단일 테스트의 품질평가 결과를 모델별로 집계합니다."""
    quality_agg = {}
    for mk in MODEL_KEYS:
        accuracies = []
        specificities = []
        structures = []
        practicalities = []
        comments = []
        for qr in quality_runs_for_test:
            if mk in qr['models'] and 'quality_evaluation' in qr['models'][mk]:
                qe = qr['models'][mk]['quality_evaluation']
                if 'accuracy' not in qe:
                    continue
                accuracies.append(qe['accuracy'])
                specificities.append(qe['specificity'])
                structures.append(qe['structure'])
                practicalities.append(qe['practicality'])
                comments.append(qe.get('comment', ''))
        if accuracies:
            quality_agg[mk] = {
                'avg_accuracy': round(statistics.mean(accuracies), 1),
                'avg_specificity': round(statistics.mean(specificities), 1),
                'avg_structure': round(statistics.mean(structures), 1),
                'avg_practicality': round(statistics.mean(practicalities), 1),
                'avg_total': round(statistics.mean([
                    statistics.mean([a, s, st, p])
                    for a, s, st, p in zip(accuracies, specificities, structures, practicalities)
                ]), 1),
                'scores_per_run': [
                    {'accuracy': a, 'specificity': s, 'structure': st, 'practicality': p,
                     'avg': round((a + s + st + p) / 4, 1)}
                    for a, s, st, p in zip(accuracies, specificities, structures, practicalities)
                ],
                'comments': comments,
            }
    return quality_agg

def aggregate():
    runs = load_runs()
    all_quality_runs = load_quality_runs()

    # Per-test, per-model aggregation
    test_agg = {}
    for test_name in TEST_NAMES:
        test_agg[test_name] = {}
        for mk in MODEL_KEYS:
            latencies = []
            input_tokens_list = []
            output_tokens_list = []
            costs = []
            chars_list = []
            for run in runs:
                for t in run['tests']:
                    if t['test_name'] == test_name:
                        r = t['results'][mk]
                        latencies.append(r['latency_s'])
                        input_tokens_list.append(r['input_tokens'])
                        output_tokens_list.append(r['output_tokens'])
                        costs.append(r['cost_usd'])
                        chars_list.append(r['response_chars'])
            test_agg[test_name][mk] = {
                'avg_latency': round(statistics.mean(latencies), 2),
                'min_latency': round(min(latencies), 2),
                'max_latency': round(max(latencies), 2),
                'stdev_latency': round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
                'avg_input_tokens': round(statistics.mean(input_tokens_list)),
                'avg_output_tokens': round(statistics.mean(output_tokens_list)),
                'avg_cost': round(statistics.mean(costs), 6),
                'avg_chars': round(statistics.mean(chars_list)),
                'hit_limit_count': sum(1 for ot in output_tokens_list if ot >= 4096),
            }

    # Overall per-model aggregation
    overall = {}
    for mk in MODEL_KEYS:
        all_latencies = []
        total_costs = []
        all_tokens = []
        for run in runs:
            run_total_cost = 0
            run_latencies = []
            run_tokens = []
            for t in run['tests']:
                r = t['results'][mk]
                run_latencies.append(r['latency_s'])
                run_total_cost += r['cost_usd']
                run_tokens.append(r['input_tokens'] + r['output_tokens'])
            all_latencies.append(statistics.mean(run_latencies))
            total_costs.append(run_total_cost)
            all_tokens.append(statistics.mean(run_tokens))

        overall[mk] = {
            'avg_latency': round(statistics.mean(all_latencies), 2),
            'stdev_latency': round(statistics.stdev(all_latencies), 2) if len(all_latencies) > 1 else 0,
            'avg_total_cost': round(statistics.mean(total_costs), 6),
            'min_total_cost': round(min(total_costs), 6),
            'max_total_cost': round(max(total_costs), 6),
            'avg_tokens': round(statistics.mean(all_tokens)),
        }

    # Quality evaluation aggregation — 전체 테스트
    quality_per_test = {}
    for test_name in TEST_NAMES:
        quality_per_test[test_name] = aggregate_quality_for_test(all_quality_runs[test_name])

    # Throughput calculation (output tokens / latency)
    throughput = {}
    for mk in MODEL_KEYS:
        test_throughputs = {}
        for test_name in TEST_NAMES:
            tp_list = []
            for run in runs:
                for t in run['tests']:
                    if t['test_name'] == test_name:
                        r = t['results'][mk]
                        tp_list.append(r['output_tokens'] / r['latency_s'])
            test_throughputs[test_name] = round(statistics.mean(tp_list), 1)
        avg_tp = round(statistics.mean(list(test_throughputs.values())), 1)
        throughput[mk] = {**test_throughputs, 'average': avg_tp}

    result = {
        'num_runs': NUM_RUNS,
        'overall': overall,
        'quality_per_test': quality_per_test,
        'throughput': throughput,
        'per_test': test_agg,
    }

    with open('aggregated_results.json', 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Print summary
    print("=" * 70)
    print(f"AGGREGATED RESULTS ({NUM_RUNS} RUNS)")
    print("=" * 70)

    print("\n### Overall Average (5 runs)")
    sorted_by_latency = sorted(overall.items(), key=lambda x: x[1]['avg_latency'])
    print("\nSpeed Ranking:")
    for i, (mk, v) in enumerate(sorted_by_latency, 1):
        model_name = runs[0]['models'][mk]['name']
        print(f"  {i}. {model_name:20s} | Avg: {v['avg_latency']:.2f}s (±{v['stdev_latency']:.2f}s) | Tokens: {v['avg_tokens']}")

    sorted_by_cost = sorted(overall.items(), key=lambda x: x[1]['avg_total_cost'])
    print("\nCost Ranking:")
    for i, (mk, v) in enumerate(sorted_by_cost, 1):
        model_name = runs[0]['models'][mk]['name']
        print(f"  {i}. {model_name:20s} | Avg: ${v['avg_total_cost']:.6f} (min: ${v['min_total_cost']:.6f}, max: ${v['max_total_cost']:.6f})")

    # 전체 테스트 품질 순위 출력
    for test_name in TEST_NAMES:
        qa = quality_per_test[test_name]
        if not qa:
            continue
        print(f"\nQuality Ranking ({test_name}):")
        sorted_by_quality = sorted(qa.items(), key=lambda x: x[1]['avg_total'], reverse=True)
        for i, (mk, v) in enumerate(sorted_by_quality, 1):
            model_name = runs[0]['models'][mk]['name']
            scores = v['scores_per_run']
            score_str = ', '.join(f"{s['avg']}" for s in scores)
            print(f"  {i}. {model_name:20s} | Avg: {v['avg_total']:.1f} | 정확: {v['avg_accuracy']:.1f} 구체: {v['avg_specificity']:.1f} 구조: {v['avg_structure']:.1f} 실용: {v['avg_practicality']:.1f} | Per-run: [{score_str}]")

    print("\nThroughput (tok/s):")
    sorted_by_tp = sorted(throughput.items(), key=lambda x: x[1]['average'], reverse=True)
    for i, (mk, v) in enumerate(sorted_by_tp, 1):
        model_name = runs[0]['models'][mk]['name']
        print(f"  {i}. {model_name:20s} | Avg: {v['average']:.1f} tok/s")

    print("\n### Per-Test Details")
    for test_name in TEST_NAMES:
        print(f"\n{test_name}:")
        sorted_models = sorted(test_agg[test_name].items(), key=lambda x: x[1]['avg_latency'])
        for mk, v in sorted_models:
            model_name = runs[0]['models'][mk]['name']
            limit_str = f" [한도 도달 {v['hit_limit_count']}/{NUM_RUNS}회]" if v['hit_limit_count'] > 0 else ""
            print(f"  {model_name:20s} | {v['avg_latency']:.2f}s (±{v['stdev_latency']:.2f}) | Out: {v['avg_output_tokens']} tok | ${v['avg_cost']:.6f} | {v['avg_chars']}자{limit_str}")

if __name__ == '__main__':
    aggregate()
