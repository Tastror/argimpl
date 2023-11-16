import os
import sys

sys.path.append("../..")
sys.path.append("..")

prefix = "."
if not os.path.exists(f"{prefix}/template_core.json"):
    prefix = ".."

from argimpl import ArgImpl

core_dict = {
    "age": 10,
    "name": "John",
    "fruits": ["apple", "banana", "orange"],
    "pre_class": 1,
    "happy": False
}
impl_dict = {
    "name": "$$",
    "age": "$$",
    "favourite_fruit": "$! $fruits$[0] + '_and_' + $fruits$[1]",
    "class": "$! ($pre_class$ + 1) * 2",
    "happy": "$! !$$"
}


print("\nExample 1\n")
arg_impl = ArgImpl()
arg_impl.load_dict_and_parse(core_dict, impl_dict)
print(arg_impl.full_dict)
print(arg_impl.full_command(show_true_false=True))
print(arg_impl.full_command("echo"))


print("\nExample 2\n")
arg_impl = ArgImpl()
arg_impl.load_json_and_parse(
    core_dicts_path=f"{prefix}/template_core.json",
    core_choosen_key="foo1",
    impl_dicts_path=f"{prefix}/template_impl.json",
    impl_choosen_key="bar1"
)
print(arg_impl.full_dict)
print(arg_impl.full_command())


print("\nExample 3\n")
arg_impl = ArgImpl()

try:
    arg_impl.parse()
except SyntaxError as e:
    print("an error example:", e)

arg_impl.load_json_and_parse(
    core_dicts_path=f"{prefix}/template_core.json",
    core_choosen_key="foo2",
    impl_dicts_path=f"{prefix}/template_impl.json",
    impl_choosen_key="bar2"
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
