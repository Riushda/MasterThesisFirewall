#include "time_constraint.h"

void print_time_constraint(time_constraint_t time_c){
	printk(KERN_INFO "time constraint : from %d:%d to %d:%d\n", time_c.start.hour, time_c.start.minute, time_c.end.hour, time_c.end.minute);
}

void create_time_constraint(time_constraint_t *time_c, uint16_t hour_start, uint16_t min_start, uint16_t hour_end, uint16_t min_end){
	daily_time_t start;
	daily_time_t end;
	
	memset(&start, 0, sizeof(daily_time_t));
	start.hour = hour_start;
	start.minute = min_start;

	memset(&end, 0, sizeof(daily_time_t));
	end.hour = hour_end;
	end.minute = min_end;

	time_c->start = start;
	time_c->end = end;
}

void set_current_time(uint16_t *hour, uint16_t *minute){
	struct timespec curr_tm;
	memset(&curr_tm, 0, sizeof(curr_tm));

	getnstimeofday(&curr_tm);

	*hour = (uint16_t) (curr_tm.tv_sec / 3600) % 24;
	*minute = (uint16_t) (curr_tm.tv_sec/60 % (24*60)) - (*hour*60);
}
/* check if time_constraint is currently respected */
int time_check(time_constraint_t *time_c){
		
	daily_time_t now;
	time_constraint_t *element = time_c;
	
	memset(&now, 0, sizeof(daily_time_t));

	set_current_time(&now.hour, &now.minute);

	return inside(element->start, now, element->end);
}

/* return 1 if now is inside time interval and 0 otherwise */
int inside(daily_time_t start, daily_time_t now, daily_time_t end){
	uint16_t start_min = start.hour*60+start.minute;
	uint16_t now_min = now.hour*60+now.minute;
	uint16_t end_min = end.hour*60+end.minute;

	if(start.hour<=end.hour){
		return start_min<=now_min && now_min<=end_min;
	}
	else{
		return start_min<=now_min || now_min<=end_min;
	}
}
