import pymysql

db=pymysql.connect(host="127.0.0.1",
                   port=3306,
                   user="root",
                   password="123456",
                   database="dict",
                   charset="utf8")
cur=db.cursor()
sql="create table if not exists user" \
    "(id int primary key auto_increment," \
    "name varchar(32) not null," \
    "password varchar(15) not null)"

try:
    cur.execute(sql)
except Exception:
    db.rollback()

    print("user出错了")
db.commit()
sql ="create table if not exists recode" \
     "(id int primary key auto_increment," \
     "u_id int, " \
     "w_id int," \
     "t timestamp," \
     "constraint u_id_fk foreign key(u_id) references user(id)," \
     "constraint w_id_fk foreign key(w_id) references words(id))"

cur.execute(sql)
