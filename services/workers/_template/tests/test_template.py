def test_template_imports():
    # Smoke test: file exists and can be imported by Python.
    # Template is stdlib-only.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "worker", "services/workers/_template/src/worker.py"
    )
    assert spec is not None
