import aiogram.utils.exceptions
from py_currency_converter import convert

import config
from handlers.init import *
import re


async def delete_last_messages(msg: Message, count: int = 3):
    """Удаляет последние N сообщений до команды."""

    for i in range(0, count):
        try:
            await bot.delete_message(chat_id=msg.from_user.id,
                                     message_id=msg.message_id - i)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass


async def start_cmd_handler(msg: Message, state: FSMContext):
    await state.finish()

    answer = ('💸 Напиши любую валюту '
              'любым способом и я конвертирую её')

    await msg.answer_sticker(sticker='CAACAgIAAxkBAAMKZCqF8NxyEdlQYjNX0uQ-kMCKBRsAAvINAAK7fWBIH8H7_ft7nyovBA')
    await msg.answer(text=answer, parse_mode='markdown')


async def converter_msg_handler(msg: Message):
    # Ищу только суммы
    # amount_regex = r'(?P<amount>\d+(?:[,.]\d+)?(?:кк|kk|[kK]|[кК])?)'
    # matches = re.findall(amount_regex, msg.text.lower())[0]

    # Ищу пары сумма валюта в тексте
    currency_regex = r'(?P<amount>\d+(?:[,.]\d+)?(?:кк|kk|[kK]|[кК])?)\s*(?P<currency>' \
                     r'USD|\$|руб?|uah?|rub?|бачей?|грн|грив(?:на|ен|ень)?|бак(?:с|сы)?|₽|usd)'
    matches = re.findall(currency_regex, msg.text.lower())

    for match in matches:

        # Обрабатываю валюты. Получаю сумму и код валюты.
        amount = match[0]

        # Умножаю на к/k
        if 'k' in amount or 'к' in amount:
            amount = float(amount.replace('k', '000').replace('к', '000'))
        else:
            amount = float(amount)

        # Преобразовываю код валюты к нужному либе виду ($=USD, рубль=RUB)
        currency = match[1]
        currency_code = ''
        for _currency in config.CURRENCIES:
            if currency in config.CURRENCIES[_currency]:
                currency_code = _currency

        if not currency_code:
            currency_code = 'RUB'

        raw_converted = convert(base=currency_code, amount=int(amount),
                                to=config.CURRENCIES.keys())

        # Округляю до двух чисел после запятой
        converted = {}
        for currency in raw_converted:
            converted[currency] = round(raw_converted[currency], 2)

        # Формирование ответа (главная валюта первая, а остальные - потом)

        answer = '%s *%s %s*\n\n' % (config.CURRENCIES_FLAGS[currency_code],
                                     converted[currency_code], currency_code)

        currencies = [i for i in config.CURRENCIES]
        currencies.remove(currency_code)

        for _currency in currencies:
            answer += '%s *%s %s*\n' % (config.CURRENCIES_FLAGS[_currency],
                                        converted[_currency], _currency)

        await msg.answer(text=answer, parse_mode='markdown')


async def get_sticker_id_handler(msg: Message):
    await msg.answer_sticker(sticker=msg.sticker.file_id)
    print(msg.sticker.file_id)
