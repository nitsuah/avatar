"""
Utility functions extracted from DreamBooth_Stable_Diffusion.ipynb for testing.
These are testable Python functions that support the notebook workflow.
"""
import logging
import os
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)


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
        json.dump(concepts_list, f, indent=2)


def load_concepts_json(filepath: str) -> List[Dict[str, str]]:
    """
    Load concepts list from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        List of concept dictionaries
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_concept_structure(concept: Dict[str, str]) -> bool:
    """
    Validate that a concept dictionary has all required keys.

    Args:
        concept: Concept dictionary

    Returns:
        True if valid, False otherwise
    """
    required_keys = {"instance_prompt", "class_prompt", "instance_data_dir", "class_data_dir"}
    return all(key in concept for key in required_keys)


def create_instance_directories(concepts_list: List[Dict[str, str]]) -> None:
    """
    Create instance and class directories for all concepts.

    Args:
        concepts_list: List of concept configurations
    """
    for concept in concepts_list:
        os.makedirs(concept["instance_data_dir"], exist_ok=True)
        os.makedirs(concept["class_data_dir"], exist_ok=True)


def calculate_recommended_training_steps(num_images: int) -> int:
    """
    Calculate recommended training steps based on number of images.

    Args:
        num_images: Number of training images

    Returns:
        Recommended training steps
    """
    if num_images <= 5:
        return 100 * num_images
    elif num_images <= 10:
        return 70 * num_images
    elif num_images <= 20:
        return 50 * num_images
    else:
        return 30 * num_images


def count_images_in_directory(directory: str) -> int:
    """
    Count valid images in a directory using Pillow verification.

    Filters by known image extensions first, then verifies each file
    can be opened and decoded by Pillow (matching DreamBoothDataset's
    loading contract).

    Args:
        directory: Path to directory containing images

    Returns:
        Count of valid images
    """
    if not os.path.isdir(directory):
        return 0

    # Known image extensions (case-insensitive)
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'}
    norm_extensions = tuple(ext.lower() for ext in extensions)

    # If Pillow not available, fall back to extension matching only
    if Image is None:
        count = 0
        for file in os.listdir(directory):
            if file.lower().endswith(norm_extensions):
                full_path = os.path.join(directory, file)
                if os.path.isfile(full_path):
                    count += 1
        return count

    count = 0
    for file in os.listdir(directory):
        # Filter against extensions first (matches fallback behavior)
        if not file.lower().endswith(norm_extensions):
            continue
        full_path = os.path.join(directory, file)
        if not os.path.isfile(full_path):
            continue
        try:
            with Image.open(full_path) as img:
                img.verify()
            # Reopen and load to ensure pixel data decodes successfully
            with Image.open(full_path) as img:
                img.load()
            count += 1
        except Exception as e:
            logger.debug("Skipping invalid image %s: %s", full_path, e)
            continue
    return count


def validate_image_count(directory: str, min_images: int = 3, max_images: int = 10) -> Tuple[bool, int, str]:
    """
    Validate that image count is within recommended range.

    Uses Pillow to verify images (matching DreamBoothDataset's loading contract),
    not just extension matching.

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
        return (True, count, f"Image count optimal: {count} images")


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
    Build accelerate command for DreamBooth training.

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
    --learning_rate={learning_rate} \\
    --max_train_steps={max_train_steps} \\
    --save_sample_prompt="{save_sample_prompt}" \\
    --concepts_list={concepts_file} \\
    --train_text_encoder \\
    --mixed_precision \\
    --use_8bit_adam"""
    return cmd