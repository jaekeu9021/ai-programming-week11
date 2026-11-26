import pytest

from load_scores import load_scores


def write_csv(path, content):
	path.write_text(content, encoding="utf-8")
	return path


def test_loads_valid_rows(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,88\nLee,75\n")

	kept, skipped = load_scores(path)

	assert kept == [("Kim", 88), ("Lee", 75)]
	assert skipped == []


def test_accepts_inclusive_score_boundaries(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nMin,0\nMax,100\n")

	kept, skipped = load_scores(path)

	assert kept == [("Min", 0), ("Max", 100)]
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


def test_row_with_too_few_columns_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim", "열 개수가 2가 아님")]


def test_row_with_too_many_columns_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,80,note\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim,80,note", "열 개수가 2가 아님")]


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


def test_score_below_minimum_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,-1\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim,-1", "점수가 0~100 밖")]


def test_score_above_maximum_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\nKim,101\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "Kim,101", "점수가 0~100 밖")]


def test_empty_name_is_skipped(tmp_path):
	path = write_csv(tmp_path / "scores.csv", "name,score\n   ,80\n")

	kept, skipped = load_scores(path)

	assert kept == []
	assert skipped == [(2, "   ,80", "이름이 비어 있음")]


def test_blank_lines_are_ignored_and_bom_and_quoted_names_are_supported(tmp_path):
	path = tmp_path / "scores.csv"
	path.write_bytes("\ufeffname,score\n\n\"Choi, Hana\",77\n\n".encode("utf-8"))

	kept, skipped = load_scores(path)

	assert kept == [("Choi, Hana", 77)]
	assert skipped == []
