"""Utility functions for the Conga CLM AI Agent."""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import re

def load_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system_prompt.txt')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful AI assistant for managing contracts in Conga CLM."

def parse_date_string(date_str: str) -> Optional[str]:
    """Parse various date string formats and return YYYY-MM-DD format."""
    if not date_str:
        return None

    date_str = date_str.strip().lower()

    # Handle relative dates
    if "today" in date_str:
        return datetime.now().strftime("%Y-%m-%d")
    elif "tomorrow" in date_str:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next month" in date_str:
        next_month = datetime.now() + timedelta(days=30)
        return next_month.replace(day=1).strftime("%Y-%m-%d")
    elif "next year" in date_str:
        next_year = datetime.now() + timedelta(days=365)
        return next_year.replace(month=1, day=1).strftime("%Y-%m-%d")

    # Try to parse common date formats
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{2})',  # MM/DD/YY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
    ]

    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                    year, month, day = groups
                else:  # MM/DD or MM-DD formats
                    month, day, year = groups
                    if len(year) == 2:
                        year = f"20{year}"

                try:
                    parsed_date = datetime(int(year), int(month), int(day))
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

    return None

def format_contract_display(contracts: List[Dict[str, Any]]) -> str:
    """Format contract list for display."""
    if not contracts:
        return "No contracts found."

    display_lines = []
    for contract in contracts:
        line = f"• {contract.get('type', 'Unknown')} - {contract.get('name', 'Unnamed')}"
        if contract.get('status'):
            line += f" (Status: {contract['status']})"
        if contract.get('account_name'):
            line += f" - Account: {contract['account_name']}"
        if contract.get('id'):
            line += f" - ID: {contract['id']}"
        display_lines.append(line)

    return "\n".join(display_lines)

def format_account_display(accounts: List[Dict[str, Any]]) -> str:
    """Format account list for display."""
    if not accounts:
        return "No accounts found."

    display_lines = []
    for account in accounts:
        line = f"• {account.get('name', 'Unnamed')}"
        if account.get('type'):
            line += f" ({account['type']})"
        if account.get('industry'):
            line += f" - Industry: {account['industry']}"
        if account.get('id'):
            line += f" - ID: {account['id']}"
        display_lines.append(line)

    return "\n".join(display_lines)

def extract_money_amount(text: str) -> Optional[float]:
    """Extract money amount from text like '$50k', '$1.5M', '$100,000'."""
    if not text:
        return None

    # Remove non-numeric characters except decimal points and commas
    clean_text = re.sub(r'[^\d.,kmKM]', '', text.lower())

    # Handle k (thousands) and m (millions) suffixes
    multiplier = 1
    if 'k' in clean_text:
        multiplier = 1000
        clean_text = clean_text.replace('k', '')
    elif 'm' in clean_text:
        multiplier = 1000000
        clean_text = clean_text.replace('m', '')

    # Remove commas and try to parse
    clean_text = clean_text.replace(',', '')

    try:
        amount = float(clean_text) * multiplier
        return amount
    except ValueError:
        return None

def validate_contract_data(data: Dict[str, Any]) -> List[str]:
    """Validate contract data and return list of errors."""
    errors = []

    # Required fields
    if not data.get('contract_type'):
        errors.append("Contract type is required")
    elif data['contract_type'] not in ['MSA', 'NDA', 'SOW', 'ORDER', 'AMENDMENT']:
        errors.append("Contract type must be one of: MSA, NDA, SOW, ORDER, AMENDMENT")

    if not data.get('contract_name'):
        errors.append("Contract name is required")

    if not data.get('account_id'):
        errors.append("Account ID is required")

    # Date validation
    if data.get('start_date') and data.get('end_date'):
        try:
            start = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end = datetime.strptime(data['end_date'], '%Y-%m-%d')
            if start >= end:
                errors.append("Start date must be before end date")
        except ValueError:
            errors.append("Invalid date format (use YYYY-MM-DD)")

    # Numeric validation
    if data.get('term_months'):
        try:
            term = int(data['term_months'])
            if term <= 0:
                errors.append("Term months must be a positive number")
        except (ValueError, TypeError):
            errors.append("Term months must be a valid number")

    if data.get('total_contract_value'):
        try:
            value = float(data['total_contract_value'])
            if value < 0:
                errors.append("Total contract value cannot be negative")
        except (ValueError, TypeError):
            errors.append("Total contract value must be a valid number")

    return errors

def generate_contract_name(contract_type: str, account_name: str) -> str:
    """Generate a meaningful contract name."""
    if not contract_type or not account_name:
        return "New Contract"

    type_names = {
        'MSA': 'Master Service Agreement',
        'NDA': 'Non-Disclosure Agreement',
        'SOW': 'Statement of Work',
        'ORDER': 'Order Form',
        'AMENDMENT': 'Contract Amendment'
    }

    full_type_name = type_names.get(contract_type, contract_type)
    return f"{account_name} {full_type_name}"

def clean_text(text: str) -> str:
    """Clean and normalize text input."""
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', ' ')

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."