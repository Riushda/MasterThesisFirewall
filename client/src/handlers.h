#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>

#ifndef HANDLERS_H
#define HANDLERS_H

enum R_VALUE
{
    NO_HANDLER = -1,
    HANDLED = 1
};

typedef int (*handler)(int argc, char **argv);

typedef struct
{
    const char *name;
    const handler handler;
} handler_t;

int handle_cmd(char name[], int argc, char **argv);

#endif