from django import template
from django.urls import reverse

register = template.Library()


# have to include icon code later
@register.inclusion_tag('admin_theme/menu_bar.html')
def show_admin_menu(user):
    main_menu = [
        {
            "name": "Dashboard",
            "childs": [
                {
                    "name": "Dashboard",
                    "url": reverse("user_dashboard"),
                }
            ]

        },

        {
            "name": "Patient",
            "childs":
                [
                    {
                        "name": "New Diagnosis",
                        "url": reverse("check_patient"),
                        # "permission": 'kctusers.add_user'
                    },

                ]
        },

    ]

    filtered_menu = []
    user_permissions = user.get_all_permissions()
    for menu in main_menu:
        item = {'name': menu['name']}
        if "childs" in menu:
            item['childs'] = []
            for child in menu['childs']:
                if 'permission' in child:
                    if child['permission'] in user_permissions:
                        item["childs"].append(child)
                    else:
                        if isinstance(child['permission'], tuple):
                            for perm in child['permission']:
                                if perm in user_permissions:
                                    item["childs"].append(child)
                else:
                    item["childs"].append(child)
        filtered_menu.append(item)

    return {"menus": filtered_menu}
