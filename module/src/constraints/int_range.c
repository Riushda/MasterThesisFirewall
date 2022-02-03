#include "int_range.h"

void print_int_constraint(interval_t interval){
	printk(KERN_INFO "int constraint : from %d to %d\n", interval.start, interval.end);
}

void create_int_constraint(interval_t *interval, int start, int end){
	interval->start = start;
	interval->end = end;
}

int inside(interval_t interval, int element){
	return interval.start<=element<=interval.end;
}