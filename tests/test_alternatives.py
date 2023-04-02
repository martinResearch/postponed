from joblib import delayed, Parallel


def repeat_string(s: str, n: int) -> str:
    return s * n


def test_joblib() -> None:
    postponed_repeat_string = delayed(repeat_string)
    # no error raised by mypy while it violates the repeat_string function signature
    p = postponed_repeat_string(s=1, n="a")
    result = Parallel(n_jobs=2)([p])
    assert result == ["a"]


if __name__ == "__main__":
    test_joblib()
