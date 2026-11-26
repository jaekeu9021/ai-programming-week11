import runpy
import subprocess
import sys
from pathlib import Path

import pytest

from load_scores import load_scores


def write_csv(path, content):
	path.write_text(content, encoding="utf-8")
	return path


def test_loads_valid_rows_and_inclusive_boundaries(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nMin,0\nMax,100\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 88), ("Min", 0), ("Max", 100)]
	assert skipped == []


def test_keeps_duplicate_names(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,80\nKim,90\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 80), ("Kim", 90)]
	assert skipped == []


def test_header_only_file_returns_empty_lists(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\n")

	assert load_scores(path) == ([], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
	with pytest.raises(FileNotFoundError):
		load_scores(tmp_path / "missing.csv")


def test_rows_with_wrong_column_counts_are_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nSolo\nMany,80,note\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [
		(2, "Solo", "열 개수가 2가 아님"),
		(3, "Many,80,note", "열 개수가 2가 아님"),
	]


def test_empty_score_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,   \n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim,   ", "점수가 비어 있음")]


def test_non_integer_score_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,absent\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim,absent", "점수가 정수가 아님")]


def test_scores_outside_range_are_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nLow,-1\nHigh,101\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [
		(2, "Low,-1", "점수가 0~100 밖"),
		(3, "High,101", "점수가 0~100 밖"),
	]


def test_empty_name_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\n   ,80\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "   ,80", "이름이 비어 있음")]


def test_blank_lines_are_ignored(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\n\nKim,88\n\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 88)]
	assert skipped == []


def test_reads_utf8_bom_and_quoted_comma_in_name(tmp_path):
	path = tmp_path / "scores.csv"
	path.write_bytes("\ufeffname,score\n\"Choi, Hana\",77\n".encode("utf-8"))

	kept, skipped = load_scores(path)

	assert kept == [("Choi, Hana", 77)]
	assert skipped == []


def test_weird_csv_skips_real_invalid_rows():
	path = Path(__file__).with_name("weird.csv")

	kept, skipped = load_scores(path)

	assert kept == [("한겨울", 77), ("윤보람", 88)]
	assert skipped == [
		(2, ",90", "이름이 비어 있음"),
		(3, "서한별,", "점수가 비어 있음"),
		(4, "서한별,", "점수가 비어 있음"),
		(5, "김,쉼표,1000", "점수가 0~100 밖"),
		(6, "이두리,-100", "점수가 0~100 밖"),
		(7, "박세찬,88.5", "점수가 정수가 아님"),
		(9, "장미르,7 2", "점수가 정수가 아님"),
	]


def test_cli_runs_with_path_argument_and_reports_exit_and_output(tmp_path, monkeypatch, capsys):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nLee,101\n")
	script = Path(__file__).with_name("load_scores.py")
	process = subprocess.run(
		[sys.executable, str(script), str(path)],
		cwd=tmp_path,
		capture_output=True,
		text=True,
		check=False,
	)

	assert process.returncode == 0
	assert "읽은 줄 : 1개" in process.stdout
	assert "  Kim 88" in process.stdout
	assert "건너뛴 줄 : 1개" in process.stdout
	assert "Lee,101" in process.stdout
	assert process.stderr == ""

	monkeypatch.setattr(sys, "argv", [str(script), str(path)])
	runpy.run_path(str(script), run_name="__main__")
	assert "Kim 88" in capsys.readouterr().out
