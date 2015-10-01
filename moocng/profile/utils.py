# -*- coding: utf-8 -*-
from moocng.users.models import User

def get_user(id):
    return User.objects.get(id=id)
