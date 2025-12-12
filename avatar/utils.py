"""
Utility functions extracted from DreamBooth_Stable_Diffusion.ipynb for testing.
These are testable Python functions that support the notebook workflow.
"""
import os
import json
from typing import List, Dict, Any
from pathlib import Path


def create_concepts_list(
    instance_name: str,
    class_name: str,
    base_data_dir: str = "/content/data"
) -> List[Dict[str, str]]:
    """
    Create a concepts list configuration for DreamBooth training.
    
    Args:
        instance_name: Unique identifier for the subject (e.g., 'nitsuah')
        class_name: General class category (e.g., 'man', 'woman', 'person')
        base_data_dir: Base directory for training data
        
    Returns:
        List of concept dictionaries with prompts and data directories
    """
    return [
        {
            "instance_prompt": f"photo of {instance_name} {class_name}",
            "class_prompt": f"photo of a {class_name}",
            "instance_data_dir": f"{base_data_dir}/{instance_name}",
            "class_data_dir": f"{base_data_dir}/{class_name}"
        }
    ]


def save_concepts_json(concepts_list: List[Dict[str, str]], filepath: str) -> None:
    """
    Save concepts list to JSON file.
    
    Args:
        concepts_list: List of concept configurations
        filepath: Path to save JSON file
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(concepts_list, f, indent=4)


def load_concepts_json(filepath: str) -> List[Dict[str, str]]:
    """
    Load concepts list from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        List of concept configurations
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def create_instance_directories(concepts_list: List[Dict[str, str]]) -> None:
    """
    Create instance data directories for all concepts.
    
    Args:
        concepts_list: List of concept configurations
    """
    for concept in concepts_list:
        os.makedirs(concept["instance_data_dir"], exist_ok=True)


def validate_concept_structure(concept: Dict[str, str]) -> bool:
    """
    Validate that a concept dictionary has all required fields.
    
    Args:
        concept: Concept dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = [
        "instance_prompt",
        "class_prompt",
        "instance_data_dir",
        "class_data_dir"
    ]
    return all(field in concept for field in required_fields)


def calculate_recommended_training_steps(num_images: int, base_steps: int = 100) -> int:
    """
    Calculate recommended training steps based on number of images.
    Rule of thumb: 100 steps per image + base of 100.
    
    Args:
        num_images: Number of training images
        base_steps: Base number of steps (default: 100)
        
    Returns:
        Recommended number of training steps
    """
    return (num_images * 100) + base_steps


def count_images_in_directory(directory: str, extensions: tuple = ('.jpg', '.jpeg', '.png')) -> int:
    """
    Count image files in a directory.
    
    Args:
        directory: Directory path
        extensions: Tuple of valid image extensions
        
    Returns:
        Number of image files found
    """
    if not os.path.exists(directory):
        return 0
    
    count = 0
    for file in os.listdir(directory):
        if file.lower().endswith(extensions):
            count += 1
    return count


def validate_image_count(directory: str, min_images: int = 3, max_images: int = 10) -> tuple:
    """
    Validate that image count is within recommended range.
    
    Args:
        directory: Directory to check
        min_images: Minimum recommended images
        max_images: Maximum recommended images
        
    Returns:
        Tuple of (is_valid, count, message)
    """
    count = count_images_in_directory(directory)
    
    if count < min_images:
        return (False, count, f"Too few images. Found {count}, recommended minimum is {min_images}")
    elif count > max_images:
        return (False, count, f"Too many images. Found {count}, recommended maximum is {max_images}")
    else:
        return (True, count, f"Image count is optimal: {count} images")


def build_training_command(
    model_name: str,
    output_dir: str,
    concepts_file: str,
    max_train_steps: int,
    save_sample_prompt: str,
    resolution: int = 512,
    train_batch_size: int = 1,
    learning_rate: float = 1e-6
) -> str:
    """
    Build the accelerate launch command for DreamBooth training.
    
    Args:
        model_name: Pretrained model name or path
        output_dir: Output directory for trained weights
        concepts_file: Path to concepts_list.json
        max_train_steps: Maximum training steps
        save_sample_prompt: Prompt for generating sample images
        resolution: Training resolution (default: 512)
        train_batch_size: Batch size (default: 1)
        learning_rate: Learning rate (default: 1e-6)
        
    Returns:
        Training command string
    """
    cmd = f"""accelerate launch train_dreambooth.py \\
  --pretrained_model_name_or_path={model_name} \\
  --pretrained_vae_name_or_path="stabilityai/sd-vae-ft-mse" \\
  --output_dir={output_dir} \\
  --revision="fp16" \\
  --with_prior_preservation --prior_loss_weight=1.0 \\
  --seed=1337 \\
  --resolution={resolution} \\
  --train_batch_size={train_batch_size} \\
  --train_text_encoder \\
  --mixed_precision="fp16" \\
  --use_8bit_adam \\
  --gradient_accumulation_steps=1 \\
  --learning_rate={learning_rate} \\
  --lr_scheduler="constant" \\
  --lr_warmup_steps=0 \\
  --num_class_images=50 \\
  --sample_batch_size=4 \\
  --max_train_steps={max_train_steps} \\
  --save_interval=10000 \\
  --save_sample_prompt="{save_sample_prompt}" \\
  --concepts_list="{concepts_file}" """
    
    return cmd.strip()
