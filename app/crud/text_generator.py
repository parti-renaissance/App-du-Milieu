from os import environ

import requests
from better_profanity import profanity


def sanitize_text(text: str):
    return text.encode("utf8").decode("utf8","ignore")


def censor_profanity(text: str):
    return profanity.censor(text)


def translate_text(
        text: str,
        from_language: str = 'FR',
        target_lang: str = 'EN'
):
    payload = {
        'auth_key': environ["DEEPL_KEY"],
        'text': text,
        'from_language': from_language,
        'target_lang': target_lang
    }
    res = requests.get('https://api.deepl.com/v2/translate', params=payload)
    return res.json()


def generate_text(
    text: str,
    from_language: str = 'FR'):
    # Translate text to EN
    if from_language != 'EN':
        translated = translate_text(
            text,
            from_language=from_language,
            target_lang='EN')['translations'][0]
    else:
        translated = text

    # Generate EN text
    generated = requests.post(
        "https://api.deepai.org/api/text-generator",
        data=translated,
        headers={'api-key': environ["DEEP_IA_KEY"]}
    ).json()

    # Censor profainty before output
    censored = censor_profanity(generated['output'])

    # Translate back to from_language
    if from_language != 'EN':
        return translate_text(
            censored,
            from_language='EN',
            target_lang=from_language)['translations'][0]
    else:
        return generated['output']
