from arg_impl import ArgImpl

core_arg_dict = {
    "age": 10,
    "name": "John",
    "fruits": ["apple", "banana", "orange"],
    "human": True,
    "useless_data": "foo"
}
arg_impl_dict = {
    "name": "$$",
    "age": "$$",
    "favourite_fruit": "$!$fruits$[0]",
    "class": 1,
    "human": "$$"
}

# dict, dict
arg_impl = ArgImpl()
arg_impl.load_dict(
    core_arg_dict = core_arg_dict,
    arg_impl_dict = arg_impl_dict
)
print(arg_impl.full_dict)
print(arg_impl.full_command("echo"))

# dict, json
arg_impl = ArgImpl()
arg_impl.load_json(
    core_arg_dict = core_arg_dict,
    arg_impl_json_path="./template_arg_impl.json",
    arg_impl_type_key="school_impl"
)
print(arg_impl.full_dict)
print(arg_impl.full_command())

# dict, json
arg_impl = ArgImpl()
arg_impl.load_json(
    core_arg_dict = core_arg_dict,
    arg_impl_json_path="./template_arg_impl.json",
    arg_impl_type_key="test_impl"
)

# $? (MustChange) value must be updated before getting the .full_xxx
try:
    print(arg_impl.full_dict)
except ValueError as e:
    print("an error example:", e)
arg_impl.update_from_mustchange("?", 123)

# non-MustChange value cannot be updated this way
try:
    arg_impl.update_from_mustchange("?", 456)
except ValueError as e:
    print("an error example:", e)

print(arg_impl.full_dict)
print(arg_impl.full_command("echo"))
