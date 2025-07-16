"""
Production database configuration and utilities
"""
import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def configure_database(app):
    """Configure database for production deployment"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        if parsed.scheme == 'postgresql':
            # PostgreSQL configuration for production
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 10,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'connect_args': {
                    'sslmode': 'require',
                    'connect_timeout': 30
                }
            }
            logger.info("✅ Configured PostgreSQL database")
            
        elif parsed.scheme == 'mysql':
            # MySQL configuration
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 10,
                'pool_recycle': 3600,
                'pool_pre_ping': True
            }
            logger.info("✅ Configured MySQL database")
            
        else:
            # Fallback to SQLite for development
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roi_calculator.db'
            logger.warning("⚠️ Using SQLite fallback database")
    else:
        # Default SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roi_calculator.db'
        logger.info("📝 Using SQLite development database")
    
    # Common database settings
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    
    return app.config['SQLALCHEMY_DATABASE_URI']

def create_database_indexes(db):
    """Create database indexes for performance"""
    try:
        # Create indexes for ROI submissions table
        db.engine.execute('''
            CREATE INDEX IF NOT EXISTS idx_roi_submissions_email 
            ON roi_submissions(email)
        ''')
        
        db.engine.execute('''
            CREATE INDEX IF NOT EXISTS idx_roi_submissions_created_at 
            ON roi_submissions(created_at)
        ''')
        
        db.engine.execute('''
            CREATE INDEX IF NOT EXISTS idx_roi_submissions_lead_tier 
            ON roi_submissions(lead_tier)
        ''')
        
        db.engine.execute('''
            CREATE INDEX IF NOT EXISTS idx_roi_submissions_hubspot_synced 
            ON roi_submissions(hubspot_synced)
        ''')
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating database indexes: {e}")

def test_database_connection(app):
    """Test database connection"""
    try:
        with app.app_context():
            db.engine.execute('SELECT 1')
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def backup_database():
    """Create database backup (for SQLite)"""
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'roi_calculator_backup_{timestamp}.db'
        
        shutil.copy2('roi_calculator.db', backup_name)
        logger.info(f"✅ Database backup created: {backup_name}")
        return backup_name
        
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        return None

def optimize_database():
    """Optimize database performance"""
    try:
        # SQLite optimization
        db.engine.execute('VACUUM')
        db.engine.execute('ANALYZE')
        logger.info("✅ Database optimization completed")
        
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
