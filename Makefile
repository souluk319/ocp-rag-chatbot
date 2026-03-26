PYTHON ?= python
PIP ?= pip

.PHONY: run stop sanitize index scrape install test test-stream test-multiturn test-contract test-fixture test-preflight clean

run:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

stop:
	@pkill -f "uvicorn src.api:app" && echo "서버 종료됨" || echo "실행 중인 서버 없음"

sanitize:
	$(PYTHON) scripts/sanitize_corpus.py

index:
	$(PYTHON) scripts/build_index.py

scrape:
	$(PYTHON) scripts/scrape_docs.py

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --format both --output data/eval_report.json

test-stream:
	$(PYTHON) scripts/eval_fixture_runner.py --fixture scripts/eval-fixture.seed.json --endpoint http://127.0.0.1:8000 --transport stream --format both --output data/eval_report_stream.json

test-multiturn:
	$(PYTHON) scripts/test_multiturn.py

test-contract:
	$(PYTHON) scripts/check_submission_contract.py

test-fixture:
	$(PYTHON) scripts/check_fixture_integrity.py

test-preflight:
	$(PYTHON) scripts/check_demo_preflight.py --endpoint http://127.0.0.1:8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	echo "캐시 정리 완료"
