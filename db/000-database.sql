drop database if exists sampledb;
drop user if exists sampleadmin;

-- create psladmin
create user sampleadmin superuser;
alter user sampleadmin with password 'sample-admin-123';

-- create database
create database sampledb with owner sampleadmin;
grant all privileges on database sampledb to sampleadmin;
