import os
from website import create_app
app = create_app(os.getenv('PLANTWATER_ENVIRONMENT', 'production'))
