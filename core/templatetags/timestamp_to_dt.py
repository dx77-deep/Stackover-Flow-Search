from django import template    
register = template.Library()
from datetime import datetime
import time 

@register.filter('timestamp_to_dt')
def convert_timestamp_to_dt(timestamp):
    try:
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.fromtimestamp(ts)