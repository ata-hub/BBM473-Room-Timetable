begin transaction;

do $$
declare 
	feature_id integer := %(feature_id)s;
    room_id integer := %(room_id)s;
    room_has boolean;

begin
    select exists (select 1 from room_features rf where rf.room_id = room_id 
                                                    and rf.feature_id = feature_id)
                    into room_has;

    if room_has = true then
        update room_features rf set is_working = true where f.room_id = room_id 
                                                    and rf.feature_id = feature_id;
    else 
        insert into room_features (room_id, feature_id, is_working)
        values (room_id, feature_id, true);
    end if;

end;
$$;
end transaction;