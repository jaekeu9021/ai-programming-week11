import runpy
import sys
from pathlib import Path

import pytest

from load_scores import load_scores


def write_csv(path, content):
	path.write_text(content, encoding="utf-8")
	return path


def test_loads_valid_rows_and_inclusive_boundaries(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nMin,0\nLee,100\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 88), ("Min", 0), ("Lee", 100)]
	assert skipped == []


def test_keeps_duplicate_names(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nKim,91\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 88), ("Kim", 91)]
	assert skipped == []


def test_header_only_file_returns_empty_lists(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\n")

	assert load_scores(path) == ([], [])


def test_missing_file_raises_file_not_found_error(tmp_path):
	with pytest.raises(FileNotFoundError):
		load_scores(tmp_path / "missing.csv")


def test_wrong_column_counts_are_skipped(tmp_path):
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


def test_cli_accepts_path_argument_and_prints_results(tmp_path, monkeypatch, capsys):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nLee,101\n")
	monkeypatch.setattr(sys, "argv", ["load_scores.py", str(path)])

	runpy.run_path(str(Path(__file__).with_name("load_scores.py")), run_name="__main__")
	output = capsys.readouterr().out

	assert "읽은 줄 : 1개" in output
	assert "Kim 88" in output
	assert "건너뛴 줄 : 1개" in output
	assert "Lee,101" in output


def test_cli_defaults_to_scores_csv_in_current_directory(tmp_path, monkeypatch, capsys):
	write_csv(tmp_path / "scores.csv", "name,score\nPark,64\n")
	monkeypatch.chdir(tmp_path)
	monkeypatch.setattr(sys, "argv", ["load_scores.py"])

	runpy.run_path(str(Path(__file__).with_name("load_scores.py")), run_name="__main__")
	output = capsys.readouterr().out

	assert "읽은 줄 : 1개" in output
	assert "Park 64" in output
	assert "건너뛴 줄 : 0개" in output
