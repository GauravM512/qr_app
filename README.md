# Flet QR Code Generator

A modern and user-friendly QR code generator built with Python and Flet framework.

## Features

- Generate QR codes from text or URLs
- Customize QR code appearance:
  - Fill color (8 color options)
  - Background color (8 color options)
  - Error correction levels (7% to 30%)
  - Border size (0-8)
  - QR code size (100-500 pixels)
- Save QR codes as PNG files
- Real-time preview
- Modern and responsive UI

## Installation

1. Clone this repository:
```bash
git clone https://github.com/GauravM512/qr-code-generator.git
cd qr-code-generator
```

2. Install required dependencies:
```bash
pip install flet qrcode pillow
```

## Usage

1. Run the application:
```bash
python src/main.py
```

2. Enter text or URL in the input field
3. Customize your QR code using the available options
4. Click "Generate QR Code" to create the QR code
5. Click "Save QR Code" to save it as a PNG file

## Requirements

- Python 3.7 or higher
- flet
- qrcode
- pillow

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request