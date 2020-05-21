"""
gui for client
"""
import json
from time import sleep
from socket import socket, AF_INET, SOCK_STREAM
from kivy.resources import resource_add_path, resource_find
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.accordion import Accordion, AccordionItem


resource_add_path("font/")
ft = resource_find('DroidSansFallback.ttf')


# TODO: config
FORMAT = 'utf-8'
HEADER = 64
PORT = 5123
DISCONNECT_MESSAGE = "!DISCONNECTED"

# SERVER = 
SERVER = 
ADDR = (SERVER, PORT)
client: socket


def getUsrInfo():
    usr_info = {
        'username': '2019900086',
        'password': '***'
    }
    json_user_info = json.dumps(usr_info, indent=1)

    return json_user_info


def parseHeader(massage_header):
    massage_header = massage_header.strip(' ')
    massage_header_list = massage_header.split('&')
    massage_length = int(massage_header_list[0])
    massage_format = massage_header_list[1]

    return massage_length, massage_format


def parseMessage(server_message, message_format):
    """

    :param client_message:
    :param message_format:
    :return:
    """
    if message_format == 'JSO':

        # print(server_message)
        # sleep(2)
        info_array = json.loads(server_message, strict=False)

        return info_array

    elif message_format == 'OBJ':
        pass

    elif message_format == 'PLA':
        return server_message

    else:
        return


def makeMessage(msg, fmt):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_format = fmt.encode(FORMAT)
    send_header = send_length + '&'.encode(FORMAT) + send_format
    send_header += b' ' * (HEADER - len(send_header))

    return send_header, message


def receive():
    # TODO: 收到回信
    # 收到的回复头
    recv_header = client.recv(HEADER).decode(FORMAT)
    # 解析回复头
    msg_length, msg_format = parseHeader(recv_header)
    # 等待一段时间，服务器把内容全部发送好
    sleep(2)
    # 得到回复信息
    recv_message = client.recv(msg_length).decode(FORMAT)
    # 解析回复信息
    recv = parseMessage(recv_message, msg_format)
    # 打印回复信息
    # print(recv)

    return recv


def send(msg, fmt):
    send_header, message = makeMessage(msg, fmt)
    # 发送header
    client.send(send_header)
    # 发送信息
    client.send(message)


def linkServer(user_info) -> list:
    global client
    try:
        client = socket(AF_INET, SOCK_STREAM)
        client.connect(ADDR)
    except Exception as e:
        return ['Connect Error!']
    send(user_info, 'JSO')
    login_message = [receive()]
    send(DISCONNECT_MESSAGE, 'STD')

    return login_message


def loadContent() -> dict:
    """

    :return: 内容字典:
        {
            标题 : 内容,...
        }
    """
    global client
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(ADDR)
    send('', 'GET')
    notices_dict = receive()
    # print(notices_dict)

    return notices_dict


class LoginTextInput(TextInput):
    def __init__(self, **kwargs):
        super(LoginTextInput, self).__init__(**kwargs)
        self.multiline = False
        self.use_bubble = True
        self.allow_copy = False


class UserInput(GridLayout):
    def __init__(self, **kwargs):
        super(UserInput, self).__init__(**kwargs)

        self.cols = 2
        self.height = 100

        self.input_username = LoginTextInput()
        self.input_password = LoginTextInput(password=True)

        self.add_widget(Label(text='Username'))
        self.add_widget(self.input_username)
        self.add_widget(Label(text='Password'))
        self.add_widget(self.input_password)


class SubmitButton(Button):
    def __init__(self, **kwargs):
        super(SubmitButton, self).__init__(**kwargs)
        self.text = 'Submit'


class LoginWidget(BoxLayout):

    def __init__(self, **kwargs):
        super(LoginWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.user_input = UserInput(size_hint_y=0.7,
                                    size_hint_x=1,
                                    )
        if __name__ == '__main__':
            self.submit_button = SubmitButton(size_hint_y=0.3,
                                              size_hint_x=0.6,
                                              pos_hint={'x': 0.4},
                                              on_release=self.submit_user_info)

        self.add_widget(self.user_input)
        self.add_widget(self.submit_button)
        self.add_widget(Label(size_hint_y=1))

    def submit_user_info(self, obj):
        # obj.disable = True
        user_name = self.user_input.input_username.text
        password = self.user_input.input_password.text
        # print(f'user_name={user_name}\n'
        #       f'password={password}')
        user_info = {
            'username': user_name,
            'password': password
        }
        json_user_info = json.dumps(user_info, indent=1)

        receive_message_list = linkServer(json_user_info)

        for receive_message in receive_message_list:
            main_app.root.login_window.login_window_widget.logging_box.changeLogTex(
                receive_message
            )
        if receive_message_list[-1] == 'Login Succeed!':
            # 如果登陆成功，进入第二个窗口
            main_app.root.current = 'notices'
            main_app.root.notices_window.notices_window_widget.getContent()
# //////


class LogBox(TextInput):
    def __init__(self, **kwargs):
        super(LogBox, self).__init__(**kwargs)
        self.readonly = True
        self.text_language = ''

    def changeLogTex(self, text):
        self.text += text + '\n'

    def cleanLogTex(self):
        self.text = ''


class LoginWindowWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginWindowWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.btn1 = Button(text='test1',
                           size_hint_y=0.4)
        self.login_widget = LoginWidget(size_hint_x=0.6,
                                        size_hint_y=0.3,
                                        pos_hint={'x': .15})
        self.logging_box = LogBox(
                           size_hint_y=0.3)

        self.add_widget(self.btn1)
        self.add_widget(self.login_widget)
        self.add_widget(self.logging_box)


class LoginWindow(Screen):

    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)

        self.login_window_widget = LoginWindowWidget()
        self.add_widget(self.login_window_widget)
# ================================================================#
"""
mabey put into client.py
"""


class EachNoticeWidget(TextInput):

    def __init__(self, content, **kwargs):
        super(EachNoticeWidget, self).__init__(**kwargs)
        self.font_name = 'font/DroidSansFallback.ttf'
        self.text = content
        self.readonly = True
        self.use_bubble = True

        # self.text = """
        # .. _top:
        # Hello world
        # ===========
        # This is an **emphased text**, some ``interpreted text``.
        # And this is a reference to top_::
        #
        #     $ print("Hello world")
        # """


class NoticesWindowWidget(Accordion):

    def __init__(self, **kwargs):
        super(NoticesWindowWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.font_name = 'font/DroidSansFallback.ttf'

    def getContent(self):

        content_dict = loadContent()       # in module client
        title_no = 0
        for title, content in content_dict.items():
            # print(title, content)
            title_no += 1
            item = AccordionItem(title=f'{title_no}')
            item.add_widget(EachNoticeWidget(content=title + '\n' + content))
            self.add_widget(item)


class NoticesWindow(Screen):

    def __init__(self, **kwargs):
        super(NoticesWindow, self).__init__(**kwargs)

        self.notices_window_widget = NoticesWindowWidget()
        self.add_widget(self.notices_window_widget)

# ================================================================#


class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.login_window = LoginWindow(name='login')
        self.notices_window = NoticesWindow(name='notices')

        self.add_widget(self.login_window)
        self.add_widget(self.notices_window)

        self.current = 'login'


class MainApp(App):

    def build(self):
        window_manager = WindowManager()

        return window_manager


if __name__ == '__main__':
    main_app = MainApp()
    main_app.run()
