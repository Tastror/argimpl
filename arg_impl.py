import os
import json
from copy import deepcopy
from pathlib import Path
from typing import Optional, Union, Any

from ArgImpl.safe_parse import safe_eval


class ArgImpl:


    class Empty:
        pass


    class MustChange:
        pass


    def __init__(self) -> None:
        """Use `impl_dict` to implement `core_dict` into a `full_dict`, and form execute command

        Arguments:

            No Arguments. After init, please use `.load_core_dict/json()` and `.load_impl_dict/json()` first.

        Typical usage example:

            core_dict: core dict which provide original data
            impl_dict: implement dict which provide generate command and new data

            1. normal example

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

            after load_dict, the result will be

            ```python
            impl = ArgImpl()
            impl.load_core_dict(core_dict)
            impl.load_impl_dict(impl_dict)
            impl.parse()
            impl.full_dict == {
                "name": "John",
                "age": 10,
                "favourite_fruit": "apple_and_banana",
                "class": 4,
                "happy": True
            }
            impl.full_command(show_true_false=True) == \\
                "--name=John --age=10 --favourite_fruit=apple_and_banana --class=4 --happy=true"
            impl.full_command(start="echo") == \\
                "echo --name=John --age=10 --favourite_fruit=apple_and_banana --class=4 --happy"
            ```

            2. json example

            in `./impl.json`

            ```json
            {
                "A": {
                    "name": "$$",
                    "age": "$$",
                    "favourite_fruit": "$!$fruits$[0]",
                    "class": 1
                },
                "B": {
                    "name": "$$ Williams",
                    "age": "$!$$+25"
                }
            }
            ```

            and use the following to load instead

            ```python
            impl.load_impl_json("./impl.json", "A")
            ```

            similar for `.load_core_json()`
        """

        self.core_dict = {}
        self.impl_dict = {}
        self._full_dict = {}
        self._core_loaded = False
        self._impl_loaded = False
        self._parsed = False


    def load_core_dict(self, core_dict: dict) -> None:
        self.core_dict = deepcopy(core_dict)
        self._parsed = False
        self._core_loaded = True


    def load_impl_dict(self, impl_dict: dict) -> None:
        self.impl_dict = deepcopy(impl_dict)
        self._parsed = False
        self._impl_loaded = True


    def load_core_json(self, core_dicts_path: Union[str, Path], core_choosen_key: str) -> None:

        if not os.path.exists(core_dicts_path):
            raise ValueError(f"core_dicts_path `{core_dicts_path}` does not exist")

        with open(core_dicts_path) as f:
            all_dicts: dict = json.load(f)
            if type(all_dicts) is not dict:
                raise ValueError(f"core_dicts_path `{core_dicts_path}` is not a valid json dict")

        self.core_dict = all_dicts.get(core_choosen_key, self.Empty())
        if type(self.core_dict) is self.Empty:
            raise ValueError(f"core_choosen_key `{core_choosen_key}` does not exist")

        self._parsed = False
        self._core_loaded = True


    def load_impl_json(self, impl_dicts_path: Union[str, Path], impl_choosen_key: str) -> None:

        if not os.path.exists(impl_dicts_path):
            raise ValueError(f"impl_dicts_path `{impl_dicts_path}` does not exist")

        with open(impl_dicts_path) as f:
            all_dicts: dict = json.load(f)
            if type(all_dicts) is not dict:
                raise ValueError(f"impl_dicts_path `{impl_dicts_path}` is not a valid dict")

        self.impl_dict = all_dicts.get(impl_choosen_key, self.Empty())
        if type(self.impl_dict) is self.Empty:
            raise ValueError(f"impl_choosen_key `{impl_choosen_key}` does not exist")

        self._parsed = False
        self._impl_loaded = True


    def load_dict_and_parse(self, core_dict: dict, impl_dict: dict) -> None:
        self.load_core_dict(core_dict)
        self.load_impl_dict(impl_dict)
        self.parse()


    def load_json_and_parse(
        self,
        core_dicts_path: Union[str, Path], core_choosen_key: str,
        impl_dicts_path: Union[str, Path], impl_choosen_key: str
    ) -> None:
        self.load_core_json(core_dicts_path, core_choosen_key)
        self.load_impl_json(impl_dicts_path, impl_choosen_key)
        self.parse()


    def parse(self):

        if self._parsed: return
        self._parsed = True

        if not self._core_loaded:
            raise SyntaxError("must load core before parsing")

        if not self._impl_loaded:
            raise SyntaxError("must load impl before parsing")


        def search_and_change(input_data: Union[str, Any], refer_dict: dict) -> Union[str, Any]:

            # keep the original type (not must be string) if data is Empty
            def assign_or_append(data, value):
                if type(data) is self.Empty:
                    return value
                else:
                    return str(data) + str(value)

            output_data = self.Empty()

            i = 0
            inlen = len(input_data)
            searching_for_end = False
            buff = ""
            while i < inlen:
                # escape
                if input_data[i] == "\\":
                    if i + 1 < inlen and input_data[i + 1] in ["$", "\\"]:
                        if searching_for_end:
                            buff += input_data[i + 1]
                        else:
                            output_data = assign_or_append(output_data, input_data[i + 1])
                        i += 1
                    else:
                        if searching_for_end:
                            buff += "\\"  # non-escaping \\ or last \\
                        else:
                            output_data = assign_or_append(output_data, "\\")
                elif searching_for_end and input_data[i] == "$":
                    searching_for_end = False
                    data = refer_dict.get(buff, self.Empty())
                    if type(data) is self.Empty:
                        raise ValueError(f"key `{buff}` does not exist")
                    output_data = assign_or_append(output_data, data)
                    buff = ""
                # replacement
                elif not searching_for_end and input_data[i] == "$":
                    if i + 1 < inlen and input_data[i + 1] == "$":
                        if i + 1 < inlen and input_data[i + 1] == "$":
                            data = refer_dict.get(k, self.Empty())
                            if type(data) is self.Empty:
                                raise ValueError(f"key `{k}` does not exist")
                            output_data = assign_or_append(output_data, data)
                            i += 1
                    else:
                        searching_for_end = True
                else:
                    if searching_for_end:
                        buff += input_data[i]
                    else:
                        output_data = assign_or_append(output_data, input_data[i])
                i += 1

            if searching_for_end:
                raise ValueError(f"`${buff}` does not end with `$`, do you mean `${buff}$`?")
            return output_data

        # DEF search_and_change END


        self._full_dict = {}

        for k, v in self.impl_dict.items():

            if type(v) is str:
                # MustChange
                if v == "$?":
                    self._full_dict[k] = self.MustChange()
                # evaluate
                elif v[0:2] == "$!":
                    # "$!($data$.len - 2) * 5"  --> "([1, 3, 4].len - 2) * 5"
                    eval_str = search_and_change(v[2:], self.core_dict)
                    # "([1, 3, 4].len - 2) * 5" --> 5
                    result, valid = safe_eval(eval_str)
                    if not valid:
                        raise ValueError(f"`{eval_str}` cannot be evaluated or be evaluated safely")
                    self._full_dict[k] = result
                # escape and replacement
                else:
                    self._full_dict[k] = search_and_change(v, self.core_dict)
            else:
                self._full_dict[k] = v


    def update_from_mustchange(self, key, value) -> None:

        if not self._parsed: self.parse()

        if type(self._full_dict.get(key, self.Empty())) is self.MustChange:
            self._full_dict[key] = value
        else:
            if type(self._full_dict.get(key, self.Empty())) is self.Empty:
                raise ValueError(f"full_dict[{key}] cannot find when updating from MustChange")
            else:
                raise ValueError(f"full_dict[{key}] is not $? (MustChange) but {self._full_dict[key]} when updating from MustChange")


    @property
    def full_dict(self) -> dict:

        if not self._parsed: self.parse()

        for k, v in self._full_dict.items():
            if type(v) is self.MustChange:
                raise ValueError(f"full_dict[{k}] is $? (MustChange) which must use .update_from_mustchange() first")
        return self._full_dict


    def full_command(self, start: Optional[str] = None, show_true_false: bool = False) -> str:

        if not self._parsed: self.parse()

        res_list = []

        for k, v in self._full_dict.items():

            if type(v) is self.MustChange:
                raise ValueError(f"full_dict[{k}] is $? (MustChange) which must use .update_from_mustchange() first")

            if v is True or v is False:
                if show_true_false:
                    # True --> true; False --> false
                    res_list.append(f"--{k}={str(v).lower()}")
                elif v is True:
                    res_list.append(f"--{k}")
            else:
                res_list.append(f"--{k}={v}")

        res = " ".join(res_list)

        if start is not None:
            return start + " " + res
        else:
            return res
