# -*- coding: utf-8 -*-
from rpython.rlib import rfile

from constant import *
from bytecode_parser import BytecodeParser
from error import InvalidType
from rpython.rlib import rrandom, rtimer
from rpython.rlib.rarithmetic import intmask, r_uint
import os
import time

LINE_BUFFER_LENGTH = 1024


def print_char_builtin_func(_, args):
  ch = args[0]
  assert ch is not None
  if isinstance(ch, ConstChar):
    os.write(1, ch.charval.encode('utf-8'))
    return ConstNone()
  else:
    raise InvalidType(u"문자", ch.type_name())

def stringize_builtin_func(_, args):
  l = []
  for ch in args[0].show():
    l.append(ConstChar(ch))

  return list_to_struct(l)

def input_builtin_func(_, args):
  stdin, stdout, stderr = rfile.create_stdio()
  line = stdin.readline(LINE_BUFFER_LENGTH)
  parser = BytecodeParser(line)

  result = []
  while parser.code[parser.pos] != '\n':
    result.append(parser.parse_char())

  return list_to_struct(result)

def to_integer_builtin_func(_, args):
  a = args[0]
  if isinstance(a, ConstStruct):
    s = collect_string(a)
    try:
      return ConstInteger(int(s.encode('utf-8')))
    except:
      return ConstNone()
  elif isinstance(a, ConstChar):
    try:
      return ConstInteger(int(a.charval.encode('utf-8')))
    except:
      return ConstNone()
  elif isinstance(a, ConstReal):
    return ConstInteger(int(a.doubleval))
  elif isinstance(a, ConstInteger):
    return a
  else:
    raise InvalidType(u"정수화할 수 있는", a.type_name())

def to_real_builtin_func(_, args):
  a = args[0]
  if isinstance(a, ConstStruct):
    s = collect_string(a)
    try:
      return ConstReal(float(s.encode('utf-8')))
    except:
      return ConstNone()
  elif isinstance(a, ConstChar):
    try:
      return ConstReal(float(a.charval.encode('utf-8')))
    except:
      return ConstNone()
  elif isinstance(a, ConstReal):
    return a
  elif isinstance(a, ConstInteger):
    return ConstReal(float(a.intval))
  else:
    raise InvalidType(u"실수화할 수 있는", a.type_name())

def random_builtin_func(_, args):
  rng = rrandom.Random(seed=r_uint(rtimer.read_timestamp()))
  return ConstInteger(intmask(rng.genrand32()))

def call_builtin_func(self, args):
  arg = args[1]
  func = args[0]

  arg_list = []
  if isinstance(arg, ConstStruct):
    arg_list = collect(arg)
  else:
    arg_list = [arg]

  assert isinstance(func, ConstFunc)
  if func.builtinval is not None:
    return func.builtinval(self, arg_list)
  else:
    return self.run(func.funcval, arg_list)

print_char_builtin = ConstFunc([(u"을", None)], None, print_char_builtin_func)
stringize_builtin = ConstFunc([(u"을", None)], None, stringize_builtin_func)
input_builtin = ConstFunc([], None, input_builtin_func)
to_integer_builtin = ConstFunc([(u"을", None)], None, to_integer_builtin_func)
to_real_builtin = ConstFunc([(u"을", None)], None, to_real_builtin_func)
random_builtin = ConstFunc([], None, random_builtin_func)
call_builtin = ConstFunc([(u"을", None), (u"로", None)], None, call_builtin_func)

default_globals = {
    u"문자 출력하다": print_char_builtin,
    u"문자열화하다": stringize_builtin,
    u"입력받다": input_builtin,
    u"정수화하다": to_integer_builtin,
    u"실수화하다": to_real_builtin,
    u"난수 가져오다": random_builtin,
    u"호출하다": call_builtin,
}

