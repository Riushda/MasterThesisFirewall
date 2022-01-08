#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include "rule.h"
#include "utils.h"
#include "netlink.h"
#include "constant.h"

#ifndef HANDLERS_H
#define HANDLERS_H

enum
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