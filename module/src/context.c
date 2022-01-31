#include "context.h"
// doc https://www.tutorialspoint.com/c_standard_library/time_h.htm
// https://man7.org/linux/man-pages/man0/time.h.0p.html

void set_current_time(uint16_t *hour, uint16_t *minute){
	struct timespec curr_tm;
	memset(&curr_tm, 0, sizeof(curr_tm));

	getnstimeofday(&curr_tm);

	*hour = (uint16_t) (curr_tm.tv_sec / 3600) % 24;
	*minute = (uint16_t) ((curr_tm.tv_sec % (24*3600)) - (*hour*3600))/60;

	/*printk("TIME: %.2lu:%.2lu:%.2lu:%.6lu \r\n",
                   (curr_tm.tv_sec / 3600) % (24),
                   (curr_tm.tv_sec / 60) % (60),
                   curr_tm.tv_sec % 60,
                   curr_tm.tv_nsec / 1000);*/
}

int time_check(time_constraint_t *time_c){
		
	daily_time_t now;
	time_constraint_t *element = time_c;
	
	memset(&now, 0, sizeof(daily_time_t));

	set_current_time(&now.hour, &now.minute);

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

