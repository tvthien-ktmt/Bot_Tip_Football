.PHONY: test backtest predict audit

test:
	python -m pytest backend/tests -v

backtest:
	python -m backend.cli backtest --mode T-24h

predict:
	python -m backend.cli predict --mode T-24h --div ALL

audit:
	python -m backend.cli audit
