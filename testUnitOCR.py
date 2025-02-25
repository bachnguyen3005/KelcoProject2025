#!/usr/bin/env python3
"""
OCR Test Runner - A simple script to test OCRProcessor functionality with image inputs
Usage: python ocr_test_runner.py <image_path> [test_function]

Arguments:
    image_path    - Path to the image file to process
    test_function - Optional: Specific function to test ("numbers", "text", or "lock")
                    If not specified, all functions will be tested
"""

import os
import sys
import argparse
from ocr import OCRProcessor  # Import the OCRProcessor from your module


def test_extract_numbers(processor, image_path):
    """Test the extract_numbers function"""
    print("\n=== Testing extract_numbers() ===")
    try:
        result = processor.extract_numbers(image_path)
        print(f"Extracted numbers: {result}")
        return result
    except Exception as e:
        print(f"Error in extract_numbers: {e}")
        return None


def test_extract_text(processor, image_path):
    """Test the extract_text function"""
    print("\n=== Testing extract_text() ===")
    try:
        result = processor.extract_text(image_path)
        print(f"Extracted text: {result}")
        return result
    except Exception as e:
        print(f"Error in extract_text: {e}")
        return None


def test_get_lock_status(processor, image_path):
    """Test the get_lock_status function"""
    print("\n=== Testing get_lock_status() ===")
    try:
        result = processor.get_lock_status(image_path)
        print(f"Lock status: {result}")
        return result
    except Exception as e:
        print(f"Error in get_lock_status: {e}")
        return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test OCRProcessor with an input image')
    parser.add_argument('image_path', help='Path to the image file to process')
    parser.add_argument('test_function', nargs='?', default='all', 
                        choices=['all', 'numbers', 'text', 'lock'],
                        help='Specific function to test (default: all)')
    
    args = parser.parse_args()
    
    # Check if the image exists
    if not os.path.isfile(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        return 1
    
    print(f"Testing OCR functions with image: {args.image_path}")
    
    try:
        # Initialize the OCRProcessor
        processor = OCRProcessor()
        
        # Call the requested test function(s)
        if args.test_function in ['all', 'numbers']:
            test_extract_numbers(processor, args.image_path)
            
        if args.test_function in ['all', 'text']:
            test_extract_text(processor, args.image_path)
            
        if args.test_function in ['all', 'lock']:
            test_get_lock_status(processor, args.image_path)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())