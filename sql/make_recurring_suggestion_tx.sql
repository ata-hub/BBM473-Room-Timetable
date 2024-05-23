begin transaction;

do $$
declare 
	event_var integer;
	timeslot_var integer;
	start_not_available boolean;
	end_not_available boolean;
	to_start time := %(to_start)s;
	to_end time :=  %(to_end)s;
	start_day date := %(start_day)s;
	end_day date := %(end_day)s;
	room integer :=  %(room)s;
	curr_user text :=  %(curr_user)s;
	interval integer := %(interval)s;
	start_day_copy date := start_day;
	room_dept_id integer;
    capacity integer;
		
begin
    select capacity from rooms where room_id = room into capacity;
	select department_id from rooms where room_id = room into room_dept_id;

	while start_day_copy <= end_day loop
		select exists (select 1 from timeslots t, bookings b  where t.date = start_day_copy and b.room_id = room
															and b.timeslot_id = t.timeslot_id --???
															and t.start_time < to_start
															and t.end_time > to_start) 
					  into start_not_available;
					 
		select exists (select 1 from timeslots t, bookings b where t.date = start_day_copy and b.room_id = room
																and b.timeslot_id = t.timeslot_id --???
											                    and to_start < t.start_time
											                    and to_end > t.start_time)
					  into end_not_available;
					 
		if start_not_available = true or end_not_available then 
			exit;
		end if;
	
		start_day_copy := start_day_copy + interval;
	end loop;
	
	if start_not_available = true or end_not_available = true then 
		raise exception 'Cant make a suggestion for another room';
	else 
        select * from rooms r
		where r.capacity >= capacity and r.department_id = room_dept_id;
    end if;

end;
$$;
end transaction;