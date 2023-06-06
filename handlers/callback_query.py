from handlers.init import *
from aiogram.types import (CallbackQuery, InlineQuery, Message, InputTextMessageContent,
                           InlineQueryResultArticle, InlineQueryResultCachedPhoto, InputMediaAudio)


async def cancel_handler(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.finish()
    if cq.message.text:
        first_line = cq.message.text.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_text(text=answer)
    else:
        first_line = cq.message.caption.split('\n')[0]
        answer = '{}\n\n❌ Действие отменено'.format(first_line)
        await cq.message.edit_caption(caption=answer)


@dp.inline_handler()
async def inline_encryption_messages_handler(msg: InlineQuery, state: FSMContext):
    if msg.query:
        answer = InputTextMessageContent(f'Насвай')

        item = InlineQueryResultArticle(
            id='1',
            title=f'⏩ Отправить курс',
            input_message_content=answer
        )
        currency_regex = r'(\d+(?:\.\d+)?(?:к|k|тыс)?)(?:\s*([^\d\s]+))?'

        matches = re.findall(currency_regex, msg.query.lower())

        try:
            answer = InputTextMessageContent(calculator(msg.query))
            item = InlineQueryResultArticle(
                id='1',
                title=f'⏩ Отправить результат выражения',
                input_message_content=answer
            )
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

                answer = InputTextMessageContent(answer, parse_mode='markdown')
                item = InlineQueryResultArticle(
                    id='1',
                    title=f'⏩ Отправить курс',
                    input_message_content=answer
                )
    else:
        item = InlineQueryResultArticle(
            id='1',
            title=f'❗ Укажи сумму и валюту',
            input_message_content=InputTextMessageContent(f'❗ Сумма и валюта не указаны')
        )

    await msg.answer(results=[item], cache_time=0)
