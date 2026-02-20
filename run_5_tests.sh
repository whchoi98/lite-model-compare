#!/bin/bash
# 5회 반복 실행 스크립트
# Runs bedrock_model_comparison.py 5 times, renames outputs, then aggregates

set -e
cd "$(dirname "$0")"

QUALITY_PREFIXES=(
    "complex_reasoning"
    "advanced_code_generation"
    "multi_dimensional_analysis"
    "technical_translation"
    "technical_translation_en_ko"
)

for i in $(seq 1 5); do
    echo ""
    echo "########################################"
    echo "# RUN $i / 5"
    echo "########################################"
    echo ""

    python3 bedrock_model_comparison.py

    # comparison_results.json → comparison_results_run{i}.json
    mv comparison_results.json "comparison_results_run${i}.json"

    # 각 테스트별 품질평가 결과 파일 이름 변경
    for prefix in "${QUALITY_PREFIXES[@]}"; do
        mv "${prefix}_results.json" "${prefix}_results_run${i}.json"
    done

    echo ""
    echo ">>> Run $i complete. Files renamed with _run${i} suffix."
    echo ""
done

echo ""
echo "########################################"
echo "# AGGREGATING RESULTS"
echo "########################################"
echo ""

python3 aggregate_results.py

echo ""
echo ">>> All done. See aggregated_results.json"
