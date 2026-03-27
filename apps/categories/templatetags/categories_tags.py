from django import template
from categories.models import Category

register = template.Library()

@register.simple_tag
def get_category_info(category_name):
    try:
        cat = Category.objects.filter(name=category_name).first()
        if cat and cat.created_by:
            return {
                'created_by': cat.created_by.username,
                'created_at': cat.created_at.strftime('%b %d, %Y')
            }
    except:
        pass
    return {'created_by': None, 'created_at': None}
