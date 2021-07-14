import argparse
import ast


def parse_list_arg(*possible_types):
	types_dict = {}
	if not isinstance(possible_types[0], (tuple, list)):
		types_dict[len(possible_types)] = possible_types
	else:
		for i in possible_types:
			types_dict[len(i)] = i

	def str_to_tuple(s):
		user_input_str = ast.literal_eval(s)

		if not any(len(user_input_str) == k for k in types_dict.keys()):
			raise argparse.ArgumentTypeError(f"provide {' or '.join(str(i) for i in types_dict.keys())} arguments! See --help for details.")
		else:
			types = types_dict[len(user_input_str)]

		return [type_to_convert(usr_input_val)
				for type_to_convert, usr_input_val
				in zip(types, user_input_str)]

	return str_to_tuple
