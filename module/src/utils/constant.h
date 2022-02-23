#ifndef CONSTANT_H
#define CONSTANT_H

#define NETLINK_FW 17
#define IP_SIZE 32
#define VECTOR_SIZE 4
#define KEY_SIZE 3
#define CHILD_NBR 2
#define TABLE_SIZE 1024
#define MAX_PAYLOAD_SIZE 1024

/* netlink_recv_msg first byte */
enum code{PID_INFO=0, ADD=1, REMOVE=2, ENABLE=3, DISABLE=4};

typedef unsigned char vector_t;
typedef unsigned char h_key_t;
typedef unsigned char bool_t;
typedef unsigned char proto_t;
typedef unsigned char bitmask_t;
typedef unsigned char string_t;

#endif