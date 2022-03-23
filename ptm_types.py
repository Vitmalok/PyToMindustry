class PyToMindustryError(Exception):
	pass



class Var:
	def unary_op(self, mindustry, stack, current_stackvar, opname):
		if opname == 'UNARY_POSITIVE':
			return
		
		current_stackvar.next()
		cs = current_stackvar.copy()
		s = self
		mindustry.append({
			'UNARY_NEGATIVE': ['op', 'sub', cs, 0, s],
			'UNARY_NOT': ['op', 'equal', cs, s, 0],
			'UNARY_INVERT': ['op', 'sub', cs, -1, s],
		}[opname])
		
		return cs
	
	def binary_op(self, mindustry, stack, current_stackvar, opname, other):
		current_stackvar.next()
		cs = current_stackvar.copy()
		s = self
		o = other
		mindustry.append({
			'BINARY_POWER': ['op', 'pow', cs, s, o],
			'BINARY_MULTIPLY': ['op', 'mul', cs, s, o],
			'BINARY_MODULO': ['op', 'mod', cs, s, o],
			'BINARY_ADD': ['op', 'add', cs, s, o],
			'BINARY_SUBTRACT': ['op', 'sub', cs, s, o],
			'BINARY_SUBSCR': ['read', cs, s, o],
			'BINARY_FLOOR_DIVIDE': ['op', 'idiv', cs, s, o],
			'BINARY_TRUE_DIVIDE': ['op', 'div', cs, s, o],
			'BINARY_LSHIFT': ['op', 'shl', cs, s, o],
			'BINARY_RSHIFT': ['op', 'shr', cs, s, o],
			'BINARY_AND': ['op', 'and', cs, s, o],
			'BINARY_XOR': ['op', 'xor', cs, s, o],
			'BINARY_OR': ['op', 'or', cs, s, o],
		}[opname])
		
		return cs
	
	def inplace_op(self, mindustry, stack, current_stackvar, opname, other):
		return self.binary_op(mindustry, stack, current_stackvar, f'BINARY_{opname.split("_")[1]}', other)
	
	def compare_op(self, mindustry, stack, current_stackvar, op, other):
		current_stackvar.next()
		cs = current_stackvar.copy()
		s = self
		o = other
		mindustry.append({
			'<': ['op', 'lessThan', cs, s, o],
			'<=': ['op', 'lessThanEq', cs, s, o],
			'==': ['op', 'equal', cs, s, o],
			'!=': ['op', 'notEqual', cs, s, o],
			'>': ['op', 'greaterThan', cs, s, o],
			'>=': ['op', 'greaterThanEq', cs, s, o],
			'is': ['op', 'strictEqual', cs, s, o],
		}[op])
		
		return cs

class Const(Var):
	def __init__(self, value):
		self.value = value
		self.type_ = type(value)
		
		self.name = repr(self)
	
	def __repr__(self):
		value = self.value
		type_ = str(self.type_).split("'")[1]
		
		if type_ == 'NoneType':
			return 'null'
		elif type_ == 'int':
			return str(value)
		elif type_ == 'float':
			return str(value)
		elif type_ == 'str':
			return f'"{value}"'
		elif type_ == 'bool':
			return str(value).lower()
		elif type_ == 'code':
			return str(value)
		else:
			return f'<Const type="{type_}" value="{value}">'

class Name(Var):
	def __init__(self, name):
		self.name = name
	
	def __repr__(self):
		return self.name

class PyName:
	def __init__(self, name, contained_object):
		self.name = name
		self.contained_object = contained_object
	
	def __repr__(self):
		return f'<PyName \'{self.name}\' containing {self.contained_object}>'



def _create_numericvar_class(prefix_):
	class _class(Var):
		prefix = prefix_
		
		def __init__(self, field_of_view, number=0):
			self.field_of_view = field_of_view
			self.number = number
			
			self.name = repr(self)
		
		def __repr__(self):
			return f'_{self.field_of_view}_{_class.prefix}{self.number}'
		
		def copy(self):
			return _class(self.field_of_view, self.number)
		
		def next(self):
			self.number += 1
	
	return _class



Stackvar = _create_numericvar_class('')
Quantvar = _create_numericvar_class('q')
