# receipt.py
from datetime import datetime

def generate_receipt(attendant, sold_items):
    """
    sold_items: list of dicts [{name, qty, price}]
    Returns: formatted receipt string
    """
    total_amount = 0
    receipt_text = (
        f"🧾 KIJANI AFRICA RECEIPT\n"
        f"Attendant: {attendant}\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )
    
    for item in sold_items:
        line_total = item['qty'] * item['price']
        total_amount += line_total
        receipt_text += f"{item['name']} - Qty: {item['qty']} - Price: KSh {item['price']} - Total: KSh {line_total}\n"
    
    receipt_text += f"\nTOTAL: KSh {total_amount}\n-------------------------\nThank you 🙏"
    return receipt_text
