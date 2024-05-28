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
	event_title text :=  %(event_title)s;
	event_desc text :=  %(event_desc)s;
	interval integer := %(interval)s;
	start_day_copy date := start_day;
	room_dept_id integer;
	user_role text;
	can_book boolean;
		
begin
	while start_day_copy <= end_day loop
		select exists (select 1 from timeslots t, bookings b  where t.date = start_day_copy and b.room_id = room
															and b.timeslot_id = t.timeslot_id --???
															and t.start_time <= to_start
															and t.end_time >= to_start) 
					  into start_not_available;
					 
		select exists (select 1 from timeslots t, bookings b where t.date = start_day_copy and b.room_id = room
																and b.timeslot_id = t.timeslot_id --???
											                    and to_start <= t.start_time
											                    and to_end >= t.start_time)
					  into end_not_available;
					 
		if start_not_available = true or end_not_available then 
			exit;
		end if;
	
		start_day_copy := start_day_copy + interval;
	end loop;
	
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
		
			while start_day <= end_day loop
				-- timeslots
				select t.timeslot_id
				from timeslots t
				where t.date = start_day and t.start_time = to_start and t.end_time = to_end
				into timeslot_var;
			
				if timeslot_var is null then
					insert into timeslots (date, start_time, end_time)
					values (start_day, to_start, to_end)
					returning timeslot_id into timeslot_var;
				
					insert into bookings(room_id, timeslot_id, event_id)
					values (room, timeslot_var, event_var);
				else
					insert into bookings(room_id, timeslot_id, event_id)
					values (room, timeslot_var, event_var);
				end if;
			
				start_day := start_day + interval;
			end loop;
		
		end if;
	
	end if;

end;
$$;
end transaction;