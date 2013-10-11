# -*- coding: utf-8 -*-
import os

from django.conf import settings
from Crypto.PublicKey import RSA


def get_keys_from_disk(key_name=None, base_path=None):
    if not base_path:
        base_path = settings.SSH_KEY_PATH
    if not key_name:
        key_name = settings.SSH_KEY_NAME
    result = {'pub_key': '', 'priv_key': ''}
    keys = (key_name, '%s.pub' % key_name)
    for key in keys:
        key_path = os.path.join(base_path, key)
        key_file = open(key_path, 'r').read()
        proper_key = RSA.importKey(key_file)
        key_map = 'pub_key' if key.endswith('.pub') else 'priv_key'
        result[key_map] = proper_key
    return result

def get_public_key(key_name=None, base_path=None):
    keys = get_keys_from_disk(key_name, base_path)
    return keys.get('pub_key', '')
