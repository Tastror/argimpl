# arg_impl

## Usage

You have 2 dicts,

```python
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
```

and you want to get a full dict, using both the *data* of `core` and the *shape* of `impl`.

ArgImpl can help you with it. After running ArgImpl.load_dict(),

```python
from arg_impl.arg_impl import ArgImpl

arg_impl = ArgImpl()
arg_impl.load_dict(core_arg_dict, arg_impl_dict)
```

you can get the result such as

```python
arg_impl.full_arg_dict == {
    "name": "John",
    "age": 10,
    "favourite_fruit": "apple",
    "class": 1,
    "human": True
}

arg_impl.full_command() == \
    "--name=John --age=10 --favourite_fruit=apple --class=1 --human=true"

arg_impl.full_command("foo") == \
    "foo --name=John --age=10 --favourite_fruit=apple --class=1 --human=true"
```

Very nice, right?

Refer to `template_arg_impl.json` to see more about how to write the `impl`.
