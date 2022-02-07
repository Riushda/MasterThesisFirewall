#include "data_constraint.h"

/* convert buffer to struct functions */

int buffer_to_data_t(char *buf, uint8_t type, data_t **data){
	data_t *element;
	int i;

	int int_value;
	uint8_t str_len;
	int start;
	int end;

	char *buffer = buf;
	int offset = 0;

	uint8_t n_value = (uint8_t) *buffer;
	buffer += sizeof(uint8_t);
	offset += sizeof(uint8_t);
	
	for(i=0; i<n_value; i++){

		switch (type)
		{
			case INT_TYPE:
			
				memset(&int_value, 0, sizeof(int));
				memcpy(&int_value, buffer, sizeof(int));

				add_int_data_t(data, int_value);
				buffer += sizeof(int);
				offset += sizeof(int);

				break;
			case STRING_TYPE:
				str_len = (uint8_t) *buffer;
				buffer += sizeof(uint8_t);
				offset += sizeof(uint8_t);

				add_str_data_t(data, str_len, buffer);
				buffer += str_len;
				offset += str_len;

				break;
			case INT_RANGE_TYPE:
				memset(&start, 0, sizeof(int));
				memcpy(&start, buffer, sizeof(int));

				buffer += sizeof(int);
				offset += sizeof(int);

				memset(&end, 0, sizeof(int));
				memcpy(&end, buffer, sizeof(int));

				buffer += sizeof(int);
				offset += sizeof(int);

				add_int_range_data_t(data, start, end);
				
				break;
			default:
				// data type not known
				destroy_data_t(*data, type);
				return -1;
		}
	}

	return offset;
}

int buffer_to_data_constraint(char *buf, uint16_t index, data_constraint_t **data_c){
	int offset;
	int i;
	char field[100];

	uint8_t type;
	uint8_t field_len;

	char *buffer = buf;

	uint8_t n_constraint = (uint8_t) *buffer;
	buffer += sizeof(uint8_t);

	for(i=0; i<n_constraint; i++){

		type = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);

		field_len = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);
		
		memset(field, 0, field_len);
		memcpy(field, buffer, field_len);

		buffer += field_len;

		data_t *data = NULL;

		offset = buffer_to_data_t(buffer, type, &data);
		if(offset<0){
			destroy_data_constraint(*data_c);
			return -1;
		}

		buffer += offset;

		add_data_constraint(data_c, type, field_len, field, data, index);
	}

	return 0;
}

/* convert struct to buffer functions */

int data_t_to_buffer(data_t *data, uint8_t type, char **buf){

	char *buffer = *buf;
	int offset = 0;
	data_t *element = data;

	uint8_t n_value = 0;

	while(element!=NULL){
		n_value += 1;
		element = element->next;
	}

	memcpy(buffer, &n_value, sizeof(uint8_t));
	buffer += sizeof(uint8_t);
	offset += sizeof(uint8_t);

	element = data;
	while(element!=NULL){

		switch (type)
		{
			case INT_TYPE:
				memcpy(buffer, &(element->value.int_value), sizeof(uint8_t));
				buffer += sizeof(int);
				offset += sizeof(int);

				break;
			case STRING_TYPE:
				memcpy(buffer, &((element->value).str_value.str_len), sizeof(uint8_t));
				buffer += sizeof(uint8_t);
				offset += sizeof(uint8_t);

				memcpy(buffer, (element->value).str_value.str, (element->value).str_value.str_len);
				buffer += (element->value).str_value.str_len;
				offset += (element->value).str_value.str_len;

				break;
			case INT_RANGE_TYPE:
				memcpy(buffer, &((element->value).int_range.start), sizeof(int));
				buffer += sizeof(int);
				memcpy(buffer, &((element->value).int_range.end), sizeof(int));
				buffer += sizeof(int);
				offset += sizeof(int)*2;
		}

		element = element->next;
	}
	
	return offset;
}

// destination buffer considered as already initialized (buf[1024] for instance)
int data_constraint_to_buffer(data_constraint_t *data_c, char **buf){
	char *buffer = *buf;
	int offset;
	data_constraint_t *element = data_c;

	uint8_t n_constraint = 0;

	while(element!=NULL){
		n_constraint += 1;
		element = element->next;
	}

	memcpy(buffer, &n_constraint, sizeof(uint8_t));
	buffer += sizeof(uint8_t);

	element = data_c;
	while(element!=NULL){

		memcpy(buffer, &(element->type), sizeof(uint8_t));
		buffer += sizeof(uint8_t);

		memcpy(buffer, &(element->field_len), sizeof(uint8_t));
		buffer += sizeof(uint8_t);

		memcpy(buffer, element->field, element->field_len);
		buffer += element->field_len;

		offset = data_t_to_buffer(element->data, element->type, &buffer);

		buffer += offset;

		element = element->next;
	}
	
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
	data_t **target = (data_t **)malloc(sizeof(data_t *));
	if(target==NULL)
		return -1;

	err = set_and_get_next_data_t(data, INT_TYPE, target);
	if(err){
		free(target);
		return -1;
	}

	(*target)->value.int_value = int_value; 
	(*target)->next = NULL;

	free(target);

	return 0;
}

int add_str_data_t(data_t **data, uint8_t str_len, char *str){
	int err;
	data_t **target = (data_t **)malloc(sizeof(data_t *));
	if(target==NULL)
		return -1;

	err = set_and_get_next_data_t(data, STRING_TYPE, target);
	if(err){
		free(target);
		return -1;
	}
		
	string_value_t *str_value = &((*target)->value.str_value);

	str_value->str_len = str_len;

	str_value->str = (char *)malloc(str_value->str_len);
	if(str_value->str==NULL){
		free(target);
		destroy_data_t(*target, STRING_TYPE);
		return -1;
	}
	memset(str_value->str, 0, str_value->str_len);
	memcpy(str_value->str, str, str_value->str_len);

	free(target);
	
	return 0;
}

int add_int_range_data_t(data_t **data, int start, int end){
	int err;
	data_t **target = (data_t **)malloc(sizeof(data_t *));
	if(target==NULL)
		return -1;

	err = set_and_get_next_data_t(data, INT_RANGE_TYPE, target);
	if(err){
		free(target);
		return -1;
	}
	
	interval_t *int_range = &((*target)->value.int_range);
	
	int_range->start = start;

	int_range->end = end;

	free(target);
	
	return 0;
}

int set_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data, uint16_t index){

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

	memset(data_c->vector, 0, VECTOR_SIZE);
	set_bit_v(data_c->vector, index);

	data_c->next = NULL;

	return 0;
}

int add_data_constraint(data_constraint_t **data_c, uint8_t type, uint8_t field_len, char *field, data_t *data, uint16_t index){
	int err;

	if(*data_c==NULL){
		*data_c = (data_constraint_t *)malloc(sizeof(data_constraint_t));
		if(*data_c==NULL)
			return -1;
		
		return set_data_constraint(*data_c, type, field_len, field, data, index);
	}

	vector_t match = match_data_constraint(element, type, field_len, field, data);

	if(!match){ // verify that it works to put char in if
		set_bit_v(element->vector, index);
		destroy_data_t(data);
		return 0;
	}

	// if no existing constraint match, then add a new one

	data_constraint_t *element = *data_c;
	while(element->next!=NULL){
		element = element->next;
	}

	element->next = (data_constraint_t *)malloc(sizeof(data_constraint_t));
	if(element==NULL)
		return -1;

	memset(element->next, 0, sizeof(data_constraint_t));

	return set_data_constraint(element->next, type, field_len, field, data, index);
}

/* search for matching struct functions */

int match_data_t(data_t *src, data_t *dst){

	data_constraint_t *element = data_c;
	while(element->next!=NULL){

	

		if(!condition)
			return element->vector;

		element = element->next;
	}

	return 0;
}

vector_t match_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data){

	int condition;

	data_constraint_t *element = data_c;
	while(element->next!=NULL){

		condition = data_c->type!=type;
		if(!condition){
			condition += data_c->field_len!=field_len;
			condition += memcmp(data_c->field, field, field_len);
			condition += match_data_t(element->data, data);
		}

		if(!condition)
			return element->vector;

		element = element->next;
	}

	return 0;
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