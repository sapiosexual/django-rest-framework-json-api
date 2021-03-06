"""
This module provides the `json_api_settings` object that is used to access
JSON API REST framework settings, checking for user settings first, then falling back to
the defaults.
"""

from django.conf import settings
from django.core.signals import setting_changed
import warnings

JSON_API_SETTINGS_PREFIX = 'JSON_API_'

RELATIONS_RENDERING_STRATEGY = 'RELATIONS'
ATTRIBUTE_RENDERING_STRATEGY = 'ATTRIBUTE'

DEFAULTS = {
    'FORMAT_FIELD_NAMES': False,
    'FORMAT_TYPES': False,
    'PLURALIZE_TYPES': False,
    'UNIFORM_EXCEPTIONS': False,
    'NESTED_SERIALIZERS_RENDERING_STRATEGY': RELATIONS_RENDERING_STRATEGY
}


class JSONAPISettings(object):
    """
    A settings object that allows json api settings to be access as
    properties.
    """

    def __init__(self, user_settings=settings, defaults=DEFAULTS):
        self.defaults = defaults
        self.user_settings = user_settings

        value = getattr(
            self.user_settings,
            JSON_API_SETTINGS_PREFIX + 'NESTED_SERIALIZERS_RENDERING_STRATEGY',
            self.defaults['NESTED_SERIALIZERS_RENDERING_STRATEGY'])

        if value not in (RELATIONS_RENDERING_STRATEGY, ATTRIBUTE_RENDERING_STRATEGY):
            raise AttributeError("Invalid value '%s' for JSON API setting "
                                 "NESTED_SERIALIZERS_RENDERING_STRATEGY" % value)
        if value == RELATIONS_RENDERING_STRATEGY and \
                not hasattr(self.user_settings,
                            JSON_API_SETTINGS_PREFIX + 'NESTED_SERIALIZERS_RENDERING_STRATEGY'):
            warnings.warn(DeprecationWarning(
                "Rendering nested serializers in relations by default is deprecated and will be "
                "changed in future releases. Please, use ResourceRelatedField or set "
                "JSON_API_NESTED_SERIALIZERS_RENDERING_STRATEGY to RELATIONS"))

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid JSON API setting: '%s'" % attr)

        value = getattr(self.user_settings, JSON_API_SETTINGS_PREFIX + attr, self.defaults[attr])

        # Cache the result
        setattr(self, attr, value)
        return value


json_api_settings = JSONAPISettings()


def reload_json_api_settings(*args, **kwargs):
    django_setting = kwargs['setting']
    setting = django_setting.replace(JSON_API_SETTINGS_PREFIX, '')
    value = kwargs['value']
    if setting in DEFAULTS.keys():
        if value is not None:
            setattr(json_api_settings, setting, value)
        elif hasattr(json_api_settings, setting):
            delattr(json_api_settings, setting)


setting_changed.connect(reload_json_api_settings)
