from handlers.init import *


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
