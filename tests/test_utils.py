"""
Test suite for avatar utilities extracted from the DreamBooth notebook.
"""
import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from avatar.utils import (
    create_concepts_list,
    save_concepts_json,
    load_concepts_json,
    create_instance_directories,
    validate_concept_structure,
    calculate_recommended_training_steps,
    count_images_in_directory,
    validate_image_count,
    build_training_command
)


class TestConceptsManagement:
    """Tests for concepts list creation and management"""
    
    def test_create_concepts_list_basic(self):
        """Test basic concepts list creation"""
        concepts = create_concepts_list("testuser", "person")
        
        assert len(concepts) == 1
        assert concepts[0]["instance_prompt"] == "photo of testuser person"
        assert concepts[0]["class_prompt"] == "photo of a person"
        assert "testuser" in concepts[0]["instance_data_dir"]
        assert "person" in concepts[0]["class_data_dir"]
    
    def test_create_concepts_list_custom_base_dir(self):
        """Test concepts list with custom base directory"""
        concepts = create_concepts_list("nitsuah", "man", base_data_dir="/custom/path")
        
        assert concepts[0]["instance_data_dir"] == "/custom/path/nitsuah"
        assert concepts[0]["class_data_dir"] == "/custom/path/man"
    
    def test_save_and_load_concepts_json(self, tmp_path):
        """Test saving and loading concepts to/from JSON"""
        concepts = create_concepts_list("testuser", "person")
        filepath = tmp_path / "concepts_test.json"
        
        save_concepts_json(concepts, str(filepath))
        
        assert filepath.exists()
        
        loaded_concepts = load_concepts_json(str(filepath))
        assert loaded_concepts == concepts
    
    def test_concepts_json_format(self, tmp_path):
        """Test that saved JSON is properly formatted"""
        concepts = create_concepts_list("nitsuah", "man")
        filepath = tmp_path / "concepts.json"
        
        save_concepts_json(concepts, str(filepath))
        
        with open(filepath, "r") as f:
            content = f.read()
            # Check it's properly indented
            assert "    " in content
            # Check all keys are present
            assert "instance_prompt" in content
            assert "class_prompt" in content


class TestDirectoryManagement:
    """Tests for directory creation and management"""
    
    def test_create_instance_directories(self, tmp_path):
        """Test creating instance directories from concepts list"""
        concepts = create_concepts_list("testuser", "person", base_data_dir=str(tmp_path))
        
        create_instance_directories(concepts)
        
        assert os.path.exists(concepts[0]["instance_data_dir"])
    
    def test_create_directories_idempotent(self, tmp_path):
        """Test that creating directories multiple times doesn't error"""
        concepts = create_concepts_list("testuser", "person", base_data_dir=str(tmp_path))
        
        create_instance_directories(concepts)
        create_instance_directories(concepts)  # Should not raise error
        
        assert os.path.exists(concepts[0]["instance_data_dir"])


class TestConceptValidation:
    """Tests for concept structure validation"""
    
    def test_validate_concept_structure_valid(self):
        """Test validation of valid concept"""
        concept = {
            "instance_prompt": "photo of user person",
            "class_prompt": "photo of a person",
            "instance_data_dir": "/path/to/instance",
            "class_data_dir": "/path/to/class"
        }
        
        assert validate_concept_structure(concept) is True
    
    def test_validate_concept_structure_missing_field(self):
        """Test validation catches missing fields"""
        concept = {
            "instance_prompt": "photo of user person",
            "class_prompt": "photo of a person",
            "instance_data_dir": "/path/to/instance"
            # Missing class_data_dir
        }
        
        assert validate_concept_structure(concept) is False
    
    def test_validate_concept_structure_empty(self):
        """Test validation of empty concept"""
        assert validate_concept_structure({}) is False


class TestTrainingStepsCalculation:
    """Tests for training steps calculations"""
    
    def test_calculate_training_steps_default(self):
        """Test default training steps calculation"""
        steps = calculate_recommended_training_steps(6)
        assert steps == 700  # 6 * 100 + 100
    
    def test_calculate_training_steps_single_image(self):
        """Test calculation with single image"""
        steps = calculate_recommended_training_steps(1)
        assert steps == 200  # 1 * 100 + 100
    
    def test_calculate_training_steps_many_images(self):
        """Test calculation with many images"""
        steps = calculate_recommended_training_steps(10)
        assert steps == 1100  # 10 * 100 + 100
    
    def test_calculate_training_steps_custom_base(self):
        """Test calculation with custom base steps"""
        steps = calculate_recommended_training_steps(5, base_steps=200)
        assert steps == 700  # 5 * 100 + 200


class TestImageCounting:
    """Tests for image counting and validation"""
    
    def test_count_images_empty_directory(self, tmp_path):
        """Test counting in empty directory"""
        count = count_images_in_directory(str(tmp_path))
        assert count == 0
    
    def test_count_images_with_files(self, tmp_path):
        """Test counting actual image files"""
        # Create dummy image files
        (tmp_path / "image1.jpg").touch()
        (tmp_path / "image2.png").touch()
        (tmp_path / "image3.jpeg").touch()
        (tmp_path / "not_an_image.txt").touch()
        
        count = count_images_in_directory(str(tmp_path))
        assert count == 3
    
    def test_count_images_nonexistent_directory(self):
        """Test counting in nonexistent directory"""
        count = count_images_in_directory("/nonexistent/path")
        assert count == 0
    
    def test_validate_image_count_optimal(self, tmp_path):
        """Test validation with optimal image count"""
        for i in range(5):
            (tmp_path / f"image{i}.jpg").touch()
        
        is_valid, count, message = validate_image_count(str(tmp_path))
        
        assert is_valid is True
        assert count == 5
        assert "optimal" in message.lower()
    
    def test_validate_image_count_too_few(self, tmp_path):
        """Test validation with too few images"""
        (tmp_path / "image1.jpg").touch()
        
        is_valid, count, message = validate_image_count(str(tmp_path))
        
        assert is_valid is False
        assert count == 1
        assert "too few" in message.lower()
    
    def test_validate_image_count_too_many(self, tmp_path):
        """Test validation with too many images"""
        for i in range(15):
            (tmp_path / f"image{i}.jpg").touch()
        
        is_valid, count, message = validate_image_count(str(tmp_path))
        
        assert is_valid is False
        assert count == 15
        assert "too many" in message.lower()


class TestCommandBuilding:
    """Tests for training command generation"""
    
    def test_build_training_command_basic(self):
        """Test basic training command generation"""
        cmd = build_training_command(
            model_name="runwayml/stable-diffusion-v1-5",
            output_dir="/output",
            concepts_file="concepts.json",
            max_train_steps=1000,
            save_sample_prompt="photo of person"
        )
        
        assert "accelerate launch" in cmd
        assert "runwayml/stable-diffusion-v1-5" in cmd
        assert "--output_dir=/output" in cmd
        assert "--max_train_steps=1000" in cmd
        assert "photo of person" in cmd
    
    def test_build_training_command_custom_params(self):
        """Test command with custom parameters"""
        cmd = build_training_command(
            model_name="model",
            output_dir="/out",
            concepts_file="concepts.json",
            max_train_steps=500,
            save_sample_prompt="test prompt",
            resolution=768,
            train_batch_size=2,
            learning_rate=2e-6
        )
        
        assert "--resolution=768" in cmd
        assert "--train_batch_size=2" in cmd
        assert "--learning_rate=2e-06" in cmd
    
    def test_build_training_command_contains_required_flags(self):
        """Test that command includes all critical flags"""
        cmd = build_training_command(
            model_name="model",
            output_dir="/out",
            concepts_file="concepts.json",
            max_train_steps=1000,
            save_sample_prompt="prompt"
        )
        
        required_flags = [
            "--pretrained_model_name_or_path",
            "--with_prior_preservation",
            "--train_text_encoder",
            "--mixed_precision",
            "--use_8bit_adam"
        ]
        
        for flag in required_flags:
            assert flag in cmd


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_setup_workflow(self, tmp_path):
        """Test complete setup workflow from concepts to directories"""
        # Create concepts
        concepts = create_concepts_list("testuser", "person", base_data_dir=str(tmp_path))
        
        # Save to JSON
        concepts_file = tmp_path / "concepts.json"
        save_concepts_json(concepts, str(concepts_file))
        
        # Create directories
        create_instance_directories(concepts)
        
        # Verify everything exists
        assert concepts_file.exists()
        assert os.path.exists(concepts[0]["instance_data_dir"])
        
        # Load and verify
        loaded = load_concepts_json(str(concepts_file))
        assert validate_concept_structure(loaded[0])
    
    def test_training_preparation_workflow(self, tmp_path):
        """Test preparing for training with image validation"""
        # Setup
        instance_dir = tmp_path / "user" / "nitsuah"
        instance_dir.mkdir(parents=True)
        
        # Add images
        for i in range(6):
            (instance_dir / f"photo{i}.jpg").touch()
        
        # Validate
        is_valid, count, message = validate_image_count(str(instance_dir))
        assert is_valid
        
        # Calculate steps
        steps = calculate_recommended_training_steps(count)
        assert steps == 700
        
        # Build command
        cmd = build_training_command(
            model_name="model",
            output_dir=str(tmp_path / "output"),
            concepts_file="concepts.json",
            max_train_steps=steps,
            save_sample_prompt="photo of nitsuah person"
        )
        
        assert str(steps) in cmd
