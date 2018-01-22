insert into permission_types(name) values ('admin');
insert into permission_types(name) values ('basic');

-- Add initial user
insert into users(
    username, first_name, last_name, email, cryptpass, last_login
)
values (
    'admin', 'Admin', 'User', 'dev@pioneersquarelabs.com',
    '$2a$12$KPM5zKM4mS3pYssYf3UWmun9Atd7G0bqS6tAddpPutt8z6KNFKEq.',
    0
);

-- Make initial user an admin
insert into user_permissions (user_id, permission_id) select id, 1 from users;
insert into user_permissions (user_id, permission_id) select id, 2 from users;

