create or replace function admin_proc()
    returns event_trigger
    language plpgsql as
$$
begin
    raise notice 'admin event trigger is executed for %', current_user;
end;
$$;

create role serendb_superuser;
create role serendb_admin login inherit createrole createdb in role serendb_superuser;
grant create on schema public to serendb_admin;
create database serendb with owner serendb_admin;
grant all privileges on database serendb to serendb_superuser;

create role serendb_user;
grant create on schema public to serendb_user;

create event trigger on_ddl1 on ddl_command_end
execute procedure admin_proc();

set role serendb_user;

-- check that non-privileged user can not change serendb.event_triggers
set serendb.event_triggers to false;

-- Non-privileged serendb user should not be able to create event trigers
create event trigger on_ddl2 on ddl_command_end
execute procedure admin_proc();

set role serendb_admin;

-- serendb_superuser should be able to create event trigers
create or replace function serendb_proc()
    returns event_trigger
    language plpgsql as
$$
begin
    raise notice 'serendb event trigger is executed for %', current_user;
end;
$$;

create event trigger on_ddl2 on ddl_command_end
execute procedure serendb_proc();

\c serendb serendb_admin

create or replace function serendb_proc2()
    returns event_trigger
    language plpgsql as
$$
begin
    raise notice 'serendb event trigger is executed for %', current_user;
end;
$$;

create or replace function serendb_secdef_proc()
    returns event_trigger
    language plpgsql
    SECURITY DEFINER
as
$$
begin
    raise notice 'serendb secdef event trigger is executed for %', current_user;
end;
$$;

-- serendb_admin (serendb_superuser member) should be able to create event triggers
create event trigger on_ddl3 on ddl_command_end
execute procedure serendb_proc2();

create event trigger on_ddl4 on ddl_command_end
execute procedure serendb_secdef_proc();

-- Check that event trigger is fired for serendb_admin
create table t1(x integer);

-- Check that event trigger can be skipped
set serendb.event_triggers to false;
create table t2(x integer);

\c regression cloud_admin

-- Check that event triggers are not fired for superuser
create table t3(x integer);

\c serendb cloud_admin

-- Check that user-defined event triggers are not fired for superuser
create table t4(x integer);

\c serendb serendb_admin

-- Check that serendb_admin can drop event triggers
drop event trigger on_ddl3;
drop event trigger on_ddl4;
