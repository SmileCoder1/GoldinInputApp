import sys
from cx_Freeze import setup, Executable
exe = Executable(
    script=r"./excelParserThing.py",
    base="Win32GUI",
)
setup(
    name= "goldin's godly work",
    version = "0.1",
    description = "yeetfully yeetlicious",
    executables = [exe]
)