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
	event_title text :=  %(event_title)s;
	event_desc text :=  %(event_desc)s;
	room_dept_id integer;
	user_role text;
	can_book boolean;

begin
	select exists (select 1 from timeslots t, bookings b  where t.date = day and b.room_id = room
															and b.timeslot_id = t.timeslot_id --???
															and t.start_time <= to_start
															and t.end_time >= to_start) 
				  into start_not_available;
	select exists (select 1 from timeslots t, bookings b where t.date = day and b.room_id = room
															and b.timeslot_id = t.timeslot_id --???
										                    and to_start <= t.start_time
										                    and to_end >= t.start_time)
				  into end_not_available;
				 
	if start_not_available = true or end_not_available = true then 
		raise exception 'this timeslot is taken';
	else
		select r.department_id from rooms r where r.room_id = room into room_dept_id;
		select u.role from users u where u.username = curr_user into user_role;
	
		if user_role = 'student' then
			select exists (select 1 from user_permissions up where up.username = curr_user
																and up.room_id = room)
							into can_book;
		elsif user_role = 'instructor' then
			select exists (select 1 from users u where u.username = curr_user
													and u.department_id = room_dept_id)
							into can_book;
		else
			can_book := true;
		end if;
	
		if can_book = true then
			-- events 
			select e.event_id
			from events e
			where e.title = event_title and e.description = event_desc and e.organizer = curr_user
			into event_var;
		
			if event_var is null then
				insert into events(title, description, organizer)
				values (event_title, event_desc, curr_user)           
				returning event_id into event_var;
			else
				raise exception 'this event has been created before';
			end if;
		
			-- timeslots
			select t.timeslot_id
			from timeslots t
			where t.date = day and t.start_time = to_start and t.end_time = to_end
			into timeslot_var;
		
			if timeslot_var is null then
				insert into timeslots (date, start_time, end_time)
				values (day, to_start, to_end)
				returning timeslot_id into timeslot_var;
			
				insert into bookings(room_id, timeslot_id, event_id)
				values (room, timeslot_var, event_var);
			else
				insert into bookings(room_id, timeslot_id, event_id)
				values (room, timeslot_var, event_var);
			end if;
		
		else 
			raise exception 'This user cannot book this room.';
		end if;
	
	end if;

end;
$$;
end transaction;