begin transaction;

do $$
declare
	event_to_delete integer := %(event_id)s;
	curr_user text := %(curr_user)s;
	username text;	

begin
	select e.organizer from events e where e.event_id = event_to_delete into username;

	if username = curr_user then
		delete from bookings b where b.event_id = event_to_delete;

		delete from timeslots t where not exists (select 1 from bookings b 
												where b.timeslot_id = t.timeslot_id);
		
		delete from events where event_id = event_to_delete;
	else 
		raise exception 'This user cannot cancel this reservation.';
	end if;
end;
$$;

end transaction;