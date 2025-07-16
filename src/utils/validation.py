"""
Form validation system for ROI Calculator
"""
import re
from typing import Dict, Any, List

def validate_roi_submission(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation for ROI submission form
    Returns: {'valid': bool, 'errors': dict}
    """
    errors = {}
    
    # Required fields validation
    required_fields = [
        'first_name', 'last_name', 'email', 'monthly_revenue',
        'average_order_value', 'monthly_orders'
    ]
    
    for field in required_fields:
        if not data.get(field):
            errors[field] = f'{field.replace("_", " ").title()} is required'
        elif isinstance(data[field], str) and not data[field].strip():
            errors[field] = f'{field.replace("_", " ").title()} cannot be empty'
    
    # Email validation
    if data.get('email'):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors['email'] = 'Please enter a valid email address'
    
    # Name validation
    for name_field in ['first_name', 'last_name']:
        if data.get(name_field):
            if len(data[name_field]) < 2:
                errors[name_field] = f'{name_field.replace("_", " ").title()} must be at least 2 characters'
            elif len(data[name_field]) > 50:
                errors[name_field] = f'{name_field.replace("_", " ").title()} must be less than 50 characters'
            elif not re.match(r'^[a-zA-Z\s\'-]+$', data[name_field]):
                errors[name_field] = f'{name_field.replace("_", " ").title()} contains invalid characters'
    
    # Financial data validation
    financial_fields = {
        'monthly_revenue': {'min': 1000, 'max': 10000000},
        'average_order_value': {'min': 1, 'max': 100000},
        'monthly_orders': {'min': 1, 'max': 1000000}
    }
    
    for field, constraints in financial_fields.items():
        if data.get(field):
            try:
                value = float(data[field])
                if value < constraints['min']:
                    errors[field] = f'{field.replace("_", " ").title()} must be at least ${constraints["min"]:,}'
                elif value > constraints['max']:
                    errors[field] = f'{field.replace("_", " ").title()} cannot exceed ${constraints["max"]:,}'
            except (ValueError, TypeError):
                errors[field] = f'{field.replace("_", " ").title()} must be a valid number'
    
    # Phone validation (optional)
    if data.get('phone'):
        phone_clean = re.sub(r'\D', '', data['phone'])
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            errors['phone'] = 'Please enter a valid phone number'
    
    # Website validation (optional)
    if data.get('website'):
        website_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if not re.match(website_pattern, data['website']):
            errors['website'] = 'Please enter a valid website URL (include http:// or https://)'
    
    # Company validation (optional)
    if data.get('company') and len(data['company']) > 100:
        errors['company'] = 'Company name must be less than 100 characters'
    
    # Industry validation (optional)
    valid_industries = [
        'E-commerce', 'SaaS', 'Healthcare', 'Finance', 'Education',
        'Real Estate', 'Manufacturing', 'Retail', 'Technology',
        'Consulting', 'Marketing', 'Other'
    ]
    if data.get('industry') and data['industry'] not in valid_industries:
        errors['industry'] = 'Please select a valid industry'
    
    # Business stage validation (optional)
    valid_stages = ['Startup', 'Growth', 'Established', 'Enterprise']
    if data.get('business_stage') and data['business_stage'] not in valid_stages:
        errors['business_stage'] = 'Please select a valid business stage'
    
    # Company size validation (optional)
    valid_sizes = ['1-10', '11-50', '51-200', '201-1000', '1000+']
    if data.get('company_size') and data['company_size'] not in valid_sizes:
        errors['company_size'] = 'Please select a valid company size'
    
    # Percentage fields validation (optional)
    percentage_fields = ['conversion_rate', 'cart_abandonment_rate']
    for field in percentage_fields:
        if data.get(field):
            try:
                value = float(data[field])
                if value < 0 or value > 100:
                    errors[field] = f'{field.replace("_", " ").title()} must be between 0 and 100'
            except (ValueError, TypeError):
                errors[field] = f'{field.replace("_", " ").title()} must be a valid percentage'
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_calculation_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate data for real-time calculations
    """
    errors = {}
    
    # Monthly revenue is required for calculations
    if not data.get('monthly_revenue'):
        errors['monthly_revenue'] = 'Monthly revenue is required for calculations'
    else:
        try:
            value = float(data['monthly_revenue'])
            if value <= 0:
                errors['monthly_revenue'] = 'Monthly revenue must be greater than 0'
            elif value > 10000000:
                errors['monthly_revenue'] = 'Monthly revenue seems unusually high'
        except (ValueError, TypeError):
            errors['monthly_revenue'] = 'Monthly revenue must be a valid number'
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def sanitize_form_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize form data to prevent XSS and other attacks
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            value = re.sub(r'[<>"\']', '', value)
            # Trim whitespace
            value = value.strip()
            # Limit length based on field type
            if key in ['first_name', 'last_name']:
                value = value[:50]
            elif key == 'email':
                value = value[:255]
            elif key in ['company', 'website']:
                value = value[:200]
            elif key == 'phone':
                value = value[:20]
            else:
                value = value[:500]
        
        sanitized[key] = value
    
    return sanitized
