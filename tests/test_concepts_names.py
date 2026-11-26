"""Name validation for create_concepts_list."""
import pytest

from avatar.utils import create_concepts_list

BAD_NAMES = ["", "  ", "a/b", "a" + "\x5c" + "b", "..", ".", "bad\x00name"]


@pytest.mark.parametrize("bad", BAD_NAMES)
def test_bad_instance_name_rejected(bad):
    with pytest.raises(ValueError):
        create_concepts_list(bad, "person")


@pytest.mark.parametrize("bad", BAD_NAMES)
def test_bad_class_name_rejected(bad):
    with pytest.raises(ValueError):
        create_concepts_list("testuser", bad)


def test_valid_names_still_work():
    assert create_concepts_list("testuser", "person") == [
        {
            "instance_prompt": "photo of testuser person",
            "class_prompt": "photo of a person",
            "instance_data_dir": "/content/data/testuser",
            "class_data_dir": "/content/data/person",
        }
    ]
