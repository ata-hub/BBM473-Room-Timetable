-- select booked event info
explain select  e.event_id , e.title , e.description, b.room_id, t.start_time, t.end_time 
from events e
inner join bookings b on b.event_id = e.event_id
inner join timeslots t on t.timeslot_id = b.timeslot_id;

-- select a specific week's bookings
explain select t."date" , e.event_id, t.start_time, t.end_time 
from events e
inner join bookings b on b.event_id = e.event_id
inner join timeslots t on t.timeslot_id = b.timeslot_id
where t.date between to_date('29-04-2024', 'DD-MM-YYYY') and to_date('05-05-2024', 'DD-MM-YYYY')
and b.room_id = 1;

-- select a room's permission list
explain select up.room_id, u.username 
from user_permissions up
inner join room_permission_requests rpr on up.room_id = rpr.room_id
inner join users u on u.username = up.username
and up.room_id = 31;