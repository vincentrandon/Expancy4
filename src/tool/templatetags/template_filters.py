from django.template.defaulttags import register


@register.filter
def get_item_transporter(dictionary, key):
    list_transporters = dictionary.get(key)
    return list_transporters

@register.filter
def get_item_from_list(list, key):
    return list[key]
