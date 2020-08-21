"""
所有数据都存储在服务端
用户打开
->一级界面
--> (录入客户)

LOGI 登录
SIGN 注册
EXIT 退出
TRAN 翻译
HIST 历史
"""

from socket import *
import sys
import time

#!!!所有发送提取成函数

ADDR=("localhost",8888)

# over
def showL1():
    while True:
        order = input("""-----欢迎使用在线字典-----
        (1)登录
        (2)注册
        (3)退出
------------------------
请输入指令：""")
        if order in "123":
            print("————————————————————————""")
            return order
        print("请输入正确指令，蠢货！")

#over
def showL2():
    while True:
        order=input("""========================
    （1）查单词
    （2）历史记录
    （3）注销
------------------------
请输入指令：""")
        if order in "123":
            return order
        else:
            print("请输入正确指令")

#over
# ！！！考虑登录中途返回一级界面的情况！！！ 目前退出login后会重新连接服务端
def log_in(client:socket):
    while True:
        name=input("请输入用户名") # !!!用户名和密码不允许出现空格!!!
        pd=input("请输入密码")
        msg=f"LOGI {name} {pd}"
        client.send(msg.encode())
        ans=client.recv(1024)
        if ans==b"Y":
            # 通过则进入二级界面
            # showL2() # 如果在本函数内调用，则本函数不能结束
            print("登录成功，等待跳转")
            time.sleep(0.3)
            print("————————————————————————\n\n\n\n")
            return name
        elif ans==b"A":
            print("该用户正在使用中")
        else:
            print("用户名或者密码错误")

#over
# ！！！考虑注册中途返回一级界面的情况！！！
def sign_up(client:socket):
    while True:
        name=input("请输入用户名（不能带有空字符）")
        pd=input("请输入密码（不能带有空字符）")
        # 检测是否合格，可做成函数 ？？？
        if " " in name or " " in pd:
            print("用户名不能带有空字符！")
            continue
        # 检测是否已注册
        msg=f"SIGN {name} {pd}"
        client.send(msg.encode())
        ans=client.recv(1024)
        if ans==b"Y":
            print("注册成功,即将跳转到一级界面")
            # 等待可以独立为函数
            time.sleep(0.3)
            print("————————————————————————\n\n\n\n")
            return
        print("用户名已经注册")


# over
def c_exit(client:socket):
    client.send(b"EXIT ")
    client.close()
    sys.exit()

#over
# 每次实现一级目录界面需要传入客户端套接字 !!! log_in sign_up!!!
def L1_Interface(client:socket):
    while True:
        #展示一级界面
        order=showL1()
        #讨论情况
        if order=="1":
            #？？？此处调用其他函数，本函数无法结束，如果直接退出，让主函数调用返回值是否影响效率？？？
            # 成功则进入二级界面
            # L2_Interface(client)
            # 因为此处L2_Interface()是主要运行的程序，所以退出本函数交给主函数来调用
            return log_in(client)
        if order=="2":
            sign_up(client)
        if order=="3":#
            c_exit(client)

# # over
# # 注销时重新连接服务端
# def reboot(client):
#     client.close()
#     client = socket()
#     client.connect(ADDR)
#     return client

#over
def transport(client):
    print("输入单词，即可返回解释")
    while True:
        word=input(">>")
        if not word:
            break
        msg=f"TRAN {word}"
        client.send(msg.encode())
        mean=client.recv(1024).decode()
        # 如果服务端返回！！，则未找到对应单词
        if mean==f"!!":
            mean="没找到对应单词的含义"
        print(mean)

#over
def history(client):
    client.send(b"HIST ")
    while True:
        his=client.recv(1024).decode()
        print(his) # 需改进！！！
        if his=="##":
            break

def logout(client,user):
    client.send(b"EXIT ")
    client.close()
    print(f"欢迎下次使用 {user}")
    time.sleep(0.3)
    print("————————————————————————\n\n\n\n")
    return "reboot"  # 退出二级界面


def L2_Interface(client:socket,user):
    while True:
        #展示界面
        o2 = showL2()
        if o2 == "1":
            transport(client)
        if o2 == "2":
            history(client)
        if o2 == "3":  # （一般注销应该断开与服务端的连接）回到一级界面
            return logout(client,user)

# over
def main():
    # 创建套接字并连接服务器（一般登录和注册操作后才会连接服务器，用类实现会更好）
    # !!!打开后直接连接服务器!!!

    #因为本例中所有数据存放在服务端，所以直接在主函数创建套接字
    while True:
        client=socket()
        client.connect(ADDR)
        # 一级界面接收到登录命令后，接收用户名并退出，由主程序调用二级界面
        user=L1_Interface(client)
        # 二级界面要么退出客户端，要么注销
        # 注销后，客户端重新连接服务端
        L2_Interface(client,user)

if __name__=="__main__":
    main()