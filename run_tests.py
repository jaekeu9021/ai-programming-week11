import os
from pathlib import Path

import pytest


def main():
	week_dir = Path(__file__).resolve().parent
	os.chdir(week_dir)
	return pytest.main(
		[
			"test_load_scores.py",
			"--cov=load_scores",
			"--cov-report=term",
		]
	)


if __name__ == "__main__":
	raise SystemExit(main())