from django.template import Library

register = Library()

@register.inclusion_tag('tool/reports/single-report/partial-company-file.html')
def company_form(form):
    return {'company_form': form}