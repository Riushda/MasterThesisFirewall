#include "data.h"

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
				
				add_data_t(data, INT_TYPE, 0, NULL, buffer);
				buffer += sizeof(int);
				offset += sizeof(int);

				break;
			case STRING_TYPE:

				add_data_t(data, STRING_TYPE, 0, NULL, buffer);
				buffer += sizeof(uint8_t) + str_len;
				offset += sizeof(uint8_t) + str_len;

				break;
			case INT_RANGE_TYPE:

				add_data_t(data, INT_RANGE_TYPE, 0, NULL, buffer);
				buffer += sizeof(int)*2;
				offset += sizeof(int)*2;
				
				break;
			default:
				// data type not known
				destroy_data_t(*data, type);
				return -1;
		}
	}

	return offset;
}

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

int init_data_t(data_t **data, uint8_t type){
	
	*data = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
	if(*data==NULL)
		return -1;

	memset(*data, 0, sizeof(data_t));

	return 0;
}

int set_data_t(data_t **data, int type, uint8_t field_len, char *field, void *value){

	data_t *element = *data;
	
	memset(element, 0, sizeof(data_t));

	element->type = type;
	
	element->field_len = field_len;

	if(field_len>0 && field!=NULL){

		element->field = (char *)kmalloc(field_len + 1, GFP_KERNEL);

		if(element->field == NULL){
			destroy_data_t(element, INT_TYPE);
			return -1;
		}

		memset(element->field, 0, field_len + 1);
		memcpy(element->field, field, field_len);
	}

	switch (type)
	{
		case INT_TYPE:

			memcpy(&((element->value).int_value) , value, sizeof(int)); 

			break;
		case STRING_TYPE:

			string_value_t *str_value = &(element->value.str_value);

			memcpy(&(str_value->str_len), value, 1);

			str_value->str = (char *)kmalloc(str_value->str_len + 1, GFP_KERNEL);
			if(str_value->str==NULL){
				destroy_data_t(element, STRING_TYPE);
				return -1;
			}
			memset(str_value->str, 0, str_value->str_len + 1);
			memcpy(str_value->str, value + 1, str_value->str_len);
		
			break;
		case INT_RANGE_TYPE:

			memcpy(&((element->value).int_range.start), value, sizeof(int));
			memcpy(&((element->value).int_range.end), value + sizeof(int), sizeof(int));  
		
			break;
		
		default:
			break;
	}

	element->next = NULL;

	return 0;
}

int add_data_t(data_t **data, int type, uint8_t field_len, char *field, void *value){

	int err;

	if(*data==NULL){

		err = init_data_t(data, type);
		if(err)
			return -1;

		return set_data_t(data, type, field_len, field, value);
	}

	data_t *element = *data;
	while(element->next!=NULL){
		element = element->next;
	}

	err = init_data_t(&(element->next), type);
	if(err)
		return -1;

	return set_data_t(&(element->next), type, field_len, field, value);
}

// check if dst contains src, if all values of src are in dst
int contains_data_t(data_t *src, data_t *dst, uint8_t type){

	int condition;

	// check if at least one element
	data_t *element_src = src;
	data_t *element_dst = dst;
	while(element_src!=NULL){
		condition = 1;
		while(element_dst!=NULL){

			switch (type)
			{
				case INT_TYPE:
					condition = (element_src->value).int_value != (element_dst->value).int_value;
					break;
				case STRING_TYPE:
					condition = (element_src->value).str_value.str_len != (element_dst->value).str_value.str_len;
					if(!condition)
						condition = memcmp((element_src->value).str_value.str, (element_dst->value).str_value.str, (element_dst->value).str_value.str_len);
					break;
				case INT_RANGE_TYPE:
					condition = (element_src->value).int_range.start != (element_dst->value).int_range.start;
					condition += (element_src->value).int_range.end != (element_dst->value).int_range.end;
					break;
			}

			// if condition==0 then we found an element in dst that match the current element of src	
			if(!condition)
				break;

			element_dst = element_dst->next;
		}
		
		// if condition is positive, then no element in dst match the current element of src
		if(condition)
			return -1;

		element_src = element_src->next;
	}

	return 0;
}

void destroy_data_t(data_t *data, uint8_t type){

	string_value_t *str_value;

	data_t *element = data;
	data_t *previous = element;
	while(element!=NULL){
		
		if(element->field_len > 0 && element->field!=NULL)
			kfree(element->field);

		switch (type)
		{
			case STRING_TYPE: 

				str_value = &(element->value.str_value);

				if(str_value->str!=NULL)
					kfree(str_value->str);

				break;

			// other data type without kmalloc do not need to be freed
		}

		element = element->next;

		kfree(previous);

		previous = element;
	}
}

void print_data_t(data_t *data, uint8_t type){
	int i = 0;
	data_t *element = data;
	while(element!=NULL){

		if(element->field_len > 0 && element->field!=NULL){
			printk(KERN_INFO "	   %s : ", element->field);
		}
		else{
			printk(KERN_INFO "	   data %d : ", i);
		}

		switch (type)
		{
			case INT_TYPE:
				printk(KERN_CONT "%d\n", element->value.int_value);
				break;
			case STRING_TYPE:
				printk(KERN_CONT "%s\n", (element->value.str_value).str);
				break;
			case INT_RANGE_TYPE:
				printk(KERN_CONT "%d-%d\n", (element->value.int_range).start, (element->value.int_range).end);
				break;
			default:
				printk(KERN_CONT "unkown\n");
		}

		element = element->next;
		i += 1;
	}
}