begin transaction;

do $$
declare 
	event_var integer := %(event_var)s;

begin
	WITH BookingPairs AS (
        SELECT
            b1.booking_id AS booking_id1,
            b2.booking_id AS booking_id2,
            b1.event_id,
            t1.date AS date1,
            t2.date AS date2,
            ABS(t1.date - t2.date) AS date_diff
        FROM
            bookings b1
            INNER JOIN bookings b2 ON b1.event_id = b2.event_id AND b1.booking_id < b2.booking_id
            INNER JOIN timeslots t1 ON b1.timeslot_id = t1.timeslot_id
            INNER JOIN timeslots t2 ON b2.timeslot_id = t2.timeslot_id
            WHERE b1.event_id = event_var
    )
    SELECT
        date_diff
    FROM
        BookingPairs;

end;
$$;
end transaction;