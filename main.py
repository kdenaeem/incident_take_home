#!/usr/bin/env python3
import json
import argparse
from datetime import datetime, timedelta


# interval map (0, 'A'), (3, 'B'), (5, 'A')

# 0 -> 'A'
# 1 -> 'A'
# 2 -> 'A'
# 3 -> 'B'
# 4 -> 'B'
# 5 -> 'A'
# 6 -> 'A'


def parse_timestamp(ts):
    """Parse ISO timestamp to datetime."""
    return datetime.fromisoformat(ts.replace('Z', '+00:00'))

def format_timestamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")



def generate_base_shifts(users, handover_start, interval, from_time, until_time):
    shifts = []
    i = 0  # Always start from first user
    current_start = handover_start
    
    while current_start < until_time:
        current_end = current_start + interval
        user = users[i % len(users)]
        
        shifts.append((current_start, current_end, user))
        
        current_start = current_end
        i += 1
    
    return shifts


def build_entry(entry, from_time, until_time):
    start, end, user = entry
    
    start = max(start, from_time)
    end = min(end, until_time)
    
    if start < end:
        return {
            "user" : user,
            "start_at" : format_timestamp(start),
            "end_at" : format_timestamp(end)
        }
    return None

def overlaps(entry_start, entry_end, override_start, override_end):
    return entry_start < override_end and override_start < entry_end

def apply_overrides(base_shifts, overrides):
    result = []
    
    for start, end, user in base_shifts:
        current_start = start
        
        parsed_overrides = []
        
        
        # Find all override that affects this shift
        for override_start, override_end, override_user in overrides:
            if overlaps(start, end, override_start, override_end):
                parsed_overrides.append((override_start, override_end, override_user))

        parsed_overrides.sort(key=lambda x: x[0])
        
        
        # Split each each around the overrides
        for override_start, override_end, override_user in parsed_overrides:
            if current_start < override_start < end:
                result.append((current_start, override_start, user))
                
            # Add the override 
            override_actual_start = max(current_start, override_start)
            override_actual_end = min(end, override_end)
            
            if override_actual_start < override_actual_end:
                result.append((override_actual_start, override_actual_end, override_user))
                
            current_start = max(current_start, override_actual_end)
            
        
        if current_start < end:
            result.append((current_start, end, user))
            
    return result
        
            

def render_schedule(schedule_config, overrides_list, from_time, until_time):
    users = schedule_config['users']
    handover_start = parse_timestamp(schedule_config['handover_start_at'])
    interval = timedelta(days=schedule_config['handover_interval_days'])

    from_dt = parse_timestamp(from_time)
    until_dt = parse_timestamp(until_time)
    
    parsed_overrides = []
    for override in overrides_list:
        override_start = parse_timestamp(override['start_at'])
        override_end = parse_timestamp(override['end_at'])
        parsed_overrides.append((override_start, override_end, override['user']))
    
    base_shifts = generate_base_shifts(users, handover_start, interval, from_dt, until_dt)
    
    final_shifts = apply_overrides(base_shifts, parsed_overrides)
    final_entries = [build_entry(shift, from_dt, until_dt) for shift in final_shifts]
    
    
    return [entry for entry in final_entries if entry is not None]


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--schedule', required=True)
    parser.add_argument('--overrides', required=True)
    parser.add_argument('--from', dest='from_time', required=True)
    parser.add_argument('--until', required=True)
    
    args = parser.parse_args()
    
    with open(args.schedule, 'r') as f:
        schedule_config = json.load(f)
        
    with open(args.overrides, 'r') as f:
        overrides_list = json.load(f)
        
    results = render_schedule(
        schedule_config,
        overrides_list,
        args.from_time,
        args.until
    )

    print(json.dumps(results, indent=2))
