#include <linux/time.h>
#include <linux/ktime.h>

typedef struct daily_time
{
	uint16_t hour;
	uint16_t minute;
} daily_time_t;

typedef struct time_constraint
{
	daily_time_t start;
	daily_time_t end;
} time_constraint_t;

void print_time_constraint(time_constraint_t time_c);

void create_time_constraint(time_constraint_t *time_c, uint16_t hour_start, uint16_t min_start, uint16_t hour_end, uint16_t min_end);

void set_current_time(uint16_t *hour, uint16_t *minute);

int time_check(time_constraint_t *time_c);

int inside(daily_time_t start, daily_time_t now, daily_time_t end);