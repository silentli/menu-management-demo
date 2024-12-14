import pytest
import json

@pytest.fixture
def create_mock_file(tmp_path):
    """Creates a mock file with the given data and returns its path."""
    def _create_file(file_name: str, data):
        file_path = tmp_path / file_name
        if isinstance(data, (list, dict)):
            file_path.write_text(json.dumps(data))  # Write JSON data
        else:
            file_path.write_text(data)  # Write raw string data
        return str(file_path)
    return _create_file