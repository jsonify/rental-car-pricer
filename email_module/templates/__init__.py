# email_module/templates/__init__.py
from .formatters import format_email_body_text, format_price_change_html
from .html_template import format_email_body_html

__all__ = ['format_email_body_text', 'format_email_body_html', 'format_price_change_html']