from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def label_with_required(field):
    label = field.label or ""
    required = ""
    if field.field.required:
        required = '<abbr title="required" class="text-danger">*</abbr>'
    return mark_safe(f'<label for="{field.id_for_label}">{label} {required}</label>')
