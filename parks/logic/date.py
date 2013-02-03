from datetime import datetime

def format_date(dt):
    if dt is None:
        return 'Never'
    return datetime.strftime(dt, '%Y-%m-%d')
