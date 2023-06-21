# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import datetime
from config import comunity_token, acces_token
from core import VkTools
from data_store import engine, add_user, user_check_in_db


class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = None
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )

    def get_data(self, event):
        if self.params['name'] is None:
            self.message_send(event.user_id, 'Введите имя и фамилию:')
            return event.text

        elif self.params['sex'] is None:
            self.message_send(event.user_id, 'Введите пол (1-м, 2-ж):')
            return int(event.text)

        elif self.params['city'] is None:
            self.message_send(event.user_id, 'Введите город, в котором проживаете:')
            return event.text

        elif self.params['year'] is None:
            self.message_send(event.user_id, 'Введите дату рождения в формате (дд.мм.гггг):')
            return datetime.now().year - int(event.text.split('.')[2])

    def event_handler(self):

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет' or command == 'Привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'здравствуй {self.params["name"]}')

                    for i in self.params:
                        if self.params[i] is None:
                            self.params[i] = self.get_data(event)

                    self.message_send(event.user_id, 'Успешная регистрация!')

                elif command == 'поиск' or command == 'найти':
                    people = []
                    while True:
                        if people:
                            user = people.pop()
                            # здесь логика дял проверки и добавления в бд
                            if user_check_in_db(engine, event.user_id, user['id']) is False:
                                add_user(engine, event.user_id, user['id'])
                                break
                        else:
                            people = self.api.serch_users(self.params, self.offset)

                    photos_user = self.api.get_photos(user['id'])
                    self.offset += 10

                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                        if num == 2:
                            break
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]} ссылка на страницу: vk.com/id{user["id"]}',
                                      attachment=attachment
                                      ) 

                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'команда не опознана')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()

            

