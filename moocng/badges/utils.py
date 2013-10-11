# -*- coding: utf-8 -*-
import os

from django.conf import settings
from Crypto.PublicKey import RSA


def get_openbadge_keys():
    base_path = settings.SSH_KEY_PATH
    key_name = settings.SSH_KEY_NAME
    result = {'priv_key': '', 'pub_key': ''}
    keys = (key_name, '%s.pub' % key_name)
    for k_name in keys:
        key_path = os.path.join(base_path, k_name)
        key_file = open(key_path, 'r').read()
        proper_key = RSA.importKey(key_file)
        map_key = 'pub_key' if k_name.endswith('.pub') else 'priv_key'
        result[map_key] = proper_key
    return result


def get_openbadge_public_key():
    base_path = settings.SSH_KEY_PATH
    key_name = settings.SSH_KEY_NAME
    pub_key_name = '%s.pub' % key_name
    key_path = os.path.join(base_path, pub_key_name)
    key_file = open(key_path, 'r').read()
    return key_file
