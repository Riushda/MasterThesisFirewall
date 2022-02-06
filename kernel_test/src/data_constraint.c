#include "data_constraint.h"

/* convert buffer to struct functions */

int buffer_to_data_t(data_t *data, uint8_t type, char *buffer){
	string_value_t *str_value;
	interval_t *int_range;
	data_t *element;
	int i;

	uint8_t n_value = (uint8_t) *buffer;

	data = (data_t *)malloc(sizeof(data_t));
	if(data==NULL)
		return -1;

	memset(data, 0, sizeof(data_t));

	element = data;
	
	for(i=0; i<n_value; i++){

		switch (type)
		{
			case INT_TYPE:
			
				element->value.int_value = *buffer;

				buffer += sizeof(int);

				break;
			case STRING_TYPE:

				str_value = &(element->value.str_value);

				str_value->str_len = (uint8_t) *buffer;
				buffer += sizeof(uint8_t);

				str_value->str = (char *)malloc(str_value->str_len);
				if(str_value->str==NULL){
					destroy_data_t(data, type);
					return -1;
				}
				memset(str_value->str, 0, str_value->str_len);
				memcpy(str_value->str, buffer, str_value->str_len);

				buffer += str_value->str_len;

				break;
			case INT_RANGE_TYPE:

				int_range = &(element->value.int_range);
				
				memcpy(&(int_range->start), buffer, sizeof(int));

				buffer += sizeof(int);

				memcpy(&(int_range->end), buffer, sizeof(int));

				buffer += sizeof(int);
				
				break;
			default:
				printf( "data type not know\n");
				destroy_data_t(data, type);
				return -1;
		}

		if(i<n_value-1){
			element->next = (data_t *)malloc(sizeof(data_t));
			if(element==NULL)
				return -1;

			memset(element, 0, sizeof(data_t));
		}

		element = element->next;
	}

	return 0;
}

int buffer_to_data_constraint(data_constraint_t *data_c, char *msg){
	int err;
	int i;
	data_constraint_t *element;
	char *buffer = msg;

	uint8_t n_constraint = (uint8_t) *buffer;
	buffer += 1;

	data_c = (data_constraint_t *)malloc(sizeof(data_constraint_t));
	if(data_c==NULL)
		return -1;

	memset(data_c, 0, sizeof(data_constraint_t));

	element = data_c;
	for(i=0; i<n_constraint; i++){

		element->type = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);

		element->field_len = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);

		element->field = (char *)malloc(element->field_len);
		if(element->field==NULL){
			destroy_data_constraint(data_c);
			return -1;
		}
		
		memset(element->field, 0, element->field_len);
		memcpy(element->field, buffer, element->field_len);

		buffer += element->field_len;

		element->data = (data_t *)malloc(sizeof(data_t));
		if(element->data==NULL){
			destroy_data_constraint(data_c);
			return -1;
		}

		err = buffer_to_data_t(element->data, element->type, buffer);
		if(err){
			destroy_data_constraint(data_c);
			return -1;
		}

		if(i<n_constraint-1){
			element->next = (data_constraint_t *)malloc(sizeof(data_constraint_t));
			if(element==NULL)
				return -1;

			memset(element, 0, sizeof(data_constraint_t));
		}

		element = element->next;
	}

	return 0;
}

/* convert struct to buffer functions */

int data_t_to_buffer(data_t *data, uint8_t type, char *buffer){
	// TODO
	return 0;
}

int data_constraint_to_buffer(data_constraint_t *data_c, char *msg){
	// TODO
	return 0;
}

/* add struct functions */

int init_data_t(data_t **data, uint8_t type){
	
	*data = (data_t *)malloc(sizeof(data_t));
	if(*data==NULL)
		return -1;

	memset(*data, 0, sizeof(data_t));

	return 0;
}

int set_and_get_next_data_t(data_t **data, uint8_t type, data_t **target){

	int err;

	if(*data==NULL){

		err = init_data_t(data, type);
		if(err)
			return -1;
		
		*target = *data;

		return 0;
	}

	data_t *element = *data;
	while(element->next!=NULL){
		element = element->next;
	}

	init_data_t(&(element->next), type);
	if(err)
		return -1;

	*target = element->next;

	return 0;
}

int add_int_data_t(data_t **data, int int_value){
	int err;
	data_t **target;
	
	err = set_and_get_next_data_t(data, INT_TYPE, target);
	if(err)
		return -1;

	(*target)->value.int_value = int_value; 
	(*target)->next = NULL;

	return 0;
}

int add_str_data_t(data_t **data, uint8_t str_len, char *str){
	int err;
	data_t **target;

	err = set_and_get_next_data_t(data, STRING_TYPE, target);
	if(err)
		return -1;
		
	string_value_t *str_value = &((*target)->value.str_value);

	str_value->str_len = str_len;

	str_value->str = (char *)malloc(str_value->str_len);
	if(str_value->str==NULL){
		destroy_data_t(*target, STRING_TYPE);
		return -1;
	}
	memset(str_value->str, 0, str_value->str_len);
	memcpy(str_value->str, str, str_value->str_len);
	
	return 0;
}

int add_int_range_data_t(data_t **data, int start, int end){
	int err;
	data_t **target;

	err = set_and_get_next_data_t(data, INT_RANGE_TYPE, target);
	if(err)
		return -1;
	
	interval_t *int_range = &((*target)->value.int_range);
	
	int_range->start = start;

	int_range->end = end;
	
	return 0;
}

int set_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data){

	memset(data_c, 0, sizeof(data_constraint_t));

	data_c->type = type;
	data_c->field_len = field_len;
	
	data_c->field = (char *)malloc(data_c->field_len);
	if(data_c->field==NULL){
		free(data_c);
		return -1;
	}

	memset(data_c->field, 0, data_c->field_len);
	memcpy(data_c->field, field, data_c->field_len);

	data_c->data = data;

	data_c->next = NULL;

	return 0;
}

int add_data_constraint(data_constraint_t **data_c, uint8_t type, uint8_t field_len, char *field, data_t *data){
	int err;

	if(*data_c==NULL){
		*data_c = (data_constraint_t *)malloc(sizeof(data_constraint_t));
		if(*data_c==NULL)
			return -1;
		
		return set_data_constraint(*data_c, type, field_len, field, data);
	}

	data_constraint_t *element = *data_c;
	while(element->next!=NULL){
		element = element->next;
	}

	element->next = (data_constraint_t *)malloc(sizeof(data_constraint_t));
	if(element==NULL)
		return -1;

	memset(element->next, 0, sizeof(data_constraint_t));

	return set_data_constraint(element->next, type, field_len, field, data);
}

/* struct destroy functions */

void destroy_data_t(data_t *data, uint8_t type){

	string_value_t *str_value;

	data_t *element = data;
	data_t *previous = element;
	while(element!=NULL){
		switch (type)
		{
			case STRING_TYPE: 

				str_value = &(element->value.str_value);

				if(str_value->str!=NULL)
					free(str_value->str);

				break;

			// other data type without malloc do not need to be freed
		}

		element = element->next;

		free(previous);

		previous = element;
	}
}

void destroy_data_constraint(data_constraint_t *data_c){

	data_constraint_t *element = data_c;
	data_constraint_t *previous = element;
	while(element!=NULL){
		
		if(element->field!=NULL)
			free(element->field);

		destroy_data_t(element->data, element->type);

		element = element->next;

		free(previous);

		previous = element;
	}
}

/* print functions */

void print_data_t(data_t *data, uint8_t type){
	int i = 0;
	data_t *element = data;
	while(element!=NULL){
		printf("	   data %d : ", i);
		switch (type)
		{
			case INT_TYPE:
				printf( "%d\n", element->value.int_value);
				break;
			case STRING_TYPE:
				printf( "%s\n", (element->value.str_value).str);
				break;
			case INT_RANGE_TYPE:
				printf( "%d-%d\n", (element->value.int_range).start, (element->value.int_range).end);
				break;
			default:
				printf( "unkown\n");
		}

		element = element->next;
		i += 1;
	}
}

void print_data_constraint(data_constraint_t *data_c){
	int i = 0;
	data_constraint_t *element = data_c;
	while(element!=NULL){
		printf( "data_constraint %d :\n", i);
		printf( "	type : %d\n", element->type);
		printf( "	field_len : %d\n", element->field_len);
		printf( "	field : %s\n", element->field);

		print_data_t(element->data, element->type);

		element = element->next;
		i += 1;
	}
}