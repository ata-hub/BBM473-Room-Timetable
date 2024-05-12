begin transaction;

do $$
declare
	event_to_delete integer := 2;	

begin
	delete from timeslots t where exists (select 1 from bookings b where b.timeslot_id = t.timeslot_id
											and b.event_id = event_to_delete
											group by b.timeslot_id, b.event_id
											having count(*) = 1);
										
	delete from bookings b where b.event_id = event_to_delete;
	
	delete from events where event_id = event_to_delete;
end;
$$;

end transaction;