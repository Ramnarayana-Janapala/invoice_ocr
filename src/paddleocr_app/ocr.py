"""
PaddleOCR wrapper with Apple Silicon support and model management.
"""
from pathlib import Path
from typing import Optional, List
import logging
from dataclasses import dataclass

from paddleocr import PaddleOCR
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str
    confidence: float
    bbox: Optional[List[List[float]]] = None
    raw_result: Optional[list] = None


class PaddleOCREngine:
    """
    Wrapper around PaddleOCR optimized for Apple Silicon.
    
    Handles:
    - Model initialization with proper caching
    - Image processing
    - Error handling
    - Language configuration
    """
    
    def __init__(
        self,
        language: str = "en",
        enable_mkldnn: bool = True,
    ):
        """
        Initialize PaddleOCR engine.
        
        Args:
            language: Language code (e.g., 'en', 'ch', 'es')
            enable_mkldnn: Enable MKLDNN CPU optimization
        """
        self.language = language

        logger.info(f"Initializing PaddleOCR with language: {language}")

        # Apple Silicon: CPU-only with optimizations
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=language,
            enable_mkldnn=enable_mkldnn,
        )
        
        logger.info("✓ PaddleOCR initialized successfully")

    def process_image(self, image_path: Path) -> List[OCRResult]:
        """
        Process image and extract text.
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Processing image: {image_path}")

        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")

        # Run OCR
        results = self.ocr.ocr(image)

        ocr_results = []

        if results is None or len(results) == 0:
            logger.warning("OCR returned empty results")
            return ocr_results

        # Handle dictionary format (newer PaddleOCR)
        if isinstance(results[0], dict):
            result_dict = results[0]
            rec_texts = result_dict.get('rec_texts', [])
            rec_scores = result_dict.get('rec_scores', [])
            rec_boxes = result_dict.get('rec_boxes', [])

            logger.info(f"Found {len(rec_texts)} text items")

            for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                bbox = rec_boxes[i] if i < len(rec_boxes) else None
                confidence = float(score)

                ocr_results.append(
                    OCRResult(
                        text=text,
                        confidence=confidence,
                        bbox=bbox,
                        raw_result={'text': text, 'score': score, 'box': bbox},
                    )
                )
                logger.info(f"Added: '{text}' (confidence: {confidence:.2%})")

        # Handle list format (older PaddleOCR)
        else:
            for line in results:
                if line is None:
                    continue
                for item in line:
                    try:
                        bbox = item[0]
                        text, confidence = item[1]
                        confidence = float(confidence)

                        ocr_results.append(
                            OCRResult(
                                text=text,
                                confidence=confidence,
                                bbox=bbox,
                                raw_result=item,
                            )
                        )
                    except Exception as e:
                        logger.error(f"Error: {e}, item: {item}")
                        continue

        logger.info(f"Extracted {len(ocr_results)} text blocks")
        return ocr_results
    
    def extract_full_text(self, image_path: Path) -> str:
        """
        Extract all text from image as a single string.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Concatenated text
        """
        results = self.process_image(image_path)
        return " ".join(r.text for r in results)
    
    def process_with_filtering(
        self,
        image_path: Path,
        min_confidence: float = 0.5,
    ) -> List[OCRResult]:
        """
        Process image and filter by confidence threshold.
        
        Args:
            image_path: Path to image file
            min_confidence: Only return results above this threshold
            
        Returns:
            Filtered OCR results
        """
        results = self.process_image(image_path)
        filtered = [r for r in results if r.confidence >= min_confidence]
        logger.info(
            f"Filtered {len(results)} results to {len(filtered)} "
            f"(confidence >= {min_confidence})"
        )
        return filtered
    
    def process_batch(
        self,
        image_dir: Path,
        pattern: str = "*.jpg",
        recursive: bool = True,
    ) -> dict:
        """
        Process multiple images in a directory.
        
        Args:
            image_dir: Directory containing images
            pattern: File pattern to match
            recursive: Search recursively
            
        Returns:
            Dict mapping image paths to OCR results
        """
        image_dir = Path(image_dir)
        if not image_dir.is_dir():
            raise ValueError(f"Not a directory: {image_dir}")
        
        # Find images
        if recursive:
            images = list(image_dir.rglob(pattern))
        else:
            images = list(image_dir.glob(pattern))
        
        logger.info(f"Found {len(images)} images to process")
        
        results = {}
        for i, image_path in enumerate(images, 1):
            logger.info(f"Processing {i}/{len(images)}: {image_path.name}")
            try:
                results[str(image_path)] = self.process_image(image_path)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results[str(image_path)] = None
        
        return results


def create_ocr_engine(
    language: str = "en",
    model_cache_dir: Optional[Path] = None,
) -> PaddleOCREngine:
    """
    Factory function to create OCR engine.
    
    Args:
        language: Language code
        model_cache_dir: Model cache directory
        
    Returns:
        Initialized PaddleOCREngine
    """
    return PaddleOCREngine(language=language)
