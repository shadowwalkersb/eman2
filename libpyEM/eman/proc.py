import argparse
import ast


def parse_list_arg(*possible_types):
	if not isinstance(possible_types[0], (tuple, list)):
		possible_types = (possible_types,)

	def str_to_tuple(s):
		user_input_str = ast.literal_eval(s)

		if not any(len(user_input_str) == len(i) for i in possible_types):
			raise argparse.ArgumentTypeError("provide 2 or 4 arguments!")

		return [type_to_convert(usr_input_val)
				for type_to_convert, usr_input_val
				in zip(possible_types, user_input_str)]

	return str_to_tuple
