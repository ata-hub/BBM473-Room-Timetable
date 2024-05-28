begin transaction;

do $$
declare 
    description text := %(description)s;
    room_id integer := %(room_id)s;
    feature_var integer;

begin
    insert into features (name) values (description) returning feature_id into feature_var;
    insert into room_features (room_id, feature_id, is_working) values (room_id, feature_var, true);
end;
$$;
end transaction;