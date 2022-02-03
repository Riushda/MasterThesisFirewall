#include "data_constraint.h"

int create_data_t(data_t *data, char *buffer){

}

int destroy_data_t(data_t *data){

}

int destroy_data_constraint(data_constraint_t *data_c){

}

int create_data_constraint(data_constraint_t *data_c, char *msg){
	char *buffer = msg;

	uint8_t n_constraint = (uint8_t) *buffer;
	buffer += 1;

	data_c = (data_constraint_t *)kmalloc(sizeof(data_constraint_t), GFP_KERNEL);
	if(data_c==NULL)
		return -1;

	memset(data_c, 0, sizeof(data_constraint_t));

	data_constraint_t *current = data_c;
	for(int i=0; i<n_constraint; i++){

		current->type = (uint8_t) *buffer;
		buffer += 1;

		current->field = (uint8_t) *buffer;
		buffer += 1;

		current->field = (char *)kmalloc(data_c->field_len, GFP_KERNEL);
		if(current->field==NULL){
			destroy_data_constraint(data_c);
			return -1;
		}
		
		memset(current->field, 0, current->field_len);
		memcpy(current->field, buffer, current->field_len);

		buffer += field_len;

		field->data = (data_t *)kmalloc(sizeof(data_t), GFP_KERNEL);
		if(field->data==NULL){
			destroy_data_constraint(data_c);
			return -1;
		}

		int err = create_data_t(&field->data, buffer);
		if(err){
			destroy_data_constraint(data_c);
			return -1;
		}


		if(i<n_constraint-1){
			current->next = (data_constraint_t *)kmalloc(sizeof(data_constraint_t), GFP_KERNEL);
			if(current==NULL)
				return -1;

			memset(current, 0, sizeof(data_constraint_t));
		}
	}

	return 0;
}

