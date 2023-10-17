import os
import re
import ast
import json
from pathlib import Path
from typing import Optional, Union

class ArgImpl:

    def __init__(self) -> None:
        """
        After init, please use `.load_dict()` or `.load_json()` first.
        """
        pass

    def load_dict(
        self,
        core_arg_dict: dict,
        arg_impl_dict: dict
    ) -> None:
        """Use `arg_impl_dict` to implement `core_arg_dict` into a full arg dict, and form execute command

        Arguments:

            core_arg_dict: your input core dict
            arg_impl_dict: arguments inplement dict

        Typical usage example:

            ```
            core_arg_dict = {
                "age": 10,
                "name": "John",
                "fruits": ["apple", "banana", "orange"]
            }
            arg_impl_dict = {
                "name": "$$",
                "age": "$$",
                "favourite_fruit": "$!$fruits$[0]",
                "class": 1
            }
            ```

            after load_dict, the result will be

            ```
            arg_impl = ArgImpl()
            arg_impl.load_dict(core_arg_dict, arg_impl_dict)
            arg_impl.full_arg_dict == {
                "name": "John",
                "age": 10,
                "favourite_fruit": "apple",
                "class": 1
            }
            ```
        """
        self.core_arg_dict = core_arg_dict
        self.this_type_dict = arg_impl_dict
        self.full_arg_dict = {}
        self.__parse()

    def load_json(
        self,
        core_arg_dict: dict,
        arg_impl_json_path: Union[str, Path],
        arg_impl_type_key: str
    ) -> None:
        """Use `arg_impl_json` (path, type_key) to implement `core_arg_dict` into a full arg dict, and form execute command

        Arguments:

            core_arg_dict: your input core dict
            arg_impl_json_path: path of `arg_impl.json`
            arg_impl_type_key: key of which dict to choose in `arg_impl.json`

        Typical usage example:

            ```
            core_arg_dict = {
                "age": 10,
                "name": "John",
                "fruits": ["apple", "banana", "orange"]
            }
            ```

            in `./arg_impl.json`
            
            ```
            {
                "school_impl": {
                    "name": "$$",
                    "age": "$$",
                    "favourite_fruit": "$!$fruits$[0]",
                    "class": 1
                },
                "family_impl": {
                    "name": "$$ Williams",
                    "age": "$!$$+25"
                }
            }
            ```

            after __init__, the result will be

            ```
            arg_impl = ArgImpl()
            arg_impl.load_json(core_arg_dict, "./arg_impl.json", "school_impl")
            arg_impl.full_arg_dict == {
                "name": "John",
                "age": 10,
                "favourite_fruit": "apple",
                "class": 1
            }
            ```
        """

        self.core_arg_dict = core_arg_dict
        self.arg_impl_json_path = Path(arg_impl_json_path)
        self.arg_impl_type_key = arg_impl_type_key
        self.all_dicts = {}
        self.this_type_dict = {}
        self.full_arg_dict = {}

        if not os.path.exists(self.arg_impl_json_path):
            raise ValueError(f"arg_impl_json_path `{self.arg_impl_json_path}` does not exist")
        
        with open(self.arg_impl_json_path) as f:
            self.all_dicts: dict = json.load(f)
            if type(self.all_dicts) is not dict:
                raise ValueError(f"arg_impl_json_path `{self.arg_impl_json_path}` is not a valid dict")
        
        self.this_type_dict = self.all_dicts.get(self.arg_impl_type_key, None)
        if self.this_type_dict is None:
            raise ValueError(f"arg_impl_type_key `{self.arg_impl_type_key}` does not exist")
        
        self.__parse()
    
    def change_json_type_key(self, new_type_key: str):

        self.arg_impl_type_key = new_type_key

        self.this_type_dict = self.all_dicts.get(self.arg_impl_type_key, None)
        if self.this_type_dict is None:
            raise ValueError(f"new_type_key `{self.arg_impl_type_key}` does not exist")
        
        self.__parse()


    def __parse(self):

        self.full_arg_dict = {}

        for k, v in self.this_type_dict.items():

            def search_and_change(input_data, refer_dict):
                output_data = ""
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
                                output_data += input_data[i + 1]
                            i += 1
                        else:
                            if searching_for_end:
                                buff += "\\"  # non-escaping \\ or last \\
                            else:
                                output_data += "\\"
                    elif searching_for_end and input_data[i] == "$":
                        searching_for_end = False
                        data = refer_dict.get(buff, None)
                        if data is None:
                            raise ValueError(f"key `{buff}` does not exist")
                        output_data += str(data)
                        buff = ""
                    # replacement
                    elif not searching_for_end and input_data[i] == "$":
                        if i + 1 < inlen and input_data[i + 1] == "$":
                            if i + 1 < inlen and input_data[i + 1] == "$":
                                data = refer_dict.get(k, None)
                                if data is None:
                                    raise ValueError(f"key `{k}` does not exist")
                                output_data += str(data)
                                i += 1
                        else:
                            searching_for_end = True
                    else:
                        if searching_for_end:
                            buff += input_data[i]
                        else:
                            output_data += input_data[i]
                    i += 1
                if searching_for_end:
                    raise ValueError(f"`${buff}` does not end with `$`, do you mean `${buff}$`?")
                return output_data

            v = str(v)
            # evaluate
            if v[0:2] == "$!":
                eval_str = search_and_change(v[2:], self.core_arg_dict)
                pattern = re.compile(r"(.+)\s*((\+|-|\*|//|%)\s*(.+)\s*|\[\s*(.+)\s*\]|\.len)")
                result = pattern.match(eval_str)
                if result is None:
                    raise ValueError(f"`{eval_str}` cannot be evaluated or be evaluated safely")
                # + - * // %
                if result.group(3) is not None:
                    if result.group(3) == "+":
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1)) + ast.literal_eval(result.group(4))
                    elif result.group(3) == "-":
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1)) - ast.literal_eval(result.group(4))
                    elif result.group(3) == "*":
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1)) * ast.literal_eval(result.group(4))
                    elif result.group(3) == "//":
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1)) // ast.literal_eval(result.group(4))
                    elif result.group(3) == "%":
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1)) % ast.literal_eval(result.group(4))
                else:
                    if result.group(2) == ".len":
                        self.full_arg_dict[k] = len(ast.literal_eval(result.group(1)))
                    else:
                        self.full_arg_dict[k] = ast.literal_eval(result.group(1))[ast.literal_eval(result.group(5))]
                check = self.full_arg_dict.get(k, None)
                if check is None:
                    raise ValueError(f"`{eval_str}` cannot be evaluated or be evaluated safely")
            # escape and replacement
            else:
                self.full_arg_dict[k] = search_and_change(v, self.core_arg_dict)


    @property
    def full_dict(self) -> dict:
        return self.full_arg_dict
    
    def full_command(self, start: Optional[str] = None) -> str:
        if start is not None:
            return start + " " + " ".join([f"--{k}={v}" for k, v in self.full_arg_dict.items()])
        else:
            return " ".join([f"--{k}={v}" for k, v in self.full_arg_dict.items()])


if __name__ == "__main__":

    core_arg_dict = {
        "age": 10,
        "name": "John",
        "fruits": ["apple", "banana", "orange"]
    }
    arg_impl_dict = {
        "name": "$$",
        "age": "$$",
        "favourite_fruit": "$!$fruits$[0]",
        "class": 1
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
    print(arg_impl.full_dict)
    print(arg_impl.full_command("echo"))
