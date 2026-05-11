from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
import os


def generate_order_pdf(order, order_items):
    """Generate a PDF containing order details and items."""
    file_path = os.path.join(settings.MEDIA_ROOT, f"order_receipts/order_{order.order_id}.pdf")

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=letter)

    # Define colors from your palette
    header_color = colors.HexColor("#008080")  # Teal
    text_color = colors.HexColor("#333333")  # Dark gray
    line_color = colors.HexColor("#CCCCCC")  # Light gray

    # Set title style
    c.setFillColor(header_color)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Order Receipt")

    # Order Details
    c.setFillColor(text_color)
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Order ID: {order.order_id}")
    c.drawString(50, 700, f"Customer: {order.first_name} {order.last_name}")
    c.drawString(50, 680, f"Email: {order.email}")
    c.drawString(50, 660, f"Phone: {order.phone}")
    c.drawString(50, 640, f"Address: {order.address1}, {order.city}, {order.state}, {order.country}, {order.zip_code}")
    c.drawString(50, 620, f"Payment Method: {order.payment_method}")
    c.drawString(50, 600, f"Payment Status: {order.payment_status}")

    # Draw a line separator
    c.setStrokeColor(line_color)
    c.line(50, 590, 550, 590)

    # Table Headers
    c.setFillColor(header_color)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 570, "Product Name")
    c.drawString(220, 570, "Brand")
    c.drawString(320, 570, "Color")
    c.drawString(380, 570, "Size")
    c.drawString(440, 570, "Quantity")
    c.drawString(500, 570, "Price")

    # Reset text color
    c.setFillColor(text_color)
    y_position = 550

    # Add order items
    c.setFont("Helvetica", 10)
    for item in order_items:
        c.drawString(50, y_position, item.name)
        c.drawString(220, y_position, item.brand)
        c.drawString(320, y_position, item.color if item.color else "-")
        c.drawString(380, y_position, item.size if item.size else "-")
        c.drawString(440, y_position, str(item.quantity))
        c.drawString(500, y_position, f"₹{item.price}")

        y_position -= 20

    # Draw a final separator
    c.setStrokeColor(line_color)
    c.line(50, y_position, 550, y_position)

    # Total Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position - 20, f"Subtotal: ₹{order.total_price}")
    c.drawString(50, y_position - 40, f"Security Deposit: ₹{order.total_security}")
    c.drawString(50, y_position - 60, f"Shipping Cost: ₹{order.shipping_cost}")
    c.drawString(50, y_position - 80, f"Discount: ₹{order.discount}")
    c.drawString(50, y_position - 100, f"Grand Total: ₹{order.Grand_total}")

    c.save()
    return file_path
