typedef struct interval
{
	int start;
	int end;
} interval_t;

void print_int_constraint(interval_t interval);

void create_int_constraint(interval_t *interval, int start, int end);

int inside(interval_t interval, int element);