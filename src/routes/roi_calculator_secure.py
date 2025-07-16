"""
ROI Calculator API Routes with Security and Monitoring
"""
from flask import Blueprint, request, jsonify
import logging
import time
from datetime import datetime

# Import models and services
from src.models.roi_submission import ROISubmission, db
from src.utils.lead_scoring import calculate_lead_score, assign_tier
from src.utils.validation import validate_roi_submission
from src.utils.security import rate_limit, sanitize_input
from src.utils.monitoring import submission_tracker, log_submission_event

# Create blueprint
roi_bp = Blueprint('roi_calculator', __name__)
logger = logging.getLogger(__name__)

@roi_bp.route('/calculate', methods=['POST'])
def calculate_roi():
    """Real-time ROI calculation endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Sanitize input
        data = sanitize_input(data)
        
        # Validate required field
        monthly_revenue = data.get('monthly_revenue')
        if not monthly_revenue or float(monthly_revenue) <= 0:
            return jsonify({'error': 'Valid monthly revenue is required'}), 400
        
        monthly_revenue = float(monthly_revenue)
        
        # Calculate projections for all scenarios
        projections = {
            'conservative': {
                'monthly_revenue': monthly_revenue * 1.10,
                'monthly_increase': monthly_revenue * 0.10,
                'annual_benefit': monthly_revenue * 0.10 * 12,
                'roi_percentage': 150,
                'break_even_months': 6,
                'conversion_improvement': '15%',
                'cost_reduction': '8%'
            },
            'expected': {
                'monthly_revenue': monthly_revenue * 1.30,
                'monthly_increase': monthly_revenue * 0.30,
                'annual_benefit': monthly_revenue * 0.30 * 12,
                'roi_percentage': 400,
                'break_even_months': 5,
                'conversion_improvement': '25%',
                'cost_reduction': '15%'
            },
            'optimistic': {
                'monthly_revenue': monthly_revenue * 1.50,
                'monthly_increase': monthly_revenue * 0.50,
                'annual_benefit': monthly_revenue * 0.50 * 12,
                'roi_percentage': 700,
                'break_even_months': 4,
                'conversion_improvement': '40%',
                'cost_reduction': '25%'
            }
        }
        
        processing_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'projections': projections,
            'processing_time': round(processing_time, 3),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"ROI calculation error: {e}")
        return jsonify({
            'error': 'Calculation failed',
            'message': 'Unable to process ROI calculation. Please try again.'
        }), 500

@roi_bp.route('/submit', methods=['POST'])
def submit_roi_form():
    """Enhanced form submission with full workflow"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Sanitize input
        data = sanitize_input(data)
        
        # Validate form data
        validation_result = validate_roi_submission(data)
        if not validation_result['valid']:
            return jsonify({
                'error': 'Validation failed',
                'field_errors': validation_result['errors']
            }), 400
        
        # Calculate lead score and tier
        lead_score = calculate_lead_score(data)
        tier = assign_tier(lead_score)
        
        # Create submission record
        submission = ROISubmission(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            company=data.get('company'),
            phone=data.get('phone'),
            website=data.get('website'),
            industry=data.get('industry'),
            company_size=data.get('company_size'),
            business_stage=data.get('business_stage'),
            monthly_revenue=float(data['monthly_revenue']),
            average_order_value=float(data['average_order_value']),
            monthly_orders=int(data['monthly_orders']),
            conversion_rate=float(data.get('conversion_rate', 0)),
            customer_acquisition_cost=float(data.get('customer_acquisition_cost', 0)),
            customer_lifetime_value=float(data.get('customer_lifetime_value', 0)),
            conservative_roi=150,
            expected_roi=400,
            optimistic_roi=700,
            conservative_revenue=float(data['monthly_revenue']) * 1.10,
            expected_revenue=float(data['monthly_revenue']) * 1.30,
            optimistic_revenue=float(data['monthly_revenue']) * 1.50,
            lead_score=lead_score,
            lead_tier=tier,
            ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
            user_agent=request.headers.get('User-Agent'),
            referrer=request.headers.get('Referer')
        )
        
        # Save to database
        db.session.add(submission)
        db.session.commit()
        
        log_submission_event(submission.id, 'submission_created', {
            'tier': tier,
            'lead_score': lead_score,
            'industry': data.get('industry')
        })
        
        # Record successful submission
        processing_time = time.time() - start_time
        submission_tracker.record_success(submission.id, processing_time)
        
        return jsonify({
            'success': True,
            'message': 'Your ROI analysis has been submitted successfully!',
            'submission_id': submission.id,
            'lead_score': lead_score,
            'tier': tier,
            'processing_time': round(processing_time, 3),
            'next_steps': {
                'email_confirmation': 'Check your email for detailed projections',
                'follow_up': f'Our team will contact you within {get_follow_up_time(tier)}',
                'calendar_link': 'https://calendly.com/chimehq/roi-consultation'
            }
        })
        
    except Exception as e:
        logger.error(f"Submission processing error: {e}")
        return jsonify({
            'error': 'Submission failed',
            'message': 'Unable to process your submission. Please try again or contact support.'
        }), 500

def get_follow_up_time(tier):
    """Get follow-up time based on lead tier"""
    follow_up_times = {
        'Hot': '1 hour',
        'Warm': '24 hours',
        'Cold': '3 days'
    }
    return follow_up_times.get(tier, '24 hours')
