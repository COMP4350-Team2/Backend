from cupboard_app.models import (
    ListName,
    User,
    UserListIngredients,
    Recipe,
    CustomIngredient
)


"""
Runs one-time script to remove load test values from the database.
"""
CustomIngredient.objects.filter(name='load_test_ingredient').delete()

ListName.objects.filter(list_name='load_test_list').delete()
ListName.objects.filter(list_name='load_test_list2').delete()

query = User.objects.filter(email__contains='cupboard_load_test')
for user in query:
    UserListIngredients.objects.filter(user__id=user.id).delete()
    Recipe.objects.filter(user__id=user.id).delete()
query.delete()
