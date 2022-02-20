#include "parser.h"

int create_format(format_t **pattern, uint8_t offset, char *splitter, char *delimiter, char *end){
    
    *pattern = (format_t *)malloc(sizeof(format_t));
    if(*pattern==NULL)
        return -1;

    (*pattern)->offset = offset;

    if(splitter==NULL){
        (*pattern)->splitter = NULL;
    }
    else{
        (*pattern)->splitter = (char *)malloc(strlen(splitter)+1);
        if((*pattern)->splitter==NULL){
            free(*pattern);
            return -1;
        }
        memset((*pattern)->splitter, 0, strlen(splitter)+1);
        memcpy((*pattern)->splitter, splitter, strlen(splitter));
    }

    if(delimiter==NULL){
        (*pattern)->delimiter = NULL;
    }
    else{
        (*pattern)->delimiter = (char *)malloc(strlen(delimiter)+1);
        if((*pattern)->delimiter==NULL){

            if(splitter!=NULL)
                free((*pattern)->splitter);
                
            free(*pattern);
            return -1;
        }
        memset((*pattern)->delimiter, 0, strlen(delimiter)+1);
        memcpy((*pattern)->delimiter, delimiter, strlen(delimiter));
    }

    if(end==NULL){
        (*pattern)->end = NULL;
    }
    else{
        (*pattern)->end = (char *)malloc(strlen(end)+1);
        if((*pattern)->end==NULL){

            if(delimiter!=NULL)
                free((*pattern)->delimiter);

            if(splitter!=NULL)
                free((*pattern)->splitter);

            free(*pattern);
            return -1;
        }
        memset((*pattern)->end, 0, strlen(end)+1);
        memcpy((*pattern)->end, end, strlen(end));
    }

    return 0;
}

void destroy_format(format_t *pattern){
    if(pattern==NULL)
        return;

    if(pattern->splitter!=NULL)
        free(pattern->splitter);

    if(pattern->delimiter!=NULL)
        free(pattern->delimiter);
    
    if(pattern->end!=NULL)
        free(pattern->end);

    free(pattern);
}

uint8_t remove_spaces(char* s, uint8_t len) {
    uint8_t left;
    char* element = s;
    uint8_t offset = 0;

    int i;
    for(i=0; i<len; i++){

        if(*element != ' '){
            memcpy(s+offset, element, 1);
            offset += 1;
        }       
        element += 1;
    }

    left = len - offset;

    memset(element - left, 0, left);

    return offset;
}

int isNumeric(const char *str) 
{
    while(*str != '\0')
    {
        if(*str < '0' || *str > '9')
            return -1;
        str++;
    }
    return 0;
}

int decode_payload(format_t *pattern, char *buf, uint8_t buf_len, data_t **payload){
    int err;

    char *group;
    char *token;
    char field[50];
    char value[50];
    char data[50];
    long long_value;
    int integer_value;
    uint8_t strlen_value;
    char *buffer = buf;

    buf_len = remove_spaces(buffer, buf_len);

    buffer += pattern->offset;      

    if(pattern->end!=NULL)
	    buffer = strsep(&buffer, pattern->end);

    group = buffer;
    if(pattern->delimiter!=NULL)
        group = strsep(&buffer, pattern->delimiter);
    
	while(group){
        memset(field, 0, 50);
        memset(value, 0, 50);
        memset(data, 0, 50);
        memset(&long_value, 0, sizeof(long));
        memset(&integer_value, 0, sizeof(int));

        if(pattern->splitter!=NULL){
           
            token = strsep(&group, pattern->splitter);
            strcpy(field, token);

            token = strsep(&group, pattern->splitter);
            if(token==NULL){
                // if splitter specified but no splitter in the buf
                strcpy(value, field);
                memset(field, 0, 50);
            }
            else{
                strcpy(value, token);
            }
        }
        else{
            strcpy(value, group);
        }

        if(!isNumeric(value)){
            // data is integer

            long_value = atoi(value);
            
            integer_value = (int) long_value;

            err = add_data_t(payload, INT_TYPE, strlen(field), field, &integer_value);
            if(err)
                return -1;
        }
        else{
            // data is string

            strlen_value = (uint8_t) strlen(value);

            memcpy(data, &strlen_value, 1);
            memcpy(data+1, value, strlen_value);

            err = add_data_t(payload, STRING_TYPE, strlen(field), field, data);
            if(err)
                return -1;
        }

        group = NULL;
		if(pattern->delimiter!=NULL)
            group = strsep(&buffer, pattern->delimiter);
	}

    return 0;
}

void print_format(format_t *pattern){
    printf( "format : \n");
    
    printf( "  offset : %d\n", pattern->offset);

    if(pattern->splitter!=NULL)
        printf( "  splitter : %s\n", pattern->splitter);

    if(pattern->delimiter!=NULL)
        printf( "  delimiter : %s\n", pattern->delimiter);

    if(pattern->end!=NULL)
        printf( "  end : %s\n", pattern->end);
}