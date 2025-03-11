#!/usr/bin/env python3
"""
QR Code Label Generator

Creates printable sheets of QR code labels from CSV data for plant growth containers.
"""

import argparse
import csv
import io
import re
import numpy as np
import qrcode
from PIL import Image, ImageDraw
import cv2
import os


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate QR code labels from CSV data')
    parser.add_argument('--input', type=str, default='labels.csv',
                        help='Path to CSV input file (default: labels.csv)')
    parser.add_argument('--output_dir', type=str, default='.',
                        help='Directory to save generated label sheets (default: current directory)')
    parser.add_argument('--label_width', type=int, default=1400,
                        help='Width of each label in pixels (default: 1400)')
    parser.add_argument('--label_height', type=int, default=600,
                        help='Height of each label in pixels (default: 600)')
    parser.add_argument('--cols', type=int, default=4,
                        help='Number of columns on label sheet (default: 4)')
    parser.add_argument('--rows', type=int, default=12,
                        help='Number of rows on label sheet (default: 12)')
    parser.add_argument('--qr_size', type=int, default=500,
                        help='Size of QR code in pixels (default: 500)')
    parser.add_argument('--label_col', type=str, default='label',
                        help='CSV column name containing label text (default: label)')
    parser.add_argument('--desc_col', type=str, default='description',
                        help='CSV column name containing description text (default: description)')
    return parser.parse_args()


def create_qr_code(text, size):
    """Create a QR code image from text."""
    if not text:
        # Return blank image if text is empty
        return np.ones((size, size), dtype=np.uint8) * 255
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create QR code as PIL Image - explicitly black on white
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to numpy array using PIL directly
    img_array = np.array(qr_img)
    
    # Ensure proper format: black (0) on white (255)
    if img_array.dtype == bool:
        # Convert to proper uint8 format (True = black module)
        # We want True values to be 0 (black) and False to be 255 (white)
        img_array = (~img_array).astype(np.uint8) * 255
    
    # Ensure array is 2D grayscale
    if len(img_array.shape) == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Resize to requested size
    img_array = cv2.resize(img_array, (size, size))
    
    # Final check to ensure black on white (0 on 255)
    # QR codes need dark modules on light background
    # If mean value is low, it means the image is mostly black, so invert
    if np.mean(img_array) < 127:
        img_array = 255 - img_array
        
    return img_array


def create_text_image(label, description, size):
    """Create text image with label and description."""
    # Create blank white image
    img = Image.new('L', (size, size), color=255)
    d = ImageDraw.Draw(img)
    
    # Import font
    from PIL import ImageFont
    try:
        # Set very large font sizes for maximum visibility
        label_size = 80  # Extremely large for label
        desc_size = 60   # Very large for description
        
        # Try to load a system font
        font_label = None
        font_desc = None
        
        # List of common font locations
        font_locations = [
            '/usr/share/fonts',            # Linux
            '/System/Library/Fonts',       # MacOS
            'C:\\Windows\\Fonts'           # Windows
        ]
        
        # Try to find a bold/heavy font for better visibility
        for location in font_locations:
            if os.path.exists(location):
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.lower().endswith('.ttf'):
                            # Prioritize bold fonts
                            if 'bold' in file.lower() or 'heavy' in file.lower():
                                try:
                                    font_label = ImageFont.truetype(os.path.join(root, file), label_size)
                                    font_desc = ImageFont.truetype(os.path.join(root, file), desc_size)
                                    break
                                except Exception:
                                    pass
                    if font_label:
                        break
            if font_label:
                break
                
        # If no bold font found, try any font
        if not font_label:
            for location in font_locations:
                if os.path.exists(location):
                    for root, dirs, files in os.walk(location):
                        for file in files:
                            if file.lower().endswith('.ttf'):
                                try:
                                    font_label = ImageFont.truetype(os.path.join(root, file), label_size)
                                    font_desc = ImageFont.truetype(os.path.join(root, file), desc_size)
                                    break
                                except Exception:
                                    pass
                        if font_label:
                            break
                if font_label:
                    break
        
        # If still no font found, use default (but will be small)
        if not font_label:
            print("Warning: No system font found. Text may be small.")
            # Try to make default font as large as possible
            font_label = ImageFont.load_default()
            font_desc = ImageFont.load_default()
            
        # Draw label very prominently
        # Center text vertically and horizontally for better visibility
        label_text = str(label)
        
        # If using a real font, calculate text size
        text_width = 0
        text_height = 0
        try:
            # PIL version compatibility check
            if hasattr(font_label, 'getbbox'):  # PIL 9.2.0+
                bbox = font_label.getbbox(label_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            elif hasattr(font_label, 'getsize'):  # Older PIL
                text_width, text_height = font_label.getsize(label_text)
        except Exception:
            pass
        
        # Center the label text
        x = (size - text_width) // 2
        y = size // 4 - text_height // 2
        x = max(10, x)  # Ensure not too far left
        y = max(10, y)  # Ensure not too far up
        
        # Draw label in center with thick text
        d.text((x, y), label_text, font=font_label, fill=0)  # Black text (0)
        
        # Draw description below the label if it exists
        if description:
            # Center the description text
            try:
                if hasattr(font_desc, 'getbbox'):
                    bbox = font_desc.getbbox(description)
                    desc_width = bbox[2] - bbox[0]
                elif hasattr(font_desc, 'getsize'):
                    desc_width, _ = font_desc.getsize(description)
                else:
                    desc_width = 0
                
                desc_x = (size - desc_width) // 2
                desc_x = max(10, desc_x)
            except Exception:
                desc_x = 10
            
            desc_y = y + text_height + 20  # Below the label with some spacing
            d.text((desc_x, desc_y), description, font=font_desc, fill=0)
    
    except Exception as e:
        print(f"Warning: Could not draw text: {e}")
        # Emergency fallback - draw extremely large text without font
        try:
            # Draw gigantic label text as a last resort
            for thickness in range(5):  # Very thick lines
                d.text((10+thickness, 10+thickness), str(label), fill=0)
            
            if description:
                d.text((10, 100), description, fill=0)
        except Exception:
            pass
    
    # Convert to numpy array without saving temporary files
    img_array = np.array(img)
    return img_array


def read_csv_data(filename, label_col='label', desc_col='description'):
    """Read label data from CSV file."""
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Check if required columns exist
            if label_col not in reader.fieldnames:
                raise ValueError(f"CSV file missing required column: {label_col}")
            
            for row in reader:
                # Handle different column name scenarios
                label = row.get(label_col, "")
                desc = row.get(desc_col, "")
                data.append((label, desc))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []
    
    return data


def generate_label_sheets(data, args):
    """Generate label sheets from data."""
    labels_per_sheet = args.rows * args.cols
    num_sheets = (len(data) + labels_per_sheet - 1) // labels_per_sheet
    
    # Calculate sheet dimensions
    sheet_width = args.cols * args.label_width
    sheet_height = args.rows * args.label_height
    
    label_count = 0
    for sheet_num in range(1, num_sheets + 1):
        # Create blank white sheet
        sheet = np.ones((sheet_height, sheet_width), dtype=np.uint8) * 255
        
        # Add labels to sheet
        for row in range(args.rows):
            for col in range(args.cols):
                if label_count >= len(data):
                    break
                
                label, desc = data[label_count]
                
                # Calculate positions
                x_offset = col * args.label_width
                y_offset = row * args.label_height
                margin = (args.label_height - args.qr_size) // 2
                
                # Create QR code
                qr_img = create_qr_code(label, args.qr_size)
                
                # Create text description
                text_img = create_text_image(label, desc, args.qr_size)
                
                # Position: QR on left, text on right
                # QR code position (left side of label)
                qr_x = x_offset + margin
                qr_y = y_offset + margin
                
                # Text position (right side of label)
                text_width = args.label_width // 2 - margin
                text_x = x_offset + args.label_width // 2
                text_y = y_offset + margin
                
                # Place the images on the sheet
                try:
                    # Place QR code
                    h, w = qr_img.shape
                    if h <= args.qr_size and w <= args.qr_size and qr_y + h <= sheet_height and qr_x + w <= sheet_width:
                        sheet[qr_y:qr_y+h, qr_x:qr_x+w] = qr_img
                    
                    # Place text
                    h, w = text_img.shape
                    if h <= args.qr_size and w <= args.qr_size and text_y + h <= sheet_height and text_x + w <= sheet_width:
                        sheet[text_y:text_y+h, text_x:text_x+w] = text_img
                except Exception as e:
                    print(f"Error placing label {label_count+1}: {e}")
                
                label_count += 1
        
        # Save sheet
        output_path = os.path.join(args.output_dir, f"labels_sheet_{sheet_num}.png")
        Image.fromarray(sheet).save(output_path)
        print(f"Generated sheet {sheet_num}: {output_path}")


def main():
    """Main function."""
    args = parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Read data from CSV
    data = read_csv_data(args.input, args.label_col, args.desc_col)
    if not data:
        print("No data found or error in CSV file. Exiting.")
        return

    print(f"Generating labels for {len(data)} entries...")
    generate_label_sheets(data, args)
    print("Done!")


if __name__ == "__main__":
    main()