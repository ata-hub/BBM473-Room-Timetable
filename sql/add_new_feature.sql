begin transaction;

do $$
declare 
    feature_var integer := %(feature_var)s;
    room_id integer := %(room_id)s;

begin
    update features set is_accepted = true where feature_id = feature_var;
    insert into room_features (room_id, feature_id, is_working) values (room_id, feature_var, true);
end;
$$;
end transaction;