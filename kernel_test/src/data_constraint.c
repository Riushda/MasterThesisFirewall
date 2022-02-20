#include "data_constraint.h"

/* convert buffer to struct functions */

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
		
		memset(field, 0, 100);
		memcpy(field, buffer, field_len);

		buffer += field_len;

		data_t *data = NULL;

		if(type!=SUBJECT_TYPE){

			offset = buffer_to_data_t(buffer, type, &data);
			if(offset < 0){
				destroy_all_data_constraint(*data_c);
				return -1;
			}

			buffer += offset;

		}

		add_data_constraint(data_c, type, field_len, field, data, index);
	}

	return 0;
}

/* convert struct to buffer functions */

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

		if(element->type!=SUBJECT_TYPE){

			offset = data_t_to_buffer(element->data, element->type, &buffer);

			buffer += offset;
		}

		element = element->next;
	}
	
	return 0;
}

/* search for matching struct functions */

data_constraint_t *get_same_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data){

	int condition;

	data_constraint_t *element = data_c;
	while(element!=NULL){

		condition = element->type==type;
		if(condition){
			condition = element->field_len==field_len;
			if(condition){
				condition = memcmp(element->field, field, field_len);
				if(!condition){

					if(type==SUBJECT_TYPE)
						return element;

					condition = contains_data_t(element->data, data, type);
					condition += contains_data_t(data, element->data, type);
					if(!condition) // if element->data contains data and data contains element->data then element->data == data
						return element;
				}
			}
		}	

		element = element->next;
	}

	return NULL;
}

/* add struct functions */

int set_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data, uint16_t index){

	memset(data_c, 0, sizeof(data_constraint_t));

	data_c->type = type;
	data_c->field_len = field_len;
	
	data_c->field = (char *)malloc(data_c->field_len + 1);
	if(data_c->field==NULL){
		free(data_c);
		return -1;
	}

	memset(data_c->field, 0, data_c->field_len + 1);
	memcpy(data_c->field, field, data_c->field_len);

	data_c->data = data;

	memset(data_c->vector, 0, VECTOR_SIZE);
	set_bit_v(data_c->vector, index);

	data_c->next = NULL;

	return 0;
}

int add_data_constraint(data_constraint_t **data_c, uint8_t type, uint8_t field_len, char *field, data_t *data, uint16_t index){

	if(*data_c==NULL){
		*data_c = (data_constraint_t *)malloc(sizeof(data_constraint_t));
		if(*data_c==NULL)
			return -1;
		
		return set_data_constraint(*data_c, type, field_len, field, data, index);
	}

	data_constraint_t *same = get_same_data_constraint(*data_c, type, field_len, field, data);

	if(same!=NULL){
		set_bit_v(same->vector, index);
		destroy_data_t(data, type);
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

/* struct destroy functions */

int remove_data_constraint(data_constraint_t **data_c, uint16_t index){
	data_constraint_t *to_remove;
	int zero = 0;

	data_constraint_t *element = *data_c;
	data_constraint_t *previous = element;
	while(element!=NULL){

		if(is_set_v(element->vector, index)){
			unset_shift_v(element->vector, index);
		}

		if(!memcmp(element->vector, &zero, sizeof(VECTOR_SIZE))){

			to_remove = element;

			element = element->next;

			previous->next = element;

			if(to_remove==*data_c)
				*data_c = element;

			if(to_remove->field!=NULL)
				free(to_remove->field);

			destroy_data_t(to_remove->data, to_remove->type);

			free(to_remove);
		}
		else{

			previous = element;

			element = element->next;
		}
	}
	return 0;
}

void destroy_all_data_constraint(data_constraint_t *data_c){

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

void print_data_constraint(data_constraint_t *data_c){
	int i = 0;
	data_constraint_t *element = data_c;
	while(element!=NULL){
		printf("data_constraint %d :\n", i);

		printf("	type : ");
		switch(element->type)
		{	
			case SUBJECT_TYPE:
				printf("SUBJECT\n");
				break;
			case INT_TYPE:
				printf("INT\n");
				break;
			case STRING_TYPE:
				printf("STRING\n");
				break;
			case INT_RANGE_TYPE:
				printf("INT_RANGE\n");
				break;
			default:
				printf("UNKOWN\n");
		}

		printf("	field_len : %d\n", element->field_len);
		printf("	field : %s\n", element->field);

		print_data_t(element->data, element->type);

		printf(" 	vector : %d\n", *(element->vector));

		element = element->next;
		i += 1;
	}
}