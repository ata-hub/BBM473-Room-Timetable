from datetime import datetime, timedelta, date, time

start_time_str = '08:00'
end_time_str = '17:00'

start_time = datetime.strptime(start_time_str, '%H:%M')
end_time = datetime.strptime(end_time_str, '%H:%M')
current_time = start_time
intervals = []

while current_time <= end_time:
    intervals.append(current_time.strftime('%H:%M'))
    current_time += timedelta(minutes=30)

print(intervals)