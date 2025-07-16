"""
Lead Scoring Algorithm for ROI Calculator
150-point scoring system with demographic, behavioral, and fit scoring
"""
import logging

logger = logging.getLogger(__name__)

def calculate_lead_score(data):
    """
    Calculate comprehensive lead score (0-150 points)
    """
    score = 0
    
    # Demographic Scoring (50 points max)
    score += calculate_demographic_score(data)
    
    # Behavioral Scoring (50 points max)
    score += calculate_behavioral_score(data)
    
    # Fit Scoring (50 points max)
    score += calculate_fit_score(data)
    
    # Ensure score is within bounds
    score = max(0, min(150, score))
    
    logger.info(f"Lead score calculated: {score}/150 for {data.get('email', 'unknown')}")
    return score

def calculate_demographic_score(data):
    """Calculate demographic-based score (50 points max)"""
    score = 0
    
    # Company size scoring (15 points max)
    company_size = data.get('company_size', '')
    size_scores = {
        '1-10': 5,      # Small business
        '11-50': 10,    # Growing business
        '51-200': 15,   # Mid-market (ideal)
        '201-1000': 12, # Enterprise
        '1000+': 8      # Very large enterprise
    }
    score += size_scores.get(company_size, 0)
    
    # Industry scoring (15 points max)
    industry = data.get('industry', '')
    industry_scores = {
        'E-commerce': 15,    # Perfect fit
        'SaaS': 12,          # Great fit
        'Retail': 12,        # Great fit
        'Technology': 10,    # Good fit
        'Marketing': 10,     # Good fit
        'Healthcare': 8,     # Moderate fit
        'Finance': 8,        # Moderate fit
        'Education': 6,      # Lower fit
        'Real Estate': 6,    # Lower fit
        'Manufacturing': 4,  # Lower fit
        'Consulting': 4,     # Lower fit
        'Other': 2          # Unknown fit
    }
    score += industry_scores.get(industry, 0)
    
    # Business stage scoring (10 points max)
    business_stage = data.get('business_stage', '')
    stage_scores = {
        'Growth': 10,        # Perfect timing
        'Established': 8,    # Good timing
        'Startup': 6,        # Early but potential
        'Enterprise': 4      # Harder to change
    }
    score += stage_scores.get(business_stage, 0)
    
    # Website presence (10 points max)
    if data.get('website'):
        score += 10
    
    return score

def calculate_behavioral_score(data):
    """Calculate behavior-based score (50 points max)"""
    score = 0
    
    # Revenue size scoring (25 points max)
    monthly_revenue = float(data.get('monthly_revenue', 0))
    if monthly_revenue >= 100000:      # $100k+/month
        score += 25
    elif monthly_revenue >= 50000:     # $50k-100k/month
        score += 20
    elif monthly_revenue >= 25000:     # $25k-50k/month
        score += 15
    elif monthly_revenue >= 10000:     # $10k-25k/month
        score += 10
    elif monthly_revenue >= 5000:      # $5k-10k/month
        score += 5
    # Below $5k/month = 0 points
    
    # Order volume scoring (15 points max)
    monthly_orders = int(data.get('monthly_orders', 0))
    if monthly_orders >= 1000:        # High volume
        score += 15
    elif monthly_orders >= 500:       # Good volume
        score += 12
    elif monthly_orders >= 200:       # Moderate volume
        score += 8
    elif monthly_orders >= 50:        # Low volume
        score += 4
    # Below 50 orders = 0 points
    
    # Average order value scoring (10 points max)
    aov = float(data.get('average_order_value', 0))
    if aov >= 200:                     # High value
        score += 10
    elif aov >= 100:                   # Good value
        score += 8
    elif aov >= 50:                    # Moderate value
        score += 5
    elif aov >= 25:                    # Low value
        score += 2
    # Below $25 AOV = 0 points
    
    return score

def calculate_fit_score(data):
    """Calculate product fit score (50 points max)"""
    score = 0
    
    # Conversion rate indicates optimization need (15 points max)
    conversion_rate = float(data.get('conversion_rate', 0))
    if conversion_rate > 0:
        if conversion_rate < 2:        # Low conversion = high need
            score += 15
        elif conversion_rate < 3:      # Below average = good need
            score += 12
        elif conversion_rate < 5:      # Average = moderate need
            score += 8
        elif conversion_rate < 8:      # Good = some need
            score += 4
        # Above 8% = minimal need = 0 points
    
    # Cart abandonment indicates optimization opportunity (15 points max)
    abandonment_rate = float(data.get('cart_abandonment_rate', 0))
    if abandonment_rate > 0:
        if abandonment_rate > 70:      # High abandonment = high opportunity
            score += 15
        elif abandonment_rate > 60:    # Above average = good opportunity
            score += 12
        elif abandonment_rate > 50:    # Average = moderate opportunity
            score += 8
        elif abandonment_rate > 40:    # Below average = some opportunity
            score += 4
        # Below 40% = minimal opportunity = 0 points
    
    # Manual hours indicates automation need (10 points max)
    manual_hours = int(data.get('manual_hours_per_week', 0))
    if manual_hours >= 20:             # High manual work
        score += 10
    elif manual_hours >= 10:           # Moderate manual work
        score += 7
    elif manual_hours >= 5:            # Some manual work
        score += 4
    elif manual_hours >= 1:            # Minimal manual work
        score += 1
    # 0 hours = 0 points
    
    # Ad spend indicates growth investment (10 points max)
    ad_spend = float(data.get('monthly_ad_spend', 0))
    if ad_spend >= 10000:              # High ad spend
        score += 10
    elif ad_spend >= 5000:             # Good ad spend
        score += 8
    elif ad_spend >= 2000:             # Moderate ad spend
        score += 5
    elif ad_spend >= 500:              # Some ad spend
        score += 2
    # Below $500 = 0 points
    
    return score

def assign_tier(lead_score):
    """
    Assign lead tier based on score
    Hot: 100-150 points (top 20%)
    Warm: 60-99 points (middle 60%)
    Cold: 0-59 points (bottom 20%)
    """
    if lead_score >= 100:
        return 'Hot'
    elif lead_score >= 60:
        return 'Warm'
    else:
        return 'Cold'

def get_lead_insights(data, score, tier):
    """Generate insights about the lead for sales team"""
    insights = []
    
    # Revenue insights
    monthly_revenue = float(data.get('monthly_revenue', 0))
    if monthly_revenue >= 50000:
        insights.append(f"High revenue business (${monthly_revenue:,.0f}/month)")
    elif monthly_revenue >= 10000:
        insights.append(f"Growing business (${monthly_revenue:,.0f}/month)")
    
    # Industry insights
    industry = data.get('industry', '')
    if industry in ['E-commerce', 'SaaS', 'Retail']:
        insights.append(f"Perfect fit industry: {industry}")
    elif industry in ['Technology', 'Marketing']:
        insights.append(f"Good fit industry: {industry}")
    
    # Optimization opportunities
    conversion_rate = float(data.get('conversion_rate', 0))
    if conversion_rate > 0 and conversion_rate < 3:
        insights.append("Low conversion rate - high optimization potential")
    
    abandonment_rate = float(data.get('cart_abandonment_rate', 0))
    if abandonment_rate > 60:
        insights.append("High cart abandonment - major opportunity")
    
    # Manual work insights
    manual_hours = int(data.get('manual_hours_per_week', 0))
    if manual_hours >= 10:
        insights.append(f"High manual workload ({manual_hours} hrs/week) - automation opportunity")
    
    return insights

def get_follow_up_priority(tier):
    """Get follow-up timing based on tier"""
    priorities = {
        'Hot': {
            'timing': '1 hour',
            'priority': 'Immediate',
            'approach': 'Phone call + personalized email'
        },
        'Warm': {
            'timing': '24 hours',
            'priority': 'High',
            'approach': 'Personalized email + follow-up call'
        },
        'Cold': {
            'timing': '3 days',
            'priority': 'Standard',
            'approach': 'Email nurture sequence'
        }
    }
    return priorities.get(tier, priorities['Cold'])
