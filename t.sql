create table if not exists recode
     (id int primary key auto_increment,
     u_id int constraint u_id_fk foreign key(u_id) references user(id),
     w_id int constraint w_id_fk foreign key(w_id) references words(id),
     'time' timestamp)