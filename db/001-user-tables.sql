drop table if exists users cascade;
create table users (
    id serial primary key,
    username varchar(255) unique,
    first_name varchar(255),
    last_name varchar(255),
    email text,
    cryptpass text,
    last_login integer,
    created integer,
    modified integer,
    deleted boolean default false
);

drop table if exists sessions cascade;
create table sessions (
    user_id int references users(id),
    session_id varchar(128) primary key,
    updates integer default 1,
    created integer,
    modified integer
);

create table permission_types (
    id serial primary key,
    name varchar(255)
);

create table user_permissions (
    user_id int references users(id),
    permission_id int references permission_types(id)
);
