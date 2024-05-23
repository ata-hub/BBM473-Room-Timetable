begin transaction;

do $$
declare 
	timeslot_var integer;
	start_not_available boolean;
	end_not_available boolean;
	new_to_start time := %(to_start)s;
	new_to_end time :=  %(to_end)s;
	new_day date :=  %(day)s;
	new_room integer :=  %(room)s;
	curr_user text :=  %(curr_user)s;
    event_id integer := %(event_id)s;
	room_dept_id integer;
	user_role text;
	can_book boolean;

begin
	select exists (select 1 from timeslots t, bookings b  where t.date = day and b.room_id = new_room
															and b.timeslot_id = t.timeslot_id --???
															and t.start_time <= new_to_start
															and t.end_time >= new_to_start) 
				  into start_not_available;
	select exists (select 1 from timeslots t, bookings b where t.date = day and b.room_id = new_room
															and b.timeslot_id = t.timeslot_id --???
										                    and new_to_start <= t.start_time
										                    and new_to_end >= t.start_time)
				  into end_not_available;
				 
	if start_not_available = true or end_not_available = true then 
		raise exception 'this timeslot is taken';
	else
		select r.department_id from rooms r where r.room_id = new_room into room_dept_id;
		select u.role from users u where u.username = curr_user into user_role;
	
		if user_role = 'student' then
			select exists (select 1 from user_permissions up where up.username = curr_user
																and up.room_id = new_room)
							into can_book;
		elsif user_role = 'instructor' then
			select exists (select 1 from users u where u.username = curr_user
													and u.department_id = room_dept_id)
							into can_book;
		else
			can_book := true;
		end if;
	
		if can_book = true then
            delete from bookings b where b.event_id = event_id;

		    delete from timeslots t where exists (select 1 from bookings b where b.timeslot_id = t.timeslot_id
												and b.event_id = event_id
												group by b.timeslot_id, b.event_id
												having count(*) = 1);

			-- timeslots
			select t.timeslot_id
			from timeslots t
			where t.date = new_day and t.start_time = new_to_start and t.end_time = new_to_end
			into timeslot_var;
		
			if timeslot_var is null then
				insert into timeslots (date, start_time, end_time)
				values (day, new_to_start, new_to_end)
				returning timeslot_id into timeslot_var;
			
				insert into bookings(room_id, timeslot_id, event_id)
				values (new_room, timeslot_var, event_id);
			else
				insert into bookings(room_id, timeslot_id, event_id)
				values (new_room, timeslot_var, event_id);
			end if;
		
		else 
			raise exception 'This user cannot book this room.';
		end if;
	
	end if;

end;
$$;
end transaction;