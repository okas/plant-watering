import os
from backend import create_app
app = create_app(os.getenv('PLANTWATER_ENVIRONMENT', 'website_production'))
