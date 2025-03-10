# QR Code Label Generator

A flexible tool for creating printable QR code labels for growth containers used in plant imaging experiments. It encodes identifiers as QR codes paired with human-readable text.

## Features

- Generates sheets of QR code labels from CSV data
- Configurable label dimensions and layout
- Customizable QR code size and properties
- Supports different label formats

## Requirements

```
numpy
qrcode
Pillow
opencv-python
```

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage with default settings:

```bash
python QR_coding.py
```

This will read from `labels.csv` in the current directory and create label sheets as PNG files.

### Command Line Options

```
python QR_coding.py --help
```

Common options:

```
--input FILENAME      Path to CSV input file (default: labels.csv)
--output_dir DIR      Directory to save generated label sheets (default: current directory)
--label_width PIXELS  Width of each label in pixels (default: 1400)
--label_height PIXELS Height of each label in pixels (default: 600)
--cols NUM            Number of columns on label sheet (default: 4)
--rows NUM            Number of rows on label sheet (default: 12)
--qr_size PIXELS      Size of QR code in pixels (default: 500)
--label_col NAME      CSV column name containing label text (default: label)
--desc_col NAME       CSV column name containing description text (default: description)
```

### Example

Create labels using a custom CSV file and output directory:

```bash
python QR_coding.py --input my_labels.csv --output_dir ./output
```

## CSV Format

The CSV file should contain at least a `label` column. The `description` column is optional:

```csv
label,description
A1,Sample 1
A2,Sample 2
A3,Sample 3
```

## Default Label Format

The default settings are optimized for OL1735WR labels from onlinelabels.com (48 labels/sheet, 4×12 layout). You can adjust the settings to work with different label formats.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.