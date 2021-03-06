import json
from vk_api.keyboard import VkKeyboard


def get_button(text, color=None):
    return {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"" + "1" + "\"}",
                    "label": f"{text}"
                },
                "color": f"{color}"
            }


def do_keyboard(kb):
    kb = json.dumps(kb, ensure_ascii=False).encode('utf-8')
    kb = str(kb.decode('utf-8'))
    return kb


menu_keyboard = {
    "one_time": False,
    "buttons": [
        [get_button('Показать вопросы', 'primary')]
    ]
}

menu_keyboard = do_keyboard(menu_keyboard)


def inline_keyboard(index):

    add_line = False

    if index == 0:
        return None

    elif index >= 5:
        add_line = True

    kb = VkKeyboard(inline=True)

    for i in range(1, index + 1):
        if add_line and i % 5 == 0:
            kb.add_line()
        kb.add_button(f'{i}')

    return kb
