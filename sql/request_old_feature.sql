begin transaction;

do $$
declare 
	feature_id integer := %(feature_id)s;
    description integer := %(description)s;
    room_id integer := %(room_id)s;
    room_has boolean;

begin
    select exists (select 1 from room_features rf where rf.room_id = room_id 
                                                    and rf.feature_id = feature_id)
                    into room_has;

    if room_has = true then
        update room_features rf set is_working = false where f.room_id = room_id 
                                                    and rf.feature_id = feature_id;

        insert into feature_requests (description, room_id, feature_id) 
        values (description, room_id, feature_id);
    else
        insert into feature_requests (description, room_id, feature_id) 
        values (description, room_id, feature_id);
    end if;

end;
$$;
end transaction;