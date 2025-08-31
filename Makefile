PY ?= python3

.PHONY: help standard run

help:
	@echo "Targets:"
	@echo "  standard   Run preset standard (json + covers)"
	@echo "  run        Run module with ARGS='...' (e.g., ARGS=\"--author 'Murakami' 'Norwegian Wood'\")"

standard:
	$(PY) -m book_fetcher --preset standard

run:
	$(PY) -m book_fetcher $(ARGS)

