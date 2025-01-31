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
        generate_qr()
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

    def on_dropdown_change(e):
        generate_qr()

    fill_color_dropdown = ft.Dropdown(
        width=150,
        label="Fill Color",
        options=[ft.dropdown.Option(key=color) for color in COLORS.keys()],
        value="Black",
        on_change=on_dropdown_change,
    )

    bg_color_dropdown = ft.Dropdown(
        width=150,
        label="Background Color",
        options=[ft.dropdown.Option(key=color) for color in COLORS.keys()],
        value="White",
        on_change=on_dropdown_change,
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
        on_change=on_dropdown_change,
    )

    def validate_number(value, min_val, max_val):
        if not value:  # Handle empty string
            return False
        try:
            num = int(value)
            return min_val <= num <= max_val
        except ValueError:
            return False

    def on_text_change(e):
        if e.control.value and not e.control.value.isdigit():
            e.control.value = ''.join(filter(str.isdigit, e.control.value))
        generate_qr()
        page.update()

    border_size_input = ft.TextField(
        label="Border Size (0-8)",
        value="4",
        width=150,
        hint_text="Enter 0-8",
        on_change=on_text_change,
    )

    qr_size_input = ft.TextField(
        label="QR Code Size (100-500)",
        value="200",
        width=150,
        hint_text="Enter 100-500",
        on_change=on_text_change,
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
    def generate_qr():
        # Only validate input text
        if not input_field.value or not input_field.value.strip():
            placeholder.visible = True
            qr_image.visible = False
            page.update()
            return

        try:
            # Validate and get sizes with proper error checking
            try:
                border_size = int(border_size_input.value) if border_size_input.value else 4
                border_size = max(0, min(border_size, 8))  # Clamp between 0-8
                
                qr_size = int(qr_size_input.value) if qr_size_input.value else 200
                qr_size = max(100, min(qr_size, 500))  # Clamp between 100-500
            except ValueError:
                border_size = 4
                qr_size = 200

            # Clear error states
            border_size_input.error_text = None
            qr_size_input.error_text = None
            input_field.error_text = None

            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_LEVELS[error_level_dropdown.value],
                box_size=20,
                border=border_size,
            )
            qr.add_data(input_field.value)
            qr.make(fit=True)

            fill_color = COLORS[fill_color_dropdown.value]
            bg_color = COLORS[bg_color_dropdown.value]
            
            qr_img = qr.make_image(fill_color=fill_color, back_color=bg_color)
            qr_img = qr_img.convert("RGB")
            
            # Ensure size is valid before resizing
            if qr_size > 0:
                qr_img = qr_img.resize((qr_size, qr_size))
            
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            qr_image.src_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            qr_image.width = qr_size
            qr_image.height = qr_size
            
            placeholder.visible = False
            qr_image.visible = True
            page.update()
        except Exception as ex:
            # Show error in input field instead of snackbar
            input_field.error_text = f"Error: {str(ex)}"
            placeholder.visible = True
            qr_image.visible = False
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