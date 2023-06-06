import aiogram.utils.exceptions
import re
import config
from handlers.init import *
from aiogram.types import Message, Sticker


async def delete_last_messages(msg: Message, count: int = 3):
    """Удаляет последние N сообщений до команды."""
    for i in range(0, count):
        try:
            await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - i)
        except aiogram.utils.exceptions.MessageToDeleteNotFound:
            pass


async def start_cmd_handler(msg: Message, state):
    await state.finish()

    answer = """💸 Добро пожаловать! Я - твой персональный конвертер валют и калькулятор выражений *valcon*.

📈 Для конвертации валюты напиши сумму и код валюты через пробел, например:
• 100 USD
• 2500 RUB
• 50 EUR

🔢 Чтобы посчитать выражение, просто напиши его, используя математические операции и числа. Например:
• 2 + 2
• (30 * 2) - (20 * 5)

💰 Доступные валюты для конвертации:
• USD - Доллар США
• RUB - Российский рубль
• UAH - Украинская гривна
• EUR - Евро
• TON - Криптовалюта TON
• USDT - Криптовалюта USDT

📝 Помни, что ты также можешь написать любое выражение и я посчитаю его для тебя.

ℹ️ Более того, ты можешь использовать меня в инлайн-режиме, чтобы быстро конвертировать валюту или выполнить вычисления без необходимости открывать чат со мной. Просто упомяни мой никнейм @YourCurrencyBot в любом чате и укажи сумму и код валюты или выражение.

Примеры использования в инлайн-режиме:
• @val_con_bot 100 USD
• @val_con_bot 50 биткоинов
• @val_con_bot 2 + 2"""

    await msg.answer_sticker(sticker='CAACAgIAAxkBAAMKZCqF8NxyEdlQYjNX0uQ-kMCKBRsAAvINAAK7fWBIH8H7_ft7nyovBA')
    await msg.answer(text=answer, parse_mode='html')


async def converter_msg_handler(msg: Message):
    currency_regex = r'(\d+(?:\.\d+)?(?:к|k|тыс)?)(?:\s*([^\d\s]+))?'

    matches = re.findall(currency_regex, msg.text.lower())

    try:
        answer = calculator(msg.text)
        await msg.answer(text=answer)
    except ValueError:
        for match in matches:
            # Обрабатываю валюты. Получаю сумму и код валюты.
            amount = match[0].replace(',', '.')

            # Умножаю на к/k
            if 'k' in amount or 'к' in amount:
                amount = float(amount.replace('k', '000').replace('к', '000'))
            else:
                amount = float(amount)

            # Преобразовываю код валюты к нужному виду ($=USD, рубль=RUB)
            currency = match[1]
            currency_code = ''

            for _currency in config.CURRENCIES:
                if currency in config.CURRENCIES[_currency]:
                    currency_code = _currency

            if not currency_code:
                currency_code = 'RUB'

            if currency_code in config.CRYPTOCURRENCIES:
                crypto = cryptopay.Crypto(config.CRYPTOPAY_API_KEY, testnet=False)
                exchange_rates = crypto.getExchangeRates()['result']
                currency_rates = {}

                for rate in exchange_rates:
                    if rate['source'] == currency_code and rate['target'] in config.CURRENCIES.keys():
                        currency_rates[rate['target']] = round(float(rate['rate']) * amount, 2)
                answer = f"{config.CRYPTOCURRENCIES_FLAGS[currency_code]} {amount} {currency_code}\n\n"

                for _currency in config.CURRENCIES_FLAGS.keys():
                    answer += f"{config.CURRENCIES_FLAGS[_currency]} {add_spaces(currency_rates[_currency])} {_currency}\n"

            else:
                currencies = list(config.CURRENCIES.keys())[:4]
                raw_converted = convert(base=currency_code, amount=amount,
                                        to=currencies)

                converted = {}
                for currency in raw_converted:
                    converted[currency] = round(raw_converted[currency], 2)

                # Формирование ответа (главная валюта первая, а остальные - потом)
                answer = f"{config.CURRENCIES_FLAGS[currency_code]} {add_spaces(converted[currency_code])} {currency_code}\n\n"
                currencies = [i for i in config.CURRENCIES][:4]
                currencies.remove(currency_code)
                for _currency in currencies:
                    answer += f"{config.CURRENCIES_FLAGS[_currency]} {add_spaces(converted[_currency])} {_currency}\n"
            answer = '*' + answer + '*'
            await msg.answer(text=answer, parse_mode='markdown')


async def get_sticker_id_handler(msg: Message):
    await msg.answer_sticker(sticker=msg.sticker.file_id)
    print(msg.sticker.file_id)
