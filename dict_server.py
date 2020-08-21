"""
网络通信框架
"""
import sys
import time
from socket import *
import pymysql
from threading import Thread
from multiprocessing import Process
from signal import *

HOST="localhost"
PORT=8888
ADDR=(HOST,PORT)

signal(SIGCHLD,SIG_IGN)
online_user={} # 记录在线用户

# over 注册
def sign_up(conndf:socket,m,db):
    # 直接传入连接，在函数内另创游标，以便写入用户信息后及时提交!!!???
    cur=db.cursor()
    name,pd=m.split(" ")
    sql="insert into user values(Null,%s,%s)"
    try:
        cur.execute(sql,[name,pd])

        print(f"用户{name}注册成功!")
        db.commit()
        msg="Y"
    except Exception as e:
        print(e)
        msg="N"
    conndf.send(msg.encode())

# 登录
def log_in(conndf, m,cur,addr):
    #不需要向数据库写入信息
    name,pd=m.split(" ")
    if name in online_user:
        conndf.send(b"A")
        return
    sql="select id from user where name=%s and password=%s"
    cur.execute(sql,[name,pd])
    id=cur.fetchone()[0]
    if not id:
        conndf.send(b"N")
        return
    conndf.send(b"Y")
    online_user[id]=name
    print(f"用户 {name}登录成功！")
    return name,id


def exit_client(conndf,addr,cur,db,id):
    print(f"{addr} 断开连接")
    if id:
        del online_user[id]
    conndf.close()
    cur.close()
    db.close()

#over
def translate(conndf, m, cur,id):
    sql="select id,mean from words where word=%s"
    cur.execute(sql,m)
    data=cur.fetchall()
    if not data:
        conndf.send(b"!!")
    else:
        msg=f"{m}:  {data[0][1]}"
        conndf.send(msg.encode())

    # 往数据库中添加记录

    sql="insert into recode (u_id,word) values (%s,%s)"
    cur.execute(sql,[id,m])
    #假设一次就能传输完
    # time.sleep(0.1)
    # conndf.send(b"##")


#历史记录在查单词的时候添加，
def history(conndf, cur,name):
    sql="select u.name,r.word,r.t " \
        "from user as u left join " \
        "recode as r on u.id=r.u_id " \
        "where u.name=%s " \
        "order by r.t desc limit 10"
    cur.execute(sql,name)
    msg=""
    for i in cur.fetchall():
        msg+=f"{i[0]}={i[1]}={i[2]}\n"
    conndf.send(msg.encode())
    time.sleep(0.1)
    conndf.send(b"##")


def t_client(conndf:socket,addr):
    db=pymysql.connect(host="localhost",
                       port=3306,
                       user="root",
                       password="123456",
                       database="dict",
                       charset="utf8")
    cur=db.cursor()
    id=""
    name=""
    while True:
        msg=conndf.recv(1024)
        # 接收的信息前四位为协议
        head,m=msg.decode().split(" ",1)
        """LOGI 登录 SIGN 注册 EXIT 退出 TRAN 翻译 HIST 历史"""
        if head=="LOGI": #over
            name,id=log_in(conndf,m,cur,addr)
        if head=="SIGN": #注册 over
            sign_up(conndf,m,db)
        if head=="TRAN": #over
            translate(conndf,m,cur,id)
            db.commit()
        if head=="EXIT": # over
            exit_client(conndf,addr,cur,db,id)
            return
        if head=="HIST":
            history(conndf,cur,name)

# over
def a_client(server):
    while True:
        conndf,addr=server.accept()
        print(f"接入-> {addr}\n===============")
        t=Thread(target=t_client,args=(conndf,addr))
        # 服务端关闭后允许子用户继续操作，因此不设置daemon
        t.start()


#over
def main():
    """创建套接字，"""
    server=socket(AF_INET,SOCK_STREAM)
    server.bind(ADDR)
    server.listen(5)
    print(f"{ADDR}开始监听\n===================")
    # 服务器没有额外操作，不开辟新进程
    try:
        a_client(server)
    except KeyboardInterrupt:
        print("服务端关闭")
        sys.exit()


if __name__=="__main__":
    main()
