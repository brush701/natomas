-- Trigger functions
create or replace function create_modified_insert() returns trigger as $$
begin
    NEW.created = extract(epoch from now())::integer;
    NEW.modified = extract(epoch from now())::integer;
    return NEW;
end;
$$ language 'plpgsql';

create or replace function modified_update() returns trigger as $$
begin
    NEW.modified = extract(epoch from now())::integer;
    return NEW;
end;
$$ language 'plpgsql';

-- Triggers for created and modified times

--create trigger users_cm_trg
--before insert on users
--for each row execute procedure create_modified_insert();
