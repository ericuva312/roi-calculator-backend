from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class ROISubmission(db.Model):
    __tablename__ = 'roi_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Contact Information
    email = db.Column(db.String(255), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    
    # Business Information
    industry = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    business_stage = db.Column(db.String(50))
    
    # Financial Data
    monthly_revenue = db.Column(db.Float, nullable=False)
    average_order_value = db.Column(db.Float, nullable=False)
    monthly_orders = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Float)
    customer_acquisition_cost = db.Column(db.Float)
    customer_lifetime_value = db.Column(db.Float)
    
    # ROI Calculations
    conservative_roi = db.Column(db.Float)
    expected_roi = db.Column(db.Float)
    optimistic_roi = db.Column(db.Float)
    
    conservative_revenue = db.Column(db.Float)
    expected_revenue = db.Column(db.Float)
    optimistic_revenue = db.Column(db.Float)
    
    # Lead Scoring
    lead_score = db.Column(db.Integer, default=0)
    lead_tier = db.Column(db.String(20))  # Hot, Warm, Cold
    
    # Integration IDs
    hubspot_contact_id = db.Column(db.String(50))
    hubspot_deal_id = db.Column(db.String(50))
    
    # Tracking
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.String(500))
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Status
    email_sent = db.Column(db.Boolean, default=False)
    hubspot_synced = db.Column(db.Boolean, default=False)
    follow_up_scheduled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ROISubmission {self.email} - {self.lead_tier}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'monthly_revenue': self.monthly_revenue,
            'lead_score': self.lead_score,
            'lead_tier': self.lead_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
