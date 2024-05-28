begin transaction;

do $$
declare 
	timeslot_var integer;
	start_not_available boolean;
	end_not_available boolean;
	new_to_start time := %(new_to_start)s;
	new_to_end time :=  %(new_to_end)s;
	new_start_day date := %(new_start_day)s;
	new_end_day date := %(new_end_day)s;
	new_room integer :=  %(new_room)s;
	curr_user text :=  %(curr_user)s;
	old_interval integer := %(old_interval)s;
	old_event_id integer := %(event_id)s;
	start_day_copy date := new_start_day;
	room_dept_id integer;
	user_role text;
	can_book boolean;
		
begin
	while start_day_copy <= new_end_day loop
		select exists (select 1 from timeslots t, bookings b, events e where t.date = start_day_copy and b.room_id = new_room
															and b.timeslot_id = t.timeslot_id --???
															and b.event_id = e.event_id
															and t.start_time <= new_to_start
															and t.end_time >= new_to_start
															and e.event_id <> old_event_id) 
					  into start_not_available;
					 
		select exists (select 1 from timeslots t, bookings b, events e where t.date = start_day_copy and b.room_id = new_room
																and b.timeslot_id = t.timeslot_id --???
																and b.event_id = e.event_id
											                    and new_to_start <= t.start_time
											                    and new_to_end >= t.start_time
																and e.event_id <> old_event_id)
					  into end_not_available;
					 
		if start_not_available = true or end_not_available then 
			exit;
		end if;
	
		start_day_copy := start_day_copy + old_interval;
	end loop;
	
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
            delete from bookings b where b.event_id = old_event_id;

		    delete from timeslots t where not exists (select 1 from bookings b 
												where b.timeslot_id = t.timeslot_id);
		
			while new_start_day <= new_end_day loop
				-- timeslots
				select t.timeslot_id
				from timeslots t
				where t.date = new_start_day and t.start_time = new_to_start and t.end_time = new_to_end
				into timeslot_var;
			
				if timeslot_var is null then
					insert into timeslots (date, start_time, end_time)
					values (new_start_day, new_to_start, new_to_end)
					returning timeslot_id into timeslot_var;
				
					insert into bookings(room_id, timeslot_id, event_id)
					values (new_room, timeslot_var, old_event_id);
				else
					insert into bookings(room_id, timeslot_id, event_id)
					values (new_room, timeslot_var, old_event_id);
				end if;
			
				new_start_day := new_start_day + old_interval;
			end loop;
		
		end if;
	
	end if;

end;
$$;
end transaction;