"""
HubSpot CRM Integration Service
"""
import os
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HubSpotService:
    def __init__(self):
        self.api_key = os.getenv('HUBSPOT_API_KEY')
        self.base_url = 'https://api.hubapi.com'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def upsert_contact(self, form_data, lead_score, tier):
        """Create or update contact in HubSpot"""
        try:
            email = form_data.get('email')
            
            # Prepare contact data
            contact_data = {
                'properties': {
                    'email': email,
                    'firstname': form_data.get('first_name'),
                    'lastname': form_data.get('last_name'),
                    'company': form_data.get('company'),
                    'phone': form_data.get('phone'),
                    'website': form_data.get('website'),
                    'industry': form_data.get('industry'),
                    'company_size': form_data.get('company_size'),
                    'business_stage': form_data.get('business_stage'),
                    'monthly_revenue': str(form_data.get('monthly_revenue')),
                    'average_order_value': str(form_data.get('average_order_value')),
                    'monthly_orders': str(form_data.get('monthly_orders')),
                    'lead_score': str(lead_score),
                    'lead_tier': tier,
                    'roi_calculator_submission': 'true',
                    'submission_date': datetime.now().isoformat(),
                    'lifecyclestage': 'lead'
                }
            }
            
            # Try to create contact (will update if exists)
            url = f'{self.base_url}/crm/v3/objects/contacts'
            response = requests.post(url, json=contact_data, headers=self.headers)
            
            if response.status_code in [200, 201]:
                contact_id = response.json().get('id')
                logger.info(f"✅ HubSpot contact created/updated: {contact_id}")
                return {
                    'success': True,
                    'contact_id': contact_id,
                    'action': 'created'
                }
            elif response.status_code == 409:
                # Contact exists, update it
                return self.update_existing_contact(email, contact_data['properties'])
            else:
                logger.error(f"❌ HubSpot contact creation failed: {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"❌ HubSpot contact upsert error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_existing_contact(self, email, properties):
        """Update existing contact by email"""
        try:
            # Search for contact by email
            search_url = f'{self.base_url}/crm/v3/objects/contacts/search'
            search_data = {
                'filterGroups': [{
                    'filters': [{
                        'propertyName': 'email',
                        'operator': 'EQ',
                        'value': email
                    }]
                }]
            }
            
            search_response = requests.post(search_url, json=search_data, headers=self.headers)
            
            if search_response.status_code == 200:
                results = search_response.json().get('results', [])
                if results:
                    contact_id = results[0]['id']
                    
                    # Update contact
                    update_url = f'{self.base_url}/crm/v3/objects/contacts/{contact_id}'
                    update_data = {'properties': properties}
                    
                    update_response = requests.patch(update_url, json=update_data, headers=self.headers)
                    
                    if update_response.status_code == 200:
                        logger.info(f"✅ HubSpot contact updated: {contact_id}")
                        return {
                            'success': True,
                            'contact_id': contact_id,
                            'action': 'updated'
                        }
            
            return {
                'success': False,
                'error': 'Contact not found for update'
            }
            
        except Exception as e:
            logger.error(f"❌ HubSpot contact update error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_deal(self, form_data, contact_id, lead_score):
        """Create deal in HubSpot"""
        try:
            monthly_revenue = float(form_data.get('monthly_revenue', 0))
            deal_value = monthly_revenue * 0.30 * 12  # Expected annual benefit
            
            deal_data = {
                'properties': {
                    'dealname': f"ROI Calculator Lead - {form_data.get('first_name')} {form_data.get('last_name')}",
                    'amount': str(deal_value),
                    'dealstage': 'appointmentscheduled',
                    'pipeline': 'default',
                    'closedate': (datetime.now() + timedelta(days=30)).isoformat(),
                    'lead_source': 'ROI Calculator',
                    'lead_score': str(lead_score),
                    'monthly_revenue': str(monthly_revenue),
                    'expected_annual_benefit': str(deal_value)
                },
                'associations': [{
                    'to': {'id': contact_id},
                    'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 3}]
                }]
            }
            
            url = f'{self.base_url}/crm/v3/objects/deals'
            response = requests.post(url, json=deal_data, headers=self.headers)
            
            if response.status_code in [200, 201]:
                deal_id = response.json().get('id')
                logger.info(f"✅ HubSpot deal created: {deal_id}")
                return {
                    'success': True,
                    'deal_id': deal_id
                }
            else:
                logger.error(f"❌ HubSpot deal creation failed: {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"❌ HubSpot deal creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_follow_up_task(self, contact_id, tier):
        """Create follow-up task based on lead tier"""
        try:
            # Determine task timing based on tier
            timing_map = {
                'Hot': 1,      # 1 hour
                'Warm': 24,    # 24 hours
                'Cold': 72     # 72 hours (3 days)
            }
            
            hours_delay = timing_map.get(tier, 24)
            due_date = datetime.now() + timedelta(hours=hours_delay)
            
            task_data = {
                'properties': {
                    'hs_task_subject': f'Follow up with {tier} ROI Calculator lead',
                    'hs_task_body': f'Contact this {tier} priority lead from ROI Calculator submission. Lead score indicates high potential.',
                    'hs_task_status': 'NOT_STARTED',
                    'hs_task_priority': 'HIGH' if tier == 'Hot' else 'MEDIUM' if tier == 'Warm' else 'LOW',
                    'hs_timestamp': due_date.isoformat(),
                    'hs_task_type': 'CALL'
                },
                'associations': [{
                    'to': {'id': contact_id},
                    'types': [{'associationCategory': 'HUBSPOT_DEFINED', 'associationTypeId': 204}]
                }]
            }
            
            url = f'{self.base_url}/crm/v3/objects/tasks'
            response = requests.post(url, json=task_data, headers=self.headers)
            
            if response.status_code in [200, 201]:
                task_id = response.json().get('id')
                logger.info(f"✅ HubSpot follow-up task created: {task_id}")
                return {
                    'success': True,
                    'task_id': task_id
                }
            else:
                logger.error(f"❌ HubSpot task creation failed: {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"❌ HubSpot task creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
