import datetime

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.list import IRightBodyTouch, ThreeLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivy.storage.jsonstore import JsonStore

list_helper = """
<ListItemWithCheckbox>:
    IconLeftWidget:
        icon: root.icon

    RightCheckbox:
        listItem: root
        on_active: app.on_active(*args)
        
    
MDBoxLayout:
    orientation: "vertical"
        
    MDToolbar:
        title: "ToDoList"
        right_action_items: [["delete-outline", lambda x: app.delete_case(x), "Удалить"]]
    
    Screen:
        ScrollView:
            MDList:
                id: container
                     
"""


class ListItemWithCheckbox(ThreeLineAvatarIconListItem):
    '''Custom list item.'''
    icon = StringProperty("alert-circle")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    pass


class ToDoApp(MDApp):
    def __init__(self, **kwargs):
        """Тут все основные элементы"""
        super().__init__(**kwargs)
        self.add_button = MDIconButton(icon='plus-circle')
        self.text_input_button = MDIconButton(icon='plus-circle')

        self.text_input_button.bind(on_press=self.save_cases)
        self.add_button.bind(on_press=self.button_to_ti)

        self.case_theme = MDTextField(hint_text="Тема: необязательно")
        self.create_new_text_field = MDTextField(hint_text="Основная задача", multiline=True)

        self.finite_number = 1  # число в конце заголовка "Без темы"

        self.checked_case_list = []

        self.checked_case_name = ''

        self.store = JsonStore("all_cases.json")  # Для хранения данных

    def save_cases(self, instance):
        """Сохраняет задачи в Json и добаляет их на экран"""
        """
        Сохраняем полученные данные и отправляем их в json файл, сортирую по тому есть ли тема или нет
        После добавляем case на экран
        и заменяем виджеты
        """
        if len(self.create_new_text_field.text) > 0:
            if len(self.case_theme.text) > 0:
                self.store.put(self.case_theme.text,
                               theme=self.case_theme.text,
                               case_body=self.create_new_text_field.text,
                               time_of_creation=str(datetime.datetime.now().strftime('%Y.%m.%d, '
                                                                                     '%H:%M:%S'))
                               )
                case = ListItemWithCheckbox(text=self.case_theme.text,
                                            secondary_text=self.create_new_text_field.text,
                                            tertiary_text=str(datetime.datetime.now().strftime('%Y.%m.%d, '
                                                                                               '%H:%M:%S')))
                self.root.ids.container.add_widget(case)
            else:
                self.store.put('without_theme ' + str(self.finite_number),
                               theme="Без темы " + str(self.finite_number),
                               case_body=self.create_new_text_field.text,
                               time_of_creation=str(datetime.datetime.now().strftime('%Y.%m.%d, '
                                                                                     '%H:%M:%S'))
                               )
                case = ListItemWithCheckbox(text="Без темы " + str(self.finite_number),
                                            secondary_text=self.create_new_text_field.text,
                                            tertiary_text=str(datetime.datetime.now().strftime('%Y.%m.%d, '
                                                                                               '%H:%M:%S')))
                self.root.ids.container.add_widget(case)
                self.finite_number += 1

        self.create_new_text_field.text = ''
        self.case_theme.text = ''

        self.root.ids.container.remove_widget(self.text_input_button)
        self.root.ids.container.remove_widget(self.case_theme)
        self.root.ids.container.remove_widget(self.create_new_text_field)

        self.root.ids.container.add_widget(self.add_button)

    def load_cases(self):
        """Выгружает задачи на экран"""
        """Цикл сортирует объекты из json, далее мы присваеваем их к case"""
        for key, value in dict(self.store).items():
            theme = value['theme']
            body = value["case_body"]
            time_of_creation = value["time_of_creation"]
            case = ListItemWithCheckbox(text=theme,
                                        secondary_text=body,
                                        tertiary_text=time_of_creation)
            self.root.ids.container.add_widget(case)

        self.root.ids.container.add_widget(self.add_button)

    def build(self):
        screen = Builder.load_string(list_helper)
        return screen

    def button_to_ti(self, instance):
        """замена кнопок на ti-TextInput"""
        self.root.ids.container.remove_widget(self.add_button)

        self.root.ids.container.add_widget(self.case_theme)
        self.root.ids.container.add_widget(self.create_new_text_field)
        self.root.ids.container.add_widget(self.text_input_button)

    def on_active(self, rcb, value):
        if value:
            self.checked_case_name = rcb.listItem.text
            self.checked_case_list.append(rcb.listItem.text)
        else:
            self.checked_case_list.remove(rcb.listItem.text)

    def delete_case(self, button):
        """Удаление case`ов"""
        if len(self.checked_case_list) >= 1:
            for key, value_ in dict(self.store).items():
                if value_['theme'] in self.checked_case_list:
                    for cases in self.checked_case_list:
                        if key != str(cases):
                            self.store.delete(key)
                        else:
                            self.store.delete(cases)
                        self.root.ids.container.clear_widgets()
                        self.load_cases()
                        break
        else:
            Snackbar(text="Вы не выбрали, что хотите удалить").open()

    def on_start(self):
        """Добавление на основной экран всех элементов"""
        return self.load_cases()


if __name__ == '__main__':
    ToDoApp().run()
