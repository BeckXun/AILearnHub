import ast
import functools
import inspect
import os
import re
from string import Template
from typing import List, Callable, Tuple

import click
from dotenv import load_dotenv
from openai import OpenAI
import platform

from prompt_template import react_system_prompt_template


class ReActAgent:
    def __init__(self, tools: List[Callable], model: str, project_directory: str):
        # 为工具函数绑定项目目录上下文
        self.tools = {}
        for func in tools:
            if func.__name__ == 'read_file':
                # 为read_file绑定项目目录 - 使用functools.partial避免闭包问题
                bound_read_file = functools.partial(func, project_directory)
                bound_read_file.__name__ = 'read_file'
                bound_read_file.__doc__ = func.__doc__
                self.tools['read_file'] = bound_read_file
            elif func.__name__ == 'write_to_file':
                # 为write_to_file绑定项目目录 - 使用functools.partial避免闭包问题
                bound_write_to_file = functools.partial(func, project_directory)
                bound_write_to_file.__name__ = 'write_to_file'
                bound_write_to_file.__doc__ = func.__doc__
                self.tools['write_to_file'] = bound_write_to_file
            else:
                self.tools[func.__name__] = func
        
        self.model = model
        self.project_directory = project_directory
        self.client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key=ReActAgent.get_api_key(),
        )

    def run(self, user_input: str):
        messages = [
            {"role": "system", "content": self.render_system_prompt(react_system_prompt_template)},
            {"role": "user", "content": f"<question>{user_input}</question>"}
        ]

        while True:

            # 请求模型
            content = self.call_model(messages)

            # 检测 Thought
            thought_match = re.search(r"<thought>(.*?)</thought>", content, re.DOTALL)
            if thought_match:
                thought = thought_match.group(1)
                print(f"\n\n💭 Thought: {thought}")

            # 检测模型是否输出 Final Answer，如果是的话，直接返回
            if "<final_answer>" in content:
                final_answer = re.search(r"<final_answer>(.*?)</final_answer>", content, re.DOTALL)
                return final_answer.group(1)

            # 检测 Action
            action_match = re.search(r"<action>(.*?)</action>", content, re.DOTALL)
            if not action_match:
                raise RuntimeError("模型未输出 <action>")
            action = action_match.group(1)
            tool_name, args = self.parse_action(action)

            print(f"\n\n🔧 Action: {tool_name}({', '.join(args)})")
            # 只有终端命令才需要询问用户，其他的工具直接执行
            should_continue = input(f"\n\n是否继续？（Y/N）") if tool_name == "run_terminal_command" else "y"
            if should_continue.lower() != 'y':
                print("\n\n操作已取消。")
                return "操作被用户取消"

            try:
                observation = self.tools[tool_name](*args)
            except Exception as e:
                observation = f"工具执行错误：{str(e)}"
            print(f"\n\n🔍 Observation：{observation}")
            obs_msg = f"<observation>{observation}</observation>"
            messages.append({"role": "user", "content": obs_msg})


    def get_tool_list(self) -> str:
        """生成工具列表字符串，包含函数签名和详细说明"""
        tool_descriptions = []
        for func in self.tools.values():
            name = func.__name__
            signature = str(inspect.signature(func))
            doc = inspect.getdoc(func)
            
            # 为绑定的函数调整签名显示
            if name in ['read_file', 'write_to_file']:
                # 隐藏project_dir参数，显示用户实际需要的参数
                if name == 'read_file':
                    signature = "(file_path)"
                elif name == 'write_to_file':
                    signature = "(file_path, content)"
            
            tool_descriptions.append(f"- {name}{signature}: {doc}")
        return "\n".join(tool_descriptions)

    def render_system_prompt(self, system_prompt_template: str) -> str:
        """渲染系统提示模板，替换变量"""
        tool_list = self.get_tool_list()
        file_list = ", ".join(
            os.path.abspath(os.path.join(self.project_directory, f))
            for f in os.listdir(self.project_directory)
        )
        return Template(system_prompt_template).substitute(
            operating_system=self.get_operating_system_name(),
            tool_list=tool_list,
            file_list=file_list
        )

    @staticmethod
    def get_api_key() -> str:
        """Load the API key from an environment variable."""
        load_dotenv()
        api_key = os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            raise ValueError(
                "未找到 SILICONFLOW_API_KEY 环境变量，请在 .env 文件中设置。\n"
                "请访问 https://cloud.siliconflow.cn/ 获取API密钥。"
            )
        return api_key

    def call_model(self, messages):
        print("\n\n正在请求模型，请稍等...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # 添加一些默认参数
                max_tokens=4000,  # 限制最大token数
            )
            content = response.choices[0].message.content
            messages.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            print(f"\n\n❌ API调用失败: {str(e)}")
            raise

    def parse_action(self, code_str: str) -> Tuple[str, List[str]]:
        match = re.match(r'(\w+)\((.*)\)', code_str, re.DOTALL)
        if not match:
            raise ValueError("Invalid function call syntax")

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # 手动解析参数，特别处理包含多行内容的字符串
        args = []
        current_arg = ""
        in_string = False
        string_char = None
        i = 0
        paren_depth = 0
        
        while i < len(args_str):
            char = args_str[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                    current_arg += char
                elif char == '(':
                    paren_depth += 1
                    current_arg += char
                elif char == ')':
                    paren_depth -= 1
                    current_arg += char
                elif char == ',' and paren_depth == 0:
                    # 遇到顶层逗号，结束当前参数
                    args.append(self._parse_single_arg(current_arg.strip()))
                    current_arg = ""
                else:
                    current_arg += char
            else:
                current_arg += char
                if char == string_char and (i == 0 or args_str[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            i += 1
        
        # 添加最后一个参数
        if current_arg.strip():
            args.append(self._parse_single_arg(current_arg.strip()))
        
        return func_name, args
    
    def _parse_single_arg(self, arg_str: str):
        """解析单个参数"""
        arg_str = arg_str.strip()
        
        # 如果是字符串字面量
        if (arg_str.startswith('"') and arg_str.endswith('"')) or \
           (arg_str.startswith("'") and arg_str.endswith("'")):
            # 移除外层引号并处理转义字符
            inner_str = arg_str[1:-1]
            # 处理常见的转义字符
            inner_str = inner_str.replace('\\"', '"').replace("\\'", "'")
            inner_str = inner_str.replace('\\n', '\n').replace('\\t', '\t')
            inner_str = inner_str.replace('\\r', '\r').replace('\\\\', '\\')
            return inner_str
        
        # 尝试使用 ast.literal_eval 解析其他类型
        try:
            return ast.literal_eval(arg_str)
        except (SyntaxError, ValueError):
            # 如果解析失败，返回原始字符串
            return arg_str

    def get_operating_system_name(self):
        os_map = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux"
        }

        return os_map.get(platform.system(), "Unknown")


def read_file(project_dir, file_path):
    """读取文件内容
    
    参数:
    - file_path: 相对于项目目录的文件路径（例如: project_dir 设置为snake时，"index.html" 代表"snake/index.html"）
    
    示例:
    - read_file("index.html") - 读取project_dir下的index.html，project_dir 设置为snake时，"index.html" 代表"snake/index.html"
    - read_file("src/main.js") - 读取project_dir下的src子目录下的main.js，project_dir 设置为snake时，"src/main.js" 代表"snake/src/main.js"
    
    注意: 不要使用绝对路径或包含项目目录名的路径
    """
    # 如果是相对路径，则相对于项目目录
    if not os.path.isabs(file_path):
        file_path = os.path.join(project_dir, file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_to_file(project_dir, file_path, content):
    """将指定内容写入指定文件
    
    参数:
    - file_path: 相对于项目目录的文件路径（例如: "index.html" 或 "css/style.css"）
    - content: 要写入的文件内容
    
    示例:
    - write_to_file("index.html", "<html>...</html>") - 在项目根目录创建index.html
    - write_to_file("css/style.css", "body { margin: 0; }") - 在css子目录创建style.css
    
    注意: 
    - 不要使用绝对路径或包含项目目录名的路径
    - 会自动创建所需的子目录
    - 多行内容请使用\n表示换行
    """
    # 如果是相对路径，则相对于项目目录
    if not os.path.isabs(file_path):
        file_path = os.path.join(project_dir, file_path)
    
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content.replace("\\n", "\n"))
    return f"文件已写入: {file_path}"

def run_terminal_command(command):
    """执行终端命令
    
    参数:
    - command: 要执行的终端命令字符串
    
    示例:
    - run_terminal_command("ls -la") - 列出当前目录文件
    - run_terminal_command("python script.py") - 运行Python脚本
    - run_terminal_command("npm install") - 安装npm依赖
    
    注意: 命令会在项目目录下执行
    """
    import subprocess
    run_result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return "执行成功" if run_result.returncode == 0 else run_result.stderr

@click.command()
@click.argument('project_directory',
                type=click.Path(exists=True, file_okay=False, dir_okay=True))
def main(project_directory):
    project_dir = os.path.abspath(project_directory)

    tools = [read_file, write_to_file, run_terminal_command]
    # agent = ReActAgent(tools=tools, model="openai/gpt-4o", project_directory=project_dir)
    agent = ReActAgent(tools=tools, model="Qwen/Qwen3-30B-A3B-Thinking-2507", project_directory=project_dir)

    task = input("请输入任务：")

    final_answer = agent.run(task)

    print(f"\n\n✅ Final Answer：{final_answer}")

if __name__ == "__main__":
    main()
