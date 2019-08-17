from django import template
register = template.Library()

@register.filter(name='humanize_timedelta')
def humanize_timedelta(seconds, fmt='{minutes:02d}:{seconds:02d}'):
    try:
        d = {}
        d['minutes'], d['seconds'] = divmod(seconds, 60)
        return fmt.format(**d)
    except (ValueError, TypeError):
        return '---'