"""Test that scripts import OK."""


def test_import_script_analyse_mission() -> None:
    """Test that `scripts.analyse_mission` imports OK."""
    # arrange
    # act
    from scripts import analyse_mission  # noqa: PLC0415 import-outside-top-level

    # assert
    assert analyse_mission


def test_import_script_analyse_missions() -> None:
    """Test that `scripts.analyse_missions` imports OK."""
    # arrange
    # act
    from scripts import analyse_missions  # noqa: PLC0415 import-outside-top-level

    # assert
    assert analyse_missions


def test_import_script_build_docs() -> None:
    """Test that `scripts.build_docs` imports OK."""
    # arrange
    # act
    from scripts import build_docs  # noqa: PLC0415 import-outside-top-level

    # assert
    assert build_docs
