begin transaction;

do $$
declare 
	event_var integer;
	timeslot_var integer;
	start_not_available boolean;
	end_not_available boolean;
	to_start time := %(to_start)s;
	to_end time :=  %(to_end)s;
	day date :=  %(day)s;
	room integer :=  %(room)s;
	curr_user text :=  %(curr_user)s;
	capacity integer;
	room_dept_id integer;

begin
	select capacity from rooms where room_id = room into capacity;
	select department_id from rooms where room_id = room into room_dept_id;

	select exists (select 1 from timeslots t, rooms r  
								where t.date = day and r.capacity >= capacity
								and r.department_id = room_dept_id
								and t.start_time <= to_start
								and t.end_time >= to_start) 
				  into start_not_available;
	select exists (select 1 from timeslots t, rooms r 
								where t.date = day and  r.capacity >= capacity
								and r.department_id = room_dept_id
								and to_start <= t.start_time
								and to_end >= t.start_time)
				  into end_not_available;
				 
	if start_not_available = true or end_not_available = true then 
		raise exception 'Cant make a suggestion for another room';
	else
		select * from rooms r
		where r.capacity >= capacity and r.department_id = room_dept_id;
	end if;

end;
$$;
end transaction;