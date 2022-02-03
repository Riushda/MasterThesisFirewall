#include "data_constraint.h"

void destroy_data_t(data_t *data, uint8_t type){

	string_value_t *str_value;

	data_t *element = data;
	data_t *previous = element;
	while(element!=NULL){
		switch (type)
		{
			case STRING_TYPE: 

				str_value = &((element->value_t).str_value);

				if(str_value->str!=NULL)
					kfree(str_value->str);

				break;
			default:
				printk(KERN_INFO "data type without kmalloc\n");
		}

		element = element->next;

		kfree(previous);

		previous = element;
	}
}

int buffer_to_data_t(data_t *data, uint8_t type, char *buffer){
	string_value_t *str_value;
	interval_t *int_range;
	data_t *element;
	int i;

	uint8_t n_value = (uint8_t) *buffer;

	data = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
	if(data==NULL)
		return -1;

	memset(data, 0, sizeof(data_t));

	element = data;
	
	for(i=0; i<n_value; i++){

		switch (type)
		{
			case INT_TYPE:
			
				(element->value_t).int_value = *buffer;

				buffer += sizeof(int);

				break;
			case STRING_TYPE:

				str_value = &((element->value_t).str_value);

				str_value->str_len = (uint8_t) *buffer;
				buffer += sizeof(uint8_t);

				str_value->str = (char *)kmalloc(str_value->str_len, GFP_KERNEL);
				if(str_value->str==NULL){
					destroy_data_t(data, type);
					return -1;
				}
				memset(str_value->str, 0, str_value->str_len);
				memcpy(str_value->str, buffer, str_value->str_len);

				buffer += str_value->str_len;

				break;
			case INT_RANGE:

				int_range = &((element->value_t).int_range);
				
				memcpy(&(int_range->start), buffer, sizeof(int));

				buffer += sizeof(int);

				memcpy(&(int_range->end), buffer, sizeof(int));

				buffer += sizeof(int);
				
				break;
			default:
				printk(KERN_INFO "data type not know\n");
				destroy_data_t(data, type);
				return -1;
		}

		if(i<n_value-1){
			element->next = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
			if(element==NULL)
				return -1;

			memset(element, 0, sizeof(data_t));
		}

		element = element->next;
	}

	return 0;
}

void destroy_data_constraint(data_constraint_t *data_c){

	data_constraint_t *element = data_c;
	data_constraint_t *previous = element;
	while(element!=NULL){
		
		if(element->field!=NULL)
			kfree(element->field);

		destroy_data_t(element->data, element->type);

		element = element->next;

		kfree(previous);

		previous = element;
	}
}

int buffer_to_data_constraint(data_constraint_t *data_c, char *msg){
	int err;
	int i;
	data_constraint_t *element;
	char *buffer = msg;

	uint8_t n_constraint = (uint8_t) *buffer;
	buffer += 1;

	data_c = (data_constraint_t *)kmalloc(sizeof(data_constraint_t), GFP_KERNEL);
	if(data_c==NULL)
		return -1;

	memset(data_c, 0, sizeof(data_constraint_t));

	element = data_c;
	for(i=0; i<n_constraint; i++){

		element->type = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);

		element->field_len = (uint8_t) *buffer;
		buffer += sizeof(uint8_t);

		element->field = (char *)kmalloc(element->field_len, GFP_KERNEL);
		if(element->field==NULL){
			destroy_data_constraint(data_c);
			return -1;
		}
		
		memset(element->field, 0, element->field_len);
		memcpy(element->field, buffer, element->field_len);

		buffer += element->field_len;

		element->data = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
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
			element->next = (data_constraint_t *)kmalloc(sizeof(data_constraint_t), GFP_KERNEL);
			if(element==NULL)
				return -1;

			memset(element, 0, sizeof(data_constraint_t));
		}

		element = element->next;
	}

	return 0;
}

data_t* set_and_get_next_data_t(data_t *data){

	if(data==NULL){

		data = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
		if(data==NULL)
			return NULL;

		memset(data, 0, sizeof(data_t));
		
		return data;
	}

	data_t *element = data;
	while(element->next!=NULL){
		element = element->next;
	}

	element->next = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
	if(element==NULL)
		return NULL;

	memset(element->next, 0, sizeof(data_t));
	element = element->next;

	return element;
}

int add_int_data_t(data_t *data, int int_value){
	data_t *current_data = set_and_get_next_data_t(data);
	if(current_data==NULL)
		return -1;

	(data->value_t).int_value = int_value;
	data->next = NULL;

	return 0;
}

int add_str_data_t(data_t *data, uint8_t str_len, char *str){
	data_t *current_data = set_and_get_next_data_t(data);
	if(current_data==NULL)
		return -1;
		
	string_value_t *str_value = &((current_data->value_t).str_value);

	str_value->str_len = str_len;

	str_value->str = (char *)kmalloc(str_value->str_len, GFP_KERNEL);
	if(str_value->str==NULL){
		destroy_data_t(data, STRING_TYPE);
		return -1;
	}
	memset(str_value->str, 0, str_value->str_len);
	memcpy(str_value->str, str, str_value->str_len);
	
	return 0;
}

int add_int_range_data_t(data_t *data, int start, int end){
	data_t *current_data = set_and_get_next_data_t(data);
	if(current_data==NULL)
		return -1;
	
	interval_t *int_range = &((data->value_t).int_range);
	
	int_range->start = start;

	int_range->end = end;
	
	return 0;
}

void print_data_t(data_t *data, uint8_t type){
	int i = 0;
	data_t *element = data;
	while(element!=NULL){
		printk(KERN_CONT "	data %d : ", i);
		switch (type)
		{
			case INT_TYPE:
				printk(KERN_INFO "%d\n", element->value_t.int_value);
				break;
			case STRING_TYPE:
				printk(KERN_INFO "%s\n", element->value_t.str_value.str);
				break;
			case INT_RANGE:
				printk(KERN_INFO "%d-%d\n", element->value_t.int_range.start, element->value_t.int_range.end);
				break;
			default:
				printk(KERN_INFO "unkown\n");
		}

		element = element->next;
		i += 1;
	}
}

void print_data_constraint(data_constraint_t *data_c){
	int i = 0;
	data_constraint_t *element = data_c;
	while(element!=NULL){
		printk(KERN_INFO "data_constraint %d :\n", i);
		printk(KERN_INFO "	type : %d\n", element->type);
		printk(KERN_INFO "	field_len : %d\n", element->field_len);
		printk(KERN_INFO "	field : %s\n", element->field);

		print_data_t(element->data, element->type);

		element = element->next;
		i += 1;
	}
}