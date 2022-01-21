#ifndef CONSTANT_H
#define CONSTANT_H

#define NETLINK_FW 17
#define IP_SIZE 32
#define VECTOR_SIZE 4
#define KEY_SIZE 3
#define CHILD_NBR 2
#define TABLE_SIZE 1024

#define ARRAY_SIZE(a) sizeof(a) / sizeof(a[0])

typedef unsigned char vector_t;
typedef unsigned char h_key_t;
typedef unsigned char bool_t;
typedef unsigned char proto_t;
typedef unsigned char bitmask_t;
typedef unsigned char string_t;

#endif