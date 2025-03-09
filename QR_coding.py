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
    
    # Create QR code as PIL Image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to numpy array without saving temporary files
    with io.BytesIO() as buffer:
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)
        img_array = np.array(Image.open(buffer))
    
    # Check if the image is RGB and convert to grayscale if needed
    if len(img_array.shape) == 3:
        img_array = img_array[:, :, 0]
    
    # Resize to requested size
    img_array = cv2.resize(img_array, (size, size))
    return img_array


def create_text_image(label, description, size):
    """Create text image with label and description."""
    # Create blank white image
    img = Image.new('L', (size, size), color=255)
    d = ImageDraw.Draw(img)
    
    # Combine label and description
    text = f"{label} {description}" if description else label
    
    # Insert newlines for readability (every ~10 chars)
    formatted_text = re.sub("(.{10})", "\\1\n", text, 0, re.DOTALL)
    
    # Draw text
    d.text((10, 10), formatted_text, fill=0)  # Black text (0) on white background
    
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
                
                # Create and place QR code
                qr_img = create_qr_code(label, args.qr_size)
                qr_x = x_offset + margin
                qr_y = y_offset + margin
                sheet[qr_y:qr_y+args.qr_size, qr_x:qr_x+args.qr_size] = qr_img
                
                # Create and place text description
                text_img = create_text_image(label, desc, args.qr_size)
                text_x = x_offset + args.label_width // 2 + margin
                text_y = y_offset + margin
                sheet[text_y:text_y+args.qr_size, text_x:text_x+args.qr_size] = text_img
                
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