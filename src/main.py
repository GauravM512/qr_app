import flet as ft
import qrcode
from io import BytesIO
import base64
from PIL import Image
import os

def main(page: ft.Page):
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREY)

    def clear_input_error(e):
        input_field.error_text = None
        page.update()

    # Create a text field for user input with on_change handler
    input_field = ft.TextField(
        label="Enter text or URL",
        width=300,
        autofocus=True,
        on_change=clear_input_error,
    )

    # Create dropdowns for color selection instead of color pickers
    COLORS = {
        "Black": "#000000",
        "White": "#FFFFFF",
        "Red": "#FF0000",
        "Green": "#00FF00",
        "Blue": "#0000FF",
        "Yellow": "#FFFF00",
        "Purple": "#800080",
        "Orange": "#FFA500",
    }

    fill_color_dropdown = ft.Dropdown(
        width=150,
        label="Fill Color",
        options=[ft.dropdown.Option(key=color) for color in COLORS.keys()],
        value="Black",
    )

    bg_color_dropdown = ft.Dropdown(
        width=150,
        label="Background Color",
        options=[ft.dropdown.Option(key=color) for color in COLORS.keys()],
        value="White",
    )

    # Add QR code customization options
    ERROR_LEVELS = {
        "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
        "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
        "Quarter (25%)": qrcode.constants.ERROR_CORRECT_Q,
        "High (30%)": qrcode.constants.ERROR_CORRECT_H,
    }

    error_level_dropdown = ft.Dropdown(
        width=150,
        label="Error Correction",
        options=[ft.dropdown.Option(key=level) for level in ERROR_LEVELS.keys()],
        value="Low (7%)",
    )

    def validate_number(value, min_val, max_val):
        try:
            num = int(value)
            return min_val <= num <= max_val
        except ValueError:
            return False

    # Remove box_size_input definition and keep only these text inputs
    border_size_input = ft.TextField(
        label="Border Size (0-8)",
        value="4",
        width=150,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"),
        hint_text="Enter 0-8",
    )

    qr_size_input = ft.TextField(
        label="QR Code Size (100-500)",
        value="200",
        width=150,
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"),
        hint_text="Enter 100-500",
    )

    # Create an image widget to display the QR code
    qr_image = ft.Image(
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )

    # Create placeholder for QR display
    placeholder = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.QR_CODE, size=50, color=ft.Colors.GREY_400),
                    ft.Text("QR Code will appear here", color=ft.Colors.GREY_400),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
        ),
        width=300,
        height=300,
    )

    # Function to generate the QR code
    def generate_qr(e):
        # Validate inputs
        if not input_field.value.strip():
            input_field.error_text = "Please enter some text or a URL"
            page.update()
            return

        # Validate numeric inputs (removed box size validation)
        if not validate_number(border_size_input.value, 0, 8):
            border_size_input.error_text = "Enter a number between 0-8"
            page.update()
            return
        if not validate_number(qr_size_input.value, 100, 500):
            qr_size_input.error_text = "Enter a number between 100-500"
            page.update()
            return

        # Clear any error messages
        border_size_input.error_text = None
        qr_size_input.error_text = None

        # Generate the QR code
        try:
            qr = qrcode.QRCode(
                version=None,  # Allow automatic version selection
                error_correction=ERROR_LEVELS[error_level_dropdown.value],
                box_size=20,  # Fixed box size
                border=int(border_size_input.value),
            )
            qr.add_data(input_field.value)
            qr.make(fit=True)

            fill_color = COLORS[fill_color_dropdown.value]
            bg_color = COLORS[bg_color_dropdown.value]
            
            qr_img = qr.make_image(fill_color=fill_color, back_color=bg_color)

            # Convert back to RGB before saving (to avoid transparency issues)
            qr_img = qr_img.convert("RGB")
            
            # Resize the image
            qr_img = qr_img.resize((int(qr_size_input.value), int(qr_size_input.value)))
            
            # Convert to base64
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            qr_image.src_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            qr_image.width = qr_size_input.value
            qr_image.height = qr_size_input.value
            
            # Hide placeholder, show QR
            placeholder.visible = False
            qr_image.visible = True
            page.update()
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error: {str(ex)}")))
            page.update()

    def close_dialog(e):
        dialog.open = False
        page.update()

    # Create dialog once and reuse it
    dialog = ft.AlertDialog(
        title=ft.Text("Success!"),
        actions=[
            ft.TextButton("OK", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def show_save_dialog(file_path):
        # Update dialog content
        dialog.content = ft.Text(f"QR Code saved at:\n{os.path.abspath(file_path)}")
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Function to save the QR code as a PNG file
    def save_qr(e):
        if qr_image.src_base64:
            try:
                file_path = "qrcode.png"
                # Decode the base64 image
                img_data = base64.b64decode(qr_image.src_base64)
                with open(file_path, "wb") as f:
                    f.write(img_data)
                show_save_dialog(file_path)
            except Exception as ex:
                dialog.title = ft.Text("Error")
                dialog.content = ft.Text(f"Error saving file: {str(ex)}")
                page.dialog = dialog
                dialog.open = True
                page.update()
        else:
            dialog.title = ft.Text("Error")
            dialog.content = ft.Text("No QR Code to save!")
            page.dialog = dialog
            dialog.open = True
            page.update()

    # Create buttons for generating and saving QR codes
    generate_button = ft.ElevatedButton(
        text="Generate QR Code",
        on_click=generate_qr,
    )
    save_button = ft.ElevatedButton(
        text="Save QR Code",
        on_click=save_qr,
    )

    # Update the page layout to split into left and right columns
    right_column = ft.Container(
        content=ft.Column(
            [
                ft.Stack(
                    [
                        placeholder,
                        qr_image,
                    ],
                    width=400,
                    height=400,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        padding=20,
    )

    # Update left column contents to include image controls
    left_column_contents = [
        input_field,
        ft.Container(height=20),
        ft.Row(
            [
                ft.Column([fill_color_dropdown]),
                ft.Container(width=20),
                ft.Column([bg_color_dropdown]),
            ],
        ),
        ft.Container(height=20),
        error_level_dropdown,
        ft.Container(height=10),
        border_size_input,
        ft.Container(height=10),
        qr_size_input,
        ft.Container(height=20),
        generate_button,
        ft.Container(height=20),
        save_button,
    ]

    # Set initial visibility
    qr_image.visible = False
    placeholder.visible = True

    page.add(
        ft.Container(
            content=ft.Row(
                [
                    # Left column - Controls
                    ft.Container(
                        content=ft.Column(
                            left_column_contents,
                            scroll=ft.ScrollMode.AUTO,
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        width=400,
                        padding=20,
                    ),
                    # Vertical divider
                    ft.VerticalDivider(),
                    # Right column - QR Code
                    right_column,
                ],
                expand=True,
            ),
            expand=True,
        )
    )

# Run the app
ft.app(target=main)