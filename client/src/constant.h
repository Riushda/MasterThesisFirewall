#ifndef CONSTANT_H
#define CONSTANT_H

#define MAX_PAYLOAD 1024
#define NETLINK_FW 17

typedef unsigned char bool_t;
typedef unsigned char proto_t;
typedef unsigned char bitmask_t;
typedef unsigned char string_t;

enum ERRORS
{
    NO_HANDLER = -1,
    HANDLED = 1
};

enum ACTIONS
{
    A_RULE = 0,
    R_RULE = 1
};

#endif