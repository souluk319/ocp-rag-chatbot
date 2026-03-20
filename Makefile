.PHONY: run stop index scrape install

run:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

stop:
	@pkill -f "uvicorn src.api:app" && echo "서버 종료됨" || echo "실행 중인 서버 없음"

index:
	python3 scripts/build_index.py

scrape:
	python3 scripts/scrape_docs.py

install:
	pip install -r requirements.txt
