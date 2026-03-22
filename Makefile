.PHONY: run stop sanitize index scrape install test clean

run:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

stop:
	@pkill -f "uvicorn src.api:app" && echo "서버 종료됨" || echo "실행 중인 서버 없음"

sanitize:
	python3 scripts/sanitize_corpus.py

index:
	python3 scripts/build_index.py

scrape:
	python3 scripts/scrape_docs.py

install:
	pip install -r requirements.txt

test:
	python3 scripts/test_multiturn.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	echo "캐시 정리 완료"
