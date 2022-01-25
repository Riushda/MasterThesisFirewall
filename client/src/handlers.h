#include <getopt.h>
#include "constant.h"
#include "utils.h"
#include "rule.h"
#include "netlink.h"

#ifndef HANDLERS_H
#define HANDLERS_H

typedef int (*handler)(int argc, char **argv);

typedef struct
{
    const string_t *name;
    const handler handler;
} handler_t;

int handle_cmd(string_t *name, int argc, char **argv);

#endif