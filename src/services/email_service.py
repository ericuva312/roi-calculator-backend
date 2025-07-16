"""
Email Service for ROI Calculator with SendGrid Integration
"""
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        self.from_email = Email("hello@chimehq.co", "Chime HQ")
    
    def send_confirmation_email(self, submission, form_data):
        """Send confirmation email to customer with ROI projections"""
        try:
            # Calculate projections
            monthly_revenue = float(form_data['monthly_revenue'])
            projections = {
                'conservative': monthly_revenue * 1.10,
                'expected': monthly_revenue * 1.30,
                'optimistic': monthly_revenue * 1.50
            }
            
            # Create email content
            subject = f"Your ROI Analysis Results - {projections['expected']:,.0f}/month Potential"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; }}
                    .projection {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
                    .cta {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                    .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Your ROI Analysis Results</h1>
                        <p>Personalized projections for {form_data.get('first_name', 'your business')}</p>
                    </div>
                    
                    <div class="content">
                        <h2>Hello {form_data.get('first_name', 'there')}!</h2>
                        
                        <p>Thank you for using our ROI Calculator. Based on your current monthly revenue of <strong>${monthly_revenue:,.0f}</strong>, here are your personalized growth projections:</p>
                        
                        <div class="projection">
                            <h3>🎯 Expected Scenario (Most Likely)</h3>
                            <p><strong>New Monthly Revenue: ${projections['expected']:,.0f}</strong></p>
                            <p>Monthly Increase: ${projections['expected'] - monthly_revenue:,.0f}</p>
                            <p>Annual Benefit: ${(projections['expected'] - monthly_revenue) * 12:,.0f}</p>
                            <p>ROI: 400%</p>
                        </div>
                        
                        <div class="projection">
                            <h3>🚀 Optimistic Scenario (Best Case)</h3>
                            <p><strong>New Monthly Revenue: ${projections['optimistic']:,.0f}</strong></p>
                            <p>Monthly Increase: ${projections['optimistic'] - monthly_revenue:,.0f}</p>
                            <p>Annual Benefit: ${(projections['optimistic'] - monthly_revenue) * 12:,.0f}</p>
                            <p>ROI: 700%</p>
                        </div>
                        
                        <div class="projection">
                            <h3>📈 Conservative Scenario (Minimum Expected)</h3>
                            <p><strong>New Monthly Revenue: ${projections['conservative']:,.0f}</strong></p>
                            <p>Monthly Increase: ${projections['conservative'] - monthly_revenue:,.0f}</p>
                            <p>Annual Benefit: ${(projections['conservative'] - monthly_revenue) * 12:,.0f}</p>
                            <p>ROI: 150%</p>
                        </div>
                        
                        <h3>🎯 Your Lead Score: {submission.lead_score}/150 ({submission.lead_tier} Priority)</h3>
                        
                        <p>Our team will contact you within <strong>{self.get_follow_up_time(submission.lead_tier)}</strong> to discuss how we can help you achieve these results.</p>
                        
                        <a href="https://calendly.com/chimehq/roi-consultation" class="cta">Schedule Your Free Consultation</a>
                        
                        <p>Questions? Reply to this email or call us at (555) 123-4567.</p>
                        
                        <p>Best regards,<br>The Chime HQ Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>&copy; 2024 Chime HQ. All rights reserved.</p>
                        <p>You received this email because you requested an ROI analysis.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            mail = Mail(
                from_email=self.from_email,
                to_emails=To(form_data['email']),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(mail)
            logger.info(f"✅ Confirmation email sent to {form_data['email']}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'Confirmation email sent successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending confirmation email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_internal_notification(self, submission, form_data):
        """Send internal notification to sales team"""
        try:
            subject = f"🔥 New {submission.lead_tier} Lead: {form_data.get('first_name')} {form_data.get('last_name')} (Score: {submission.lead_score})"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>New ROI Calculator Submission</h2>
                
                <h3>Lead Information</h3>
                <ul>
                    <li><strong>Name:</strong> {form_data.get('first_name')} {form_data.get('last_name')}</li>
                    <li><strong>Email:</strong> {form_data.get('email')}</li>
                    <li><strong>Phone:</strong> {form_data.get('phone', 'Not provided')}</li>
                    <li><strong>Company:</strong> {form_data.get('company', 'Not provided')}</li>
                    <li><strong>Website:</strong> {form_data.get('website', 'Not provided')}</li>
                </ul>
                
                <h3>Business Details</h3>
                <ul>
                    <li><strong>Industry:</strong> {form_data.get('industry', 'Not specified')}</li>
                    <li><strong>Company Size:</strong> {form_data.get('company_size', 'Not specified')}</li>
                    <li><strong>Business Stage:</strong> {form_data.get('business_stage', 'Not specified')}</li>
                    <li><strong>Monthly Revenue:</strong> ${float(form_data.get('monthly_revenue', 0)):,.0f}</li>
                    <li><strong>Average Order Value:</strong> ${float(form_data.get('average_order_value', 0)):,.0f}</li>
                    <li><strong>Monthly Orders:</strong> {int(form_data.get('monthly_orders', 0)):,}</li>
                </ul>
                
                <h3>Lead Scoring</h3>
                <ul>
                    <li><strong>Lead Score:</strong> {submission.lead_score}/150</li>
                    <li><strong>Tier:</strong> {submission.lead_tier}</li>
                    <li><strong>Follow-up Priority:</strong> {self.get_follow_up_time(submission.lead_tier)}</li>
                </ul>
                
                <h3>ROI Projections</h3>
                <ul>
                    <li><strong>Expected Monthly Revenue:</strong> ${float(form_data.get('monthly_revenue', 0)) * 1.30:,.0f}</li>
                    <li><strong>Expected Annual Benefit:</strong> ${(float(form_data.get('monthly_revenue', 0)) * 0.30) * 12:,.0f}</li>
                </ul>
                
                <h3>Next Steps</h3>
                <p>Contact this lead within <strong>{self.get_follow_up_time(submission.lead_tier)}</strong>.</p>
                
                <p><strong>Submission ID:</strong> {submission.id}</p>
                <p><strong>Timestamp:</strong> {submission.created_at}</p>
            </body>
            </html>
            """
            
            mail = Mail(
                from_email=self.from_email,
                to_emails=To("hello@chimehq.co"),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(mail)
            logger.info(f"✅ Internal notification sent for submission {submission.id}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message': 'Internal notification sent successfully'
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending internal notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_follow_up_time(self, tier):
        """Get follow-up time based on lead tier"""
        times = {
            'Hot': '1 hour',
            'Warm': '24 hours',
            'Cold': '3 days'
        }
        return times.get(tier, '24 hours')
