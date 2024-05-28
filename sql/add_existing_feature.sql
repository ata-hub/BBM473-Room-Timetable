begin transaction;

do $$
declare 
	feature_id_var integer := %(feature_id)s;
    room_id_var integer := %(room_id)s;
    room_has boolean;

begin
    select exists (select 1 from room_features rf where rf.room_id = room_id_var 
                                                    and rf.feature_id = feature_id_var)
                    into room_has;

    if room_has = true then
        update room_features rf set is_working = true where rf.room_id = room_id_var 
                                                    and rf.feature_id = feature_id_var;
    else 
        insert into room_features (room_id, feature_id, is_working)
        values (room_id_var, feature_id_var, true);
    end if;

end;
$$;
end transaction;