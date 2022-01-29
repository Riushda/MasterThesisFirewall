#include <linux/time.h>

typedef struct daily_time
{
	uint16_t hour;
	uint16_t minute;
} daily_time_t;

typedef struct time_constraint
{
	daily_time_t start;
	daily_time_t end;
	struct time_constraint *next;
} time_constraint_t;

typedef struct context
{
	uint8_t type;
	void *constraint;
	struct context *next;
} context_t;

int time_check(time_constraint_t *time_c);

int inside(daily_time_t start, daily_time_t now, daily_time_t end);

