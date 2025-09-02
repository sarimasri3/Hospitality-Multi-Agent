"""
Response formatting utilities.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code
    
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"


def format_date(date: datetime, format_type: str = "long") -> str:
    """
    Format date for display.
    
    Args:
        date: Date to format
        format_type: Format type (long, short, iso)
    
    Returns:
        Formatted date string
    """
    if format_type == "long":
        return date.strftime("%B %d, %Y")
    elif format_type == "short":
        return date.strftime("%m/%d/%Y")
    elif format_type == "iso":
        return date.strftime("%Y-%m-%d")
    else:
        return str(date)


def format_property_card(property_data: Dict[str, Any]) -> str:
    """
    Format property data as a display card.
    
    Args:
        property_data: Property information
    
    Returns:
        Formatted property card string
    """
    return f"""
**{property_data['name']}**
📍 {property_data['location']['city']}
💰 {format_currency(property_data['minimum_price'])}/night
👥 Up to {property_data['guest_space']} guests
🏠 {property_data['property_type'].title()}
✨ {', '.join(property_data.get('amenities', [])[:3])}
"""


def format_booking_summary(booking: Dict[str, Any]) -> str:
    """
    Format booking data as a summary.
    
    Args:
        booking: Booking information
    
    Returns:
        Formatted booking summary
    """
    check_in = datetime.fromisoformat(booking['check_in_date'])
    check_out = datetime.fromisoformat(booking['check_out_date'])
    
    return f"""
📅 **Booking Summary**
• Reference: {booking['booking_id'][:8].upper()}
• Check-in: {format_date(check_in)}
• Check-out: {format_date(check_out)}
• Nights: {booking.get('nights', (check_out - check_in).days)}
• Guests: {booking['number_of_guests']}
• Total: {format_currency(booking['total_price'])}
• Status: {booking['status'].title()}
"""


def format_price_breakdown(
    accommodation: float,
    service_fee: float,
    cleaning_fee: float,
    tax: float,
    add_ons: Optional[float] = 0
) -> str:
    """
    Format price breakdown.
    
    Args:
        accommodation: Base accommodation cost
        service_fee: Service fee
        cleaning_fee: Cleaning fee
        tax: Tax amount
        add_ons: Optional add-on costs
    
    Returns:
        Formatted price breakdown
    """
    total = accommodation + service_fee + cleaning_fee + tax + add_ons
    
    breakdown = f"""
💰 **Price Breakdown**
• Accommodation: {format_currency(accommodation)}
• Service Fee: {format_currency(service_fee)}
• Cleaning Fee: {format_currency(cleaning_fee)}"""
    
    if add_ons > 0:
        breakdown += f"\n• Add-ons: {format_currency(add_ons)}"
    
    breakdown += f"""
• Tax: {format_currency(tax)}
──────────────
**Total: {format_currency(total)}**
"""
    
    return breakdown


def format_error_message(error_code: str, details: Optional[str] = None) -> str:
    """
    Format user-friendly error message.
    
    Args:
        error_code: Error code
        details: Optional error details
    
    Returns:
        Formatted error message
    """
    error_messages = {
        "INVALID_DATES": "The dates you selected are not valid. Please check and try again.",
        "PROPERTY_UNAVAILABLE": "This property is not available for your selected dates.",
        "PAYMENT_FAILED": "Payment authorization failed. Please try a different payment method.",
        "SYSTEM_ERROR": "We encountered a technical issue. Please try again in a moment.",
        "VALIDATION_ERROR": "Some information is missing or incorrect. Please review and try again."
    }
    
    message = error_messages.get(error_code, "An unexpected error occurred.")
    
    if details:
        message += f"\n\nDetails: {details}"
    
    return f"❌ {message}"


def format_success_message(action: str, details: Optional[str] = None) -> str:
    """
    Format success message.
    
    Args:
        action: Action that succeeded
        details: Optional details
    
    Returns:
        Formatted success message
    """
    messages = {
        "booking_created": "✅ Your booking has been confirmed!",
        "payment_authorized": "✅ Payment authorized successfully.",
        "email_sent": "✅ Confirmation email sent.",
        "survey_submitted": "✅ Thank you for your feedback!",
        "profile_updated": "✅ Your profile has been updated."
    }
    
    message = messages.get(action, f"✅ {action} completed successfully.")
    
    if details:
        message += f"\n\n{details}"
    
    return message