'''
说明文档：telegram机器人相关测试：
    re_get_number(query_data)------------->获取data数据中的数字格式--返回list类型[numbers, delete_id]
        numbers：返回第一个数字--只存在第一个数字返回第一个数字值和None
        delete_id : 返回第二个数字--若没有第一个数字则返回None

    re_get_setting_url(query_data)------------->调用url按钮设置的时候进行修改-返回list类型[name_url_dict_list]
        按 | 分按钮格子 按 & 区分按钮名字和url链接 按换行区分url生成在一行还是多行
        对用户输入进行正则规则匹配，只会按着规则产生list列表，而后通过方法check_url_setting来判断url的输入是否正确。

    check_url_setting(name_url_dict_list)------------->调用list规则检查，返回flag值
        name_url_dict_list：列表型，内容为字典，一个字典代表一行url生成
        对用户输入的规则进行正则修改成list列表后对数据进行检查，如果没有按照规则生成，便会跳出判断循环，输出flag=0，判断为0即说明输入错误
        错误原因：输入规则不符合要求或url请求失败，url的请求状态非200成功接收的话，一律按无效连接，使得url按钮生成失效

    id_insert(tables, upuser_user, user_id_data)-------------->将用户数据存储到后端数据库中（user2数据库）
        tables: 要存到的数据库名
        upuser_user： 当前用户的所有数据信息
        uer_id_data: 要存的用户数据库的id列表型list
        如果用户表中本来没有数据：第一次时候start的人便会存到第一个位置，成为管理员。可以对图文默认样式进行修改，更快更方便
        而后使用/start方法的人会跟数据库中的id列进行比对，如果其id没有在其中，则会存入他的数据，否则不存入

    get_id_chat(tables)-------------->获取用户id表
        tables: 要搜的数据库名
        对其的id_chat唯一id进行遍历获取，生成list型的id表

    get_sign_statute(id_re, tables)----------------->判断该用户是否有修改权限并返回具体的权限代号
        id_re: 获取当前用户的id
        tables：要判断的库名
        获取当前用户的id，判断其现在拥有的权限为多少，并将该值返回出来确认为是哪种权限

    get_message_text(tables, id_message, change_row)--------------------->获取message库下指定id的文本信息
        tables: 数据库表名
        id_message：对应信息库中的id行，获取该行的数据
        change_row： 要获取该行数据的哪一列，列名
        结果为返回该位置的值：（若该位置无值）则返回None

    get_data(row)----------------->对用户的点击指令来修改获得的样式效果：
        row：获取后台中用户点击了哪一个按钮，如果没有点击，默认传入参数1
        即用户点击哪个图文表时：进行展开的前端展示

    sign_mark_change(id_re, sign_re)---------------->对id_re的权限进行修改，修改为传入的sign_re
        id_re:获取当前用户的id
        sign_re：要修改成的权限类型
        通过用户点击效果，对用户的权限进行修改，当用户点击了哪个按钮对其进行判断，是否要赋予权限，要的话直接对其进行修改权限

    change_message_text(id_re, tables, text_re, id_message)-------------------->修改文本信息
        id_re:获取当前用户id——判断是否有权限
        tables：要修改的信息表名
        text_re: 要修改成的文本名
        id_message:要修改的信息表中哪条信息的文本
        当用户点击了编辑按钮，输入的是文本就会调用该方法，会开始接收用户实时输入的文本进行数据库替换

    change_message_Graphic(id_re, tables, text_re, id_message)-------------------->修改图像类信息
        id_re:获取当前用户id——判断是否有权限
        tables：要修改的信息表名
        text_re: 要修改成的图像的file_id名
        id_message:要修改的信息表中哪条信息的文本
        当用户点击了编辑按钮，输入的是图像类内容就会调用该方法，开始接收用户输入的图像并将数据存到数据库中进行替换

    change_message_button_text(id_re, tables, text_re, id_message)-------------------->修改url类信息
        id_re:获取当前用户id——判断是否有权限
        tables：要修改的信息表名
        text_re: 要修改成的按钮设置规则文本-将其二次获取后在展示的时候更改修改效果展示出来
        id_message:要修改的信息表中哪条信息的文本
        当用户点击了设置按钮-url的按钮，就会调用该功能，按规则输入后会使按钮生成成功，否则会要求用户重新输入。

    call_back_message_re(id_message)---------------->将点击的图文表取消修改--恢复为默认形式
        id_message:要修改的信息表中的哪一行的id值
        当用户点击了恢复默认的时候，便会调用该方法，使得信息样式恢复为最初管理员设置的相同

    message_id_insert(tables)---------->添加新的图文表格
        tables：要添加的表名
        当用户点击添加后，在后台数据库便会加入一个同默认设置相同的配置的行数据

    message_id_delete(tables, message_id)------------>删除图文表
        tables：要修改的表名
        message_id：信息库中的id名
        当用户点击了该按钮的删除按钮，便会调用该方法，执行删除，按钮便会消失

'''

import re
import pymysql
import logging
import time
import urllib
import hashlib
from mysql_data import password, mydabases
from telegram import __version__ as TG_VER
import pickle
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)


# 正则匹配数字
def re_get_number(query_data):
    data = []
    numbers = re.search(r'-?[0-9]+.*', query_data, re.S)
    delete_id = None
    # 获取的数据正则匹配
    if numbers is not None:
        if 'id' in numbers.group():
            numbers_re = int(re.search(r'-?[0-9]+', numbers.group(), re.S).group())
            delete_id = int(re.search(r'(?<={}_).*\d'.format(numbers_re), numbers.group(), re.S).group())
            numbers = numbers_re
        else:
            numbers = int(numbers.group())
    else:
        numbers = -1
    data.append(numbers)
    data.append(delete_id)
    return data


# 正则匹配name和url
def re_get_setting_url(query_data):
    # 第一步 哪几个按钮同行：
    setting_rows_list = re.findall(r'[^\n]*', query_data, re.S)[::2]
    # 第二步 确认按钮的顺序
    name_url_dict_list = []
    for setting_rows in setting_rows_list:
        name_url_list = re.findall(r'[^|]*', setting_rows, re.S)[::2]
        # 第三步 确认名字和url
        name_url_dict = {}
        for name_url in name_url_list:
            name = re.findall(r'[^&]*', name_url, re.S)[::2][0].replace(" ", '')
            url = re.findall(r'[^&]*', name_url, re.S)[::2][1].replace(" ", '')
            name_url_dict[name] = url
        name_url_dict_list.append(name_url_dict)
    return name_url_dict_list


# 判断name和url是否正确
def check_url_setting(name_url_dict_list):
    flag = 1
    for name_url_dict in name_url_dict_list:
        for key in name_url_dict.keys():
            if key == '':
                flag = 0
                print("输入的数据有误！请重新输入.")
                break
            else:
                if '@' in name_url_dict[key]:
                    name_url_dict[key] = "https://t.me/"+name_url_dict[key][1:]
                try:
                    if len(re.search(r'(http)?', name_url_dict[key], re.S).group()) == 0:
                        status1 = urllib.request.urlopen('https://'+name_url_dict[key],timeout=10).status
                        status2 = urllib.request.urlopen('http://'+name_url_dict[key],timeout=10).status
                    else:
                        status1 = urllib.request.urlopen(name_url_dict[key],timeout=10).status
                        status2 = 404
                    if status1 or status2 == 200:
                        print(True)
                    else:
                        flag = 0
                        print("输入的链接有误无法访问！，请重新输入")
                        break
                except Exception:
                    print(name_url_dict[key])
                    flag = 0
                    break

    return flag


# 添加用户
def id_insert(tables, upuser_user, user_id_data):
    '''加入用户id，进行记录保存，当用户使用/start指令的时候就会调用该方法将用户的id，名字，@型姓名存入数据库'''
    # 获取当前的用户id表 转存为ret元组表
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    # if 当前表为空，没有用户时，默认开始存入数据
    if len(user_id_data) == 0:
        cursor = conn.cursor()
        sql = "INSERT INTO {}(name_id, id_chat, name,sign) VALUES (%s, %s, %s, 0);".format(tables)
        print(sql, 'id_insert')
        id_chat = upuser_user.id
        name_id = upuser_user.username
        name = upuser_user.first_name
        # 执行SQL语句
        cursor.execute(sql, [name_id, id_chat, name])
        # 提交事务
        conn.commit()
        cursor.close()
    # 若用户表非空，即对当前访问用户的id进行表格检查是否在id表中，如果不在，则进入读取
    else:
        if str(upuser_user.id) not in user_id_data:
            cursor = conn.cursor()
            sql = "INSERT INTO {}(name_id, id_chat, name,sign) VALUES (%s, %s, %s, 0);".format(tables)
            id_chat = upuser_user.id
            name_id = upuser_user.username
            name = upuser_user.first_name
            # 执行SQL语句
            cursor.execute(sql, [name_id, id_chat, name])
            # 提交事务
            conn.commit()
            cursor.close()
        else:
            pass
    conn.close()


# 获取用户id
def get_id_chat(tables):
    '''获取数据库中的用户id表并返回list型的id表'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT id_chat from {};".format(tables))
    ret = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    user_id_data = []
    for id_chat_re in ret:
        user_id_data.append(id_chat_re[0])
    return user_id_data


# 获取当前用户是否拥有编辑权限
def get_sign_statute(id_re, tables):
    '''获取数据库中的用户id表并返回list型的id表'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT sign from {} where id_chat={};".format(tables, id_re))
    ret_sign = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return ret_sign


# 获取message库下指定id的文本信息
def get_message_text(tables, id_message, change_row):
    '''获取文本数据库中的文本信息并返回指定id的list型的文本信息表'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT {} from {} WHERE id={};".format(change_row, tables, id_message)
    cursor.execute(sql)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    return ret[0][0]


# 制作图文添加的显示格式
def get_data(row):
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT id from {};".format('message')
    print(sql,'-164')
    cursor.execute(sql)
    ret = cursor.fetchall()
    cursor.close()
    conn.close()
    message_text_data = []
    for text_re in ret:
        message_text_data.append(text_re[0])
    # 制作格式
    page_data = []
    size = 5
    starts = 0
    pages = []
    setting = []
    page = 1
    for i in range(len(message_text_data[1::])):
        starts += 1
        if starts <= size:
            if int(row) == i+1:
                pages.append(InlineKeyboardButton(text="id:{}✔".format(message_text_data[i+1]),
                                                  callback_data='page_picture_text_{}'.format(i+1)))
                setting.append(InlineKeyboardButton('发送欢迎语句(发给数据库中所有用户)', callback_data='send_message_{}'.format(message_text_data[row])))
                setting.append(InlineKeyboardButton('自定义编辑欢迎内容', callback_data='edit_message_{}'.format(message_text_data[row])))
                setting.append(InlineKeyboardButton('按钮设置--配置url链接', callback_data='edit_url_{}'.format(message_text_data[row])))
                setting.append(InlineKeyboardButton('删除按钮', callback_data='page_picture_text_{}_{}id'.format(row, message_text_data[row])))
            else:
                pages.append(InlineKeyboardButton(text="id:{}".format(message_text_data[i+1]), callback_data='page_picture_text_{}'.format(i+1)))
        if starts == size:
            page_data.append(pages)
            if page - 1 < int(row) / size <= page:
                page_data.append(setting)
            page += 1
            starts = 0
            pages = []
    if pages != None:
        page_data.append(pages)
        if page - 1 < int(row) / size <= page:
            page_data.append(setting)
    else:
        print(False)

    return page_data


# 改变用户的编辑权限（1->有权限,0->没有权限）
def sign_mark_change(id_re, sign_re):
    '''用户是否拥有修改权限判定'''
    # 进行sign修改，存入即时数据
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "UPDATE USER2 SET sign=%s WHERE id_chat=%s;"
    try:
        # 执行SQL语句
        cursor.execute(sql, [sign_re, id_re])
        # 提交事务
        conn.commit()
    except Exception as e:
        # 有异常，回滚事务
        conn.rollback()
    cursor.close()
    conn.close()


# 修改信息库下的指定id的文本信息
def change_message_text(id_re, tables, text_re, id_message):
    '''判断是否拥有修改权限，拥有后赋予修改效果--用户发的信息实时记录更新为欢迎语句直到用户失去权限'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT sign from USER2 WHERE id_chat={};".format(id_re)
    cursor.execute(sql)
    sign = cursor.fetchone()[0]
    # UPDATE message SET text='welcome to use bot' WHERE id=1;
    conn.commit()
    if sign != '0':
        text = text_re
        sql = "UPDATE {} SET text='{}' WHERE id={};".format(tables, text, id_message)
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    else:
        print("failed--text")
    conn.close()


# 修改信息库下指定id的图文信息
def change_message_Graphic(id_re, tables, text_re, id_message):
    '''判断是否拥有修改权限，拥有后赋予修改效果--用户发的信息实时记录更新为欢迎语句直到用户失去权限'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT sign from USER2 WHERE id_chat={};".format(id_re)
    # print(sql, '-213')
    cursor.execute(sql)
    sign = cursor.fetchone()[0]
    # UPDATE message SET text='welcome to use bot' WHERE id=1;
    conn.commit()
    if sign != '0':
        text = text_re
        sql = "UPDATE {} SET Graphic_id='{}' WHERE id={};".format(tables, text, id_message)
        # sql = "UPDATE %s SET photo_id=%s WHERE id=%s;"
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    else:
        print("failed--Graphic")
    conn.close()


# 修改信息库下的指定id的文本信息
def change_message_button_text(id_re, tables, text_re, id_message):
    '''判断是否拥有修改权限，拥有后赋予修改效果--用户发的信息实时记录更新为欢迎语句直到用户失去权限
        id_re : 用户id名--确认是不是用户表中的第一位人员：才是管理员
        tables： 修改的数据表
        text_re: 更新的数据
        id_message: 表中的名'''
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT sign from USER2 WHERE id_chat={};".format(id_re)
    cursor.execute(sql)
    sign = cursor.fetchone()[0]
    # UPDATE message SET text='welcome to use bot' WHERE id=1;
    conn.commit()
    if sign != '0':
        text = text_re
        sql = 'UPDATE {} SET button_text="{}" WHERE id={};'.format(tables, text, id_message)
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    else:
        print("failed--change_message")
    conn.close()


# 恢复message库下指定id的文本信息为默认值
def call_back_message_re(id_message):
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    # 获取指定最初id下的文本信息-即默认信息
    cursor.execute("SELECT text from message WHERE id=1;")
    text = cursor.fetchone()
    cursor.execute("SELECT Graphic_id from message WHERE id=1;")
    photo = cursor.fetchone()
    # 从元组中取出，重命名为message_re,photo_re
    message_re = text[0]
    photo_re = photo[0]
    # 更新修改后的数据，将其恢复为默认信息
    sql = "UPDATE message SET text=%s WHERE id=%s;"
    cursor.execute(sql, [message_re, id_message])
    sql = "UPDATE message SET Graphic_id=%s WHERE id=%s;"
    cursor.execute(sql, [photo_re, id_message])
    # 提交事务记录
    conn.commit()
    cursor.close()
    conn.close()


# 添加新的图文表格---message中的行增加，初始值均为默认
def message_id_insert(tables):
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "INSERT INTO {}(text,Graphic_id) VALUES (%s, %s);".format(tables)
    # 填入默认文本
    text = get_message_text('message', 1, 'text')
    # 填入默认照片
    graphic_id = get_message_text('message', 1, 'Graphic_id')
    # 执行SQL语句
    cursor.execute(sql, [text, graphic_id])
    # 提交事务
    conn.commit()
    cursor.close()
    conn.close()


# 删除指定的图文表格---message中的指定行删除
def message_id_delete(tables, message_id):
    conn = pymysql.connect(host='localhost', user='root', password=password, database=mydabases[0], charset='utf8')
    cursor = conn.cursor()
    sql = "delete from {} where id = {};".format(tables, message_id)
    print(sql)
    # 执行SQL语句
    cursor.execute(sql)
    # 提交事务
    conn.commit()
    cursor.close()
    conn.close()


# 指令执行--当输入指令时才会调用该方法，展示基本信息
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''执行/start命令后机器人弹出的导航界面'''
    # 获取当前用户的数据
    upuser_user = update.effective_user
    print(upuser_user.id, '--start')
    # 获取当前用户表中所有id
    data_list = get_id_chat('USER2')
    # 执行是否加入id的方法
    print(data_list)
    id_insert('user2', upuser_user, data_list)
    # 增加按钮功能
    new_data_list = get_id_chat('user2')
    print(new_data_list)
    if upuser_user.id != int(new_data_list[0]):
        keyboard = [
            [InlineKeyboardButton('发送欢迎语句(仅自己可见)', callback_data='hello_message')]
        ]
        await context.bot.sendMessage(chat_id=upuser_user.id, text='欢迎加入数据库',
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [
            [InlineKeyboardButton('发送欢迎语句(仅自己可见)', callback_data='hello_message'), InlineKeyboardButton('自定义编辑欢迎内容', callback_data='edit_message_1')],
            [InlineKeyboardButton('图文', callback_data='page_picture_text')]
        ]
        # 发送的信息
        await context.bot.sendMessage(chat_id=upuser_user.id, text='欢迎使用机器人,管理员',
                                      reply_markup=InlineKeyboardMarkup(keyboard))


# /start后的发送信息的发送效果
async def hello_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''点击发送欢迎语句时返回调用hello_message方法管理员为一号id用户可以选择是否发送给其他用户'''
    # 获取当前用户的数据
    upuser_user = update.effective_user
    # 按钮加载
    query = update.callback_query
    print(query, '-->313')
    await query.answer()
    # 获取id表
    data_list = get_id_chat('USER2')
    text = get_message_text('message', 1, 'text')

    # 给表中所有用户发送指定id型的广告欢迎信息
    # for data in data_list:
    await context.bot.sendMessage(chat_id=upuser_user.id, text=text)


# 图文表中的发送信息
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''发送信息给用户表中的所有用户'''
    # 按钮加载
    query = update.callback_query
    data = re_get_number(query.data)
    id_send = data[0]
    print(id_send, "发送的id_send")
    await query.answer()
    # 获取id表
    data_list = get_id_chat('USER2')
    change_row = ['text', 'Graphic_id', 'button_text']
    text = get_message_text('message', id_send, change_row[0])
    graphic_id = get_message_text('message', id_send, change_row[1])
    button_text = []
    if get_message_text('message', id_send, change_row[2]) is not None:
        if len(get_message_text('message', id_send, change_row[2])) != 0:
            name_url_dict_list = re_get_setting_url(get_message_text('message', id_send, change_row[2]))
            print(name_url_dict_list)
            for name_url_dict in name_url_dict_list:
                name_url_dict_text = []
                for key in name_url_dict.keys():
                    if "@" in name_url_dict[key]:
                        name_url_dict[key] = "https://t.me/" + name_url_dict[key][1:]
                    name_url_dict_text.append(InlineKeyboardButton('{}'.format(key), url='{}'.format(name_url_dict[key])))
                button_text.append(name_url_dict_text)

    # 给表中所有用户发送指定id型的广告欢迎信息
    for data in data_list:
        if int(graphic_id[-1]) == 1:
            await context.bot.sendPhoto(chat_id=int(data), photo=graphic_id[:-1], caption=text,
                                        reply_markup=InlineKeyboardMarkup(button_text))
        elif int(graphic_id[-1]) == 2:
            await context.bot.sendVideo(chat_id=int(data), video=graphic_id[:-1], caption=text,
                                        reply_markup=InlineKeyboardMarkup(button_text))
        elif int(graphic_id[-1]) == 3:
            await context.bot.sendAnimation(chat_id=int(data), Animation=graphic_id[:-1], caption=text,
                                            reply_markup=InlineKeyboardMarkup(button_text))
        else:
            await context.bot.sendMessage(chat_id=int(data), text=text, reply_markup=InlineKeyboardMarkup(button_text))


# 编辑图文信息--（包括/start中的和图文表中的所有信息）
async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''编辑要发送的欢迎信息-step1----'''
    # 获取用户数据
    query = update.callback_query
    upuser_user = update.effective_user
    # data = get_id_chat
    # 获取当前权限状态
    sign_statute = get_sign_statute(upuser_user.id, 'USER2')
    # 获取修改权限后开始进行判断是哪种权限
    if sign_statute != '0':  # 拥有修改权时
        # 纯数字--是修改图文权限
        if str(sign_statute).isdigit():
            # 数字1是修改默认样式
            if sign_statute == "1":
                keyboard = [
                    [InlineKeyboardButton('确认', callback_data='change_message_.{}'.format(int(sign_statute)))],
                ]
            # 否则是修改图文表中的样式
            else:
                keyboard = [
                        [InlineKeyboardButton('确认', callback_data='change_message_.{}'.format(int(sign_statute)))],
                        [InlineKeyboardButton('恢复默认', callback_data='callback_message_{}'.format(int(sign_statute)))]
                    ]
            await context.bot.sendMessage(chat_id=upuser_user.id, text='当前样式为：')
            # 有权限开始实时捕获相关信息
            text_get = update.message.text
            photo_get = update.message.photo
            video_get = update.message.video
            animation_get = update.message.animation
            # 判断文字是否修改
            if text_get is not None:
                change_message_text(upuser_user.id, 'message', text_get, int(sign_statute))
                graphic_id = get_message_text('message', sign_statute, 'Graphic_id')

                # 发送类型
                text = get_message_text('message', int(sign_statute), 'text')
                if int(graphic_id[-1]) == 1:
                    await context.bot.sendPhoto(chat_id=upuser_user.id, photo=graphic_id[:-1], caption=text,
                                                reply_markup=InlineKeyboardMarkup(keyboard))
                elif int(graphic_id[-1]) == 2:
                    await context.bot.sendVideo(chat_id=upuser_user.id, video=graphic_id[:-1], caption=text,
                                                reply_markup=InlineKeyboardMarkup(keyboard))
                elif int(graphic_id[-1]) == 3:
                    await context.bot.sendAnimation(chat_id=upuser_user.id, Animation=graphic_id[:-1], caption=text,
                                                    reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    await context.bot.sendMessage(chat_id=upuser_user.id, text=text,
                                                  reply_markup=InlineKeyboardMarkup(keyboard))
            text = get_message_text('message', int(sign_statute), 'text')
            # 判断图片是否修改--（图片，视频，GIF中取一个）
            if len(photo_get) != 0:
                print(True, 'photo_get', 'edit_message--photo_get')
                photo_get_id = photo_get[0].file_id
                change_message_Graphic(upuser_user.id, 'message', photo_get_id+'1', int(sign_statute))
                # 获取当前修改后的图信息（图片）
                photo_get_id = get_message_text('message', int(sign_statute), 'Graphic_id')[:-1]
                await context.bot.sendPhoto(chat_id=upuser_user.id, photo=photo_get_id, caption='{}'.format(text),
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            elif video_get is not None:
                video_get_id = video_get.file_id
                change_message_Graphic(upuser_user.id, 'message', video_get_id+'2', int(sign_statute))
                # 获取当前修改后的图信息（视频）
                video_get_id = get_message_text('message', int(sign_statute), 'Graphic_id')[:-1]
                await context.bot.sendVideo(chat_id=upuser_user.id, video=video_get_id, caption='{}'.format(text),
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            elif animation_get is not None:
                animation_get_id = animation_get.file_id
                change_message_Graphic(upuser_user.id, 'message', animation_get_id+'3', int(sign_statute))
                # 获取当前修改后的图信息（GIF）
                animation_get_id = get_message_text('message', int(sign_statute), 'Graphic_id')[:-1]
                await context.bot.sendAnimation(chat_id=upuser_user.id, animation=animation_get_id,
                                                caption='{}'.format(text), reply_markup=InlineKeyboardMarkup(keyboard))

        # 非纯数字是url设置
        else:  # 不是纯数字-是url存储
            sign_statute = sign_statute[0:-3]
            text_get = update.message.text
            if text_get is not None:  # 不为空时生成按钮
                if check_url_setting(re_get_setting_url(text_get)) == 1:  # 按钮规则成立
                    change_message_button_text(upuser_user.id, 'message', text_get, int(sign_statute))
                    await context.bot.sendMessage(chat_id=upuser_user.id, text='保存成功！')
                    # 成功后取消修改权限
                    sign_mark_change(upuser_user.id, 0)
                else:
                    await context.bot.sendMessage(chat_id=upuser_user.id, text='输入格式有问题！')

    else:  # 否则因为点击了赋予修改权限
        if query is None:
            pass
        else:
            # 获取数据
            data_edit_message = re_get_number(query.data)
            # 赋予用户修改欢迎信息权限
            sign_mark_change(upuser_user.id, data_edit_message[0])
            # 获取当前权限
            sign_statute = get_sign_statute(upuser_user.id, 'USER2')
            if sign_statute == "1":
                keyboard = [
                    [InlineKeyboardButton('确认', callback_data='change_message_{}'.format(int(sign_statute)))],
                ]
                text1 = '默认'
                text2 = '(即添加后的默认图文)'
            else:
                keyboard = [
                    [InlineKeyboardButton('确认', callback_data='change_message_{}'.format(int(sign_statute)))],
                    [InlineKeyboardButton('恢复默认', callback_data='callback_message_{}'.format(int(sign_statute)))]
                ]
                text1 = ''
                text2 = ''
            text = get_message_text('message', int(data_edit_message[0]), 'text')
            graphic_id = get_message_text('message', int(data_edit_message[0]), 'Graphic_id')

            await context.bot.sendMessage(chat_id=upuser_user.id,
                                          text='开始修改{}图文形态{}\n当前样式为：'.format(text1, text2))
            if int(graphic_id[-1]) == 1:
                await context.bot.sendPhoto(chat_id=upuser_user.id, photo=graphic_id[:-1], caption=text,
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            elif int(graphic_id[-1]) == 2:
                await context.bot.sendVideo(chat_id=upuser_user.id, video=graphic_id[:-1], caption=text,
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            elif int(graphic_id[-1]) == 3:
                await context.bot.sendAnimation(chat_id=upuser_user.id, Animation=graphic_id[:-1], caption=text,
                                                reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.sendMessage(chat_id=upuser_user.id, text=text,
                                              reply_markup=InlineKeyboardMarkup(keyboard))


# 按钮设置，出现链接url，点击图文页面可以进行跳转
async def edit_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 获取用户数据
    query = update.callback_query
    # upuser_user = update.effective_user
    data = get_id_chat('USER2')
    # 获取当前权限状态
    sign_statute = get_sign_statute(data[0], 'USER2')
    print(sign_statute, '有值')
    # 点击设置按钮后赋予权限
    data_edit_url = re_get_number(query.data)  # --获取到其在message中的id
    # 赋予权限
    sign_mark_change(data[0], str(data_edit_url[0])+'url')
    # 获取当前权限状态
    sign_statute = get_sign_statute(data[0], 'USER2')
    await context.bot.sendMessage(chat_id=data[0], text='请输入按钮配置\n格式:\n按钮名称&url (同行按钮用|隔开，下一行按钮请换行输入）\n例：\n'
                                                               '按钮1&https://t.me/... | 按钮2&https://t.me/...\n'
                                                               '按钮3&https://t.me/... | 按钮4&https://t.me/... '
                                                               '| 按钮5&https://t.me/')


# 图文表的添加删除的形态生成--即制作展示图文表总样式s
async def page_picture_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''添加格式图文状态'''
    # 按钮加载
    query = update.callback_query
    await query.answer()
    # 获取表格样式
    data = re_get_number(query.data)
    print(data)
    numbers = data[0]
    delete_id = data[1]
    # 插入数据
    if numbers == -2:
        message_id_insert('message')

    # 删除数据
    if delete_id is not None:
        message_id_delete('message', int(delete_id))
        numbers = -1
    page_data = get_data(data[0])
    # upuser_user = update.effective_user
    page_data.append([InlineKeyboardButton('添加图文', callback_data="page_picture_text_-2")])
    await query.edit_message_text(text='图文选择', reply_markup=InlineKeyboardMarkup(page_data))
    # await query.edit_message_caption(caption='图文选择', reply_markup=InlineKeyboardMarkup(page_data))


# 点击修改图文表的确认修改后返回修改完成--首页无按钮，图文表中可以点击返回回到图文表
async def change_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''确认修改后取消修改权，固定下欢迎语句信息'''
    # 按钮加载
    query = update.callback_query
    await query.answer()
    # 获取用户数据
    upuser_user = update.effective_user
    number_change_message = re_get_number(query.data)

    # 修改用户权限，取消用户修改权
    sign_mark_change(upuser_user.id, 0)
    keyboard = [
        [InlineKeyboardButton('返回', callback_data='page_picture_text')]
    ]
    if int(number_change_message[0]) == 1:
        await context.bot.sendMessage(chat_id=upuser_user.id, text='修改完成！')
    else:
        await context.bot.sendMessage(chat_id=upuser_user.id, text='修改完成！', reply_markup=InlineKeyboardMarkup(keyboard))


# 恢复为默认样式--默认样式即首页的发送信息出来的样式，可修改--仅图文表中有该按钮
async def callback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''取消修改欢迎信息，让自己的信息恢复为默认信息'''
    # 按钮加载
    query = update.callback_query
    await query.answer()
    # 获取用户数据
    upuser_user = update.effective_user
    # 将几号id的信息恢复为默认
    data_callback_message = re_get_number(query.data)

    call_back_message_re(data_callback_message[0])
    # 修改用户权限，取消用户修改权
    sign_mark_change(upuser_user.id, 0)
    keyboard = [
        [InlineKeyboardButton('返回', callback_data='page_picture_text')]
    ]
    # 获取当前文本信息
    text_callback_message = get_message_text("message", data_callback_message[0], 'text')
    graphic_callback_message = get_message_text("message", data_callback_message[0], 'Graphic_id')
    await context.bot.sendMessage(chat_id=upuser_user.id, text='已恢复为默认！\n当前样式为：')
    await context.bot.sendPhoto(chat_id=upuser_user.id, photo=graphic_callback_message[:-1],
                                caption='{}'.format(text_callback_message))
    await context.bot.sendMessage(chat_id=upuser_user.id, text='点击返回', reply_markup=InlineKeyboardMarkup(keyboard))


# 主类方法
def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6034899603:AAHuPres3X5Gz8ZbmwaAzTj38Vw48zUJuDA").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    application.add_handlers(handlers={
        -1: [
            CommandHandler('start', start),
            CallbackQueryHandler(hello_message, pattern='hello_message'),
            CallbackQueryHandler(page_picture_text, pattern='page_picture_text'),
            CallbackQueryHandler(send_message, pattern='send_message'),
            CallbackQueryHandler(edit_message, pattern='edit_message'),
            CallbackQueryHandler(edit_url, pattern='edit_url'),
            MessageHandler(filters.TEXT | filters.PHOTO | filters.ANIMATION | filters.VIDEO |
                           filters.ATTACHMENT, edit_message),
        ],
        -2: [
            CallbackQueryHandler(change_message, pattern='change_message'),
            CallbackQueryHandler(callback_message, pattern='callback_message'),
        ],
        -3: [
        ],
        -4: [
        ]
    })
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()