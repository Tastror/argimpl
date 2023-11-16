# argimpl

## Usage

You have 2 dicts,

```python
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
```

and you want to get a full dict, using both the *data* of `core` and the *shape* of `impl`.

ArgImpl can help you with it. After running ArgImpl.load_core/impl_dict(),

```python
from argimpl import ArgImpl

impl = ArgImpl()
impl.load_core_dict(core_dict)
impl.load_impl_dict(impl_dict)
impl.parse()  # if not here, it will parse when use .full_dict or .full_commad()
```

you can get the result such as

```python
impl.full_dict == {
    "name": "John",
    "age": 10,
    "favourite_fruit": "apple_and_banana",
    "class": 4,
    "happy": True
}

impl.full_command(show_true_false=True) == \
    "--name=John --age=10 --favourite_fruit=apple_and_banana --class=4 --happy=true"

impl.full_command(start="echo") == \
    "echo --name=John --age=10 --favourite_fruit=apple_and_banana --class=4 --happy"
```

Very nice, right?

Refer to `doc` in `template_impl.json` to see more about how to write the `impl`.
