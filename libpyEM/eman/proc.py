import argparse


def parse_list_arg(*possible_types):
	"""Return a function that can be passed to argparse.add_argument() as an argument to 'type'.

	>>> parse_list_arg(int,float)("3, 4")
	[3, 4.0]
	>>> parse_list_arg(int,int)("3, 4")
	[3, 4]
	>>> parse_list_arg([int,int],[int,int,int])("3,4,5")
	[3, 4, 5]
	>>> parse_list_arg([int,int],[int,int,int])("3,4")
	[3, 4]
	>>> parse_list_arg([int,str],[int,int,int])("3,4")
	[3, '4']
	>>> parse_list_arg([int,str],[int,int,int])("3,4,5")
	[3, 4, 5]
	>>> parse_list_arg([int],[int,int],[int,int,int])("3,4")
	[3, 4]
	>>> parse_list_arg([int],[int,int],[int,int,int])("3")
	[3]
	"""

	types_dict = {}
	print("possible_types: ", possible_types)
	if not isinstance(possible_types[0], (tuple, list)):
		types_dict[len(possible_types)] = possible_types
	else:
		for i in possible_types:
			types_dict[len(i)] = i

	def str_to_tuple(s):
		user_input_str = s.split(',')
		print("user_input_str: ", user_input_str)

		if not any(len(user_input_str) == k for k in types_dict.keys()):
			raise argparse.ArgumentTypeError(f"provide {' or '.join(str(i) for i in types_dict.keys())} arguments! See --help for details.")
		else:
			types = types_dict[len(user_input_str)]

		print("types: ", types)
		return [type_to_convert(usr_input_val)
				for type_to_convert, usr_input_val
				in zip(types, user_input_str)]

	return str_to_tuple


if __name__ == "__main__":
	import doctest
	doctest.testmod()
