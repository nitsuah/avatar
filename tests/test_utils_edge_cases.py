"""
Edge case tests for avatar utilities.
"""
import os
import pytest
from pathlib import Path
from avatar import utils


def _create_test_image(path: Path):
    """Create a minimal valid test image using Pillow."""
    from PIL import Image
    img = Image.new('RGB', (4, 4), color='red')
    img.save(path)


class TestTrainingStepsTierBoundaries:
    """Tests for calculate_recommended_training_steps at tier boundaries."""

    @pytest.mark.parametrize("num_images,expected_steps", [
        (0, 0),
        (5, 500),
        (6, 420),
        (10, 700),
        (11, 550),
        (20, 1000),
        (21, 630),
    ])
    def test_training_steps_tier_boundaries(self, num_images, expected_steps):
        assert utils.calculate_recommended_training_steps(num_images) == expected_steps


class TestValidateImageCountBounds:
    """Tests for validate_image_count at exact boundary values."""

    def test_exactly_min_images_is_valid(self, tmp_path):
        """Exactly 3 images (default min) is valid."""
        for i in range(3):
            _create_test_image(tmp_path / f"img{i}.jpg")
        ok, count, msg = utils.validate_image_count(str(tmp_path))
        assert ok is True
        assert count == 3
        assert "optimal" in msg.lower()

    def test_exactly_max_images_is_valid(self, tmp_path):
        """Exactly 10 images (default max) is valid."""
        for i in range(10):
            _create_test_image(tmp_path / f"img{i}.jpg")
        ok, count, msg = utils.validate_image_count(str(tmp_path))
        assert ok is True
        assert count == 10
        assert "optimal" in msg.lower()

    def test_custom_bounds_too_many(self, tmp_path):
        """With min=1, max=2, three images gives 'Too many' message."""
        for i in range(3):
            _create_test_image(tmp_path / f"img{i}.jpg")
        ok, count, msg = utils.validate_image_count(str(tmp_path), min_images=1, max_images=2)
        assert ok is False
        assert count == 3
        assert "too many" in msg.lower()


class TestCountImagesFallbackPath:
    """Tests for count_images_in_directory when Pillow is not available (fallback path)."""

    def test_fallback_counts_by_extension_case_insensitive(self, tmp_path, monkeypatch):
        """Fallback counts by extension, case-insensitive."""
        monkeypatch.setattr(utils, 'Image', None)

        (tmp_path / "a.JPG").touch()
        (tmp_path / "b.png").touch()
        (tmp_path / "c.txt").touch()
        (tmp_path / "d.jpg").write_bytes(b"x")  # corrupt

        count = utils.count_images_in_directory(str(tmp_path))
        assert count == 3  # a.JPG, b.png, d.jpg (by extension)

    def test_fallback_ignores_subdirectory_named_like_image(self, tmp_path, monkeypatch):
        """A subdirectory named e.png is not counted."""
        monkeypatch.setattr(utils, 'Image', None)

        (tmp_path / "e.png").mkdir()

        count = utils.count_images_in_directory(str(tmp_path))
        assert count == 0


class TestCountImagesWithPillow:
    """Tests for count_images_in_directory with Pillow available."""

    def test_uppercase_extension_counted(self, tmp_path):
        """Uppercase extensions (A.PNG) are counted with Pillow."""
        _create_test_image(tmp_path / "A.PNG")
        count = utils.count_images_in_directory(str(tmp_path))
        assert count == 1

    def test_directory_named_like_image_not_counted(self, tmp_path):
        """A directory named dir.png is not counted."""
        (tmp_path / "dir.png").mkdir()
        count = utils.count_images_in_directory(str(tmp_path))
        assert count == 0


class TestBuildTrainingCommand:
    """Tests for build_training_command output."""

    def test_command_contains_revision_fp16(self):
        cmd = utils.build_training_command(
            model_name="model",
            output_dir="/out",
            concepts_file="concepts.json",
            max_train_steps=1000,
            save_sample_prompt="prompt"
        )
        assert '--revision="fp16"' in cmd

    def test_command_contains_seed_1337(self):
        cmd = utils.build_training_command(
            model_name="model",
            output_dir="/out",
            concepts_file="concepts.json",
            max_train_steps=1000,
            save_sample_prompt="prompt"
        )
        assert "--seed=1337" in cmd

    def test_command_contains_save_sample_prompt_in_double_quotes(self):
        cmd = utils.build_training_command(
            model_name="model",
            output_dir="/out",
            concepts_file="concepts.json",
            max_train_steps=1000,
            save_sample_prompt="a photo"
        )
        assert '--save_sample_prompt="a photo"' in cmd


class TestValidateConceptStructure:
    """Tests for validate_concept_structure edge cases."""

    def test_accepts_dict_with_extra_key(self):
        """Accepts a dict with all required keys plus an extra key."""
        concept = {
            "instance_prompt": "photo of user person",
            "class_prompt": "photo of a person",
            "instance_data_dir": "/path/to/instance",
            "class_data_dir": "/path/to/class",
            "extra_key": "ignored"
        }
        assert utils.validate_concept_structure(concept) is True

    def test_rejects_missing_only_class_prompt(self):
        """Rejects a dict missing only class_prompt."""
        concept = {
            "instance_prompt": "photo of user person",
            "instance_data_dir": "/path/to/instance",
            "class_data_dir": "/path/to/class"
            # Missing class_prompt
        }
        assert utils.validate_concept_structure(concept) is False