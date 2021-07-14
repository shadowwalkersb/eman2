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
		print('Not list, not tuple')
		types_dict[len(possible_types)] = possible_types
	else:
		for i in possible_types:
			types_dict[len(i)] = i
	# print(type(possible_types))
	# print(type(possible_types[0]))
	# print(possible_types)
	print("LEN: ", len(possible_types))
	print("WWW")
	print(types_dict)
	# sys.exit(0)

	def str_to_tuple(s):
		user_input_str = s.split(',')
		print("user_input_str: ", user_input_str)

		# for item in possible_types:
		# 	print("item: ", item)
		# print(possible_types[0])
		# print(possible_types)
		# print("LEN: ", len(possible_types))

		# print("ANY: ", [len(user_input_str) == len(i) for i in possible_types])
		lengths = types_dict.keys()
		print("lens; ", lengths)
		print([k for k in lengths])
		# import pdb;pdb.set_trace()

		if not any(len(user_input_str) == k for k in lengths):
			comma = ' or '
			msg = f"provide {' or '.join(str(i) for i in types_dict.keys())} arguments! See --help for details."
			print("msg: ", msg)
			raise argparse.ArgumentTypeError(msg)
		else:
			types = types_dict[len(user_input_str)]

		print("types: ", types)
		print("NO")
		result = [type_to_convert(usr_input_val)
				for type_to_convert, usr_input_val
				in zip(types, user_input_str)]

		print('result: ', result)

		return result

	return str_to_tuple


if __name__ == "__main__":
	import doctest
	doctest.testmod()
