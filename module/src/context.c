#include "context.h"
// doc https://www.tutorialspoint.com/c_standard_library/time_h.htm
// https://man7.org/linux/man-pages/man0/time.h.0p.html

int time_check(time_constraint_t *time_c){
	struct tm *tm_struct;	
	time64_t totalsecs; // useless be a required argument
	daily_time_t now;
	time_constraint_t *element = time_c;

	memset(tm_struct, 0, sizeof(struct tm));
	memset(&now, 0, sizeof(daily_time_t));

	time64_to_tm(totalsecs, 0, tm_struct);

	now.minute = (uint16_t) tm_struct->tm_min;
	now.hour = (uint16_t) tm_struct->tm_hour;

	while(element!=NULL){
		if(inside(element->start, now, element->end)){
			return 1;
		}

		element = element->next;
	}

	return 0;
}

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

