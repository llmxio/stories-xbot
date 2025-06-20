import json
import os
from threading import Lock
from typing import Any, Dict

_LOCALES_PATH = os.path.join(os.path.dirname(__file__), "../locales")
_SUPPORTED_LOCALES = ["en", "ru", "zh"]
_DEFAULT_LOCALE = "en"


class I18n:
    _translations: Dict[str, Dict[str, str]] = {}
    _lock = Lock()

    @classmethod
    def load_translations(cls):
        with cls._lock:
            if cls._translations:
                return
            for locale in _SUPPORTED_LOCALES:
                path = os.path.join(_LOCALES_PATH, f"{locale}.json")
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cls._translations[locale] = json.load(f)
                except FileNotFoundError:
                    cls._translations[locale] = {}

    @classmethod
    def t(cls, locale: str, key: str, **kwargs: Any) -> str:
        cls.load_translations()
        locale = locale if locale in _SUPPORTED_LOCALES else _DEFAULT_LOCALE
        value = cls._translations.get(locale, {}).get(key)
        if value is None:
            value = cls._translations[_DEFAULT_LOCALE].get(key, key)
        if kwargs:
            try:
                value = value.format(**kwargs)
            except Exception:
                pass
        return value


def t(locale: str, key: str, **kwargs: Any) -> str:
    return I18n.t(locale, key, **kwargs)
