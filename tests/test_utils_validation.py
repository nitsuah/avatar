import pytest

from avatar.utils import calculate_recommended_training_steps


@pytest.mark.parametrize("num_images", [-1, -100])
def test_negative_image_counts_raise_value_error(num_images):
    with pytest.raises(ValueError, match="num_images"):
        calculate_recommended_training_steps(num_images)


def test_zero_images_returns_zero_steps():
    assert calculate_recommended_training_steps(0) == 0
