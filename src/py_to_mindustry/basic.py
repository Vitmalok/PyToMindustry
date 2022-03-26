from py_to_mindustry.ptm_types import *



def _use_func_pattern(pattern, current_stackvar, args):
	command = []
	outputs = []
	arg_i = 0
	
	for part in pattern:
		if type(part) == str and part and part[0] == '%':
			if part.endswith('arg'):
				try:
					command.append(args[arg_i])
				except IndexError:
					raise PyToMindustryError(f'Not enough {len(args)} arguments for function.')
				
				arg_i += 1
			elif part.endswith('out'):
				current_stackvar.next()
				command.append(current_stackvar.copy())
				outputs.append(current_stackvar.copy())
		else:
			command.append(part)
	
	return command, outputs



def _create_simple_func_class(pattern_):
	class _class:
		pattern = pattern_
		
		def CALL_FUNCTION(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, args):
			command, outputs = _use_func_pattern(_class.pattern, current_stackvar, args)
			mindustry.append(command)
			
			match len(outputs):
				case 0:
					return None
				case 1:
					return outputs[0]
				case _:
					return outputs
		
	return _class

def _create_simple_method_class(pattern_):
	class _class:
		pattern = pattern_
		
		def CALL_METHOD(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, args):
			command, outputs = _use_func_pattern(_class.pattern, current_stackvar, [field_of_view] + args)
			mindustry.append(command)
			
			match len(outputs):
				case 0:
					return None
				case 1:
					return outputs[0]
				case _:
					return outputs
	
	return _class

def _create_simple_attr_class(attr_name_):
	class _class:
		attr_name = attr_name_
		
		def LOAD_ATTR(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view):
			current_stackvar.next()
			mindustry.append(['sensor', current_stackvar.copy(), field_of_view, _class.attr_name])
			return current_stackvar.copy()
	
	return _class

def _create_simple_setattr_class(attr_name_):
	class _class:
		attr_name = attr_name_
		
		def LOAD_ATTR(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view):
			current_stackvar.next()
			mindustry.append(['sensor', current_stackvar.copy(), field_of_view, _class.attr_name])
			return current_stackvar.copy()
		
		def STORE_ATTR(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, value):
			if type(value) not in ('tuple', 'list'):
				value = (value,)
			
			mindustry.append(['control', _class.attr_name, field_of_view, *value, *[0]*(4 - len(value))])
	
	return _class

class _range_func:
	def CALL_FUNCTION(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, args):
		current_stackvar.next()
		return PyName(current_stackvar.copy(), _range_obj(*args))

class _range_obj:
	def __init__(self, *args):
		if len(args) == 1:
			self.start, self.stop, self.step = 0, *args, 1
		elif len(args) == 2:
			self.start, self.stop, self.step = *args, 1
		elif len(args) == 3:
			self.start, self.stop, self.step = args
	
	def GET_ITER(self, mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view):
		mindustry.append(['set', Name(f'{field_of_view}_i'), Const(self.start - self.step)])
		return PyName(field_of_view, self)
	
	def FOR_ITER(self, mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, jump_to):
		i = Name(f'{field_of_view}_i')
		mindustry.append(['op', 'add', i, i, Const(self.step)])
		
		jump = (len(mindustry), 1)
		
		if jump_to in deferred_jumps:
			deferred_jumps[jump_to].append(jump)
		else:
			deferred_jumps[jump_to] = [jump]
		
		mindustry.append(['jump', None, 'greaterThanEq', i, self.stop])
		
		return i

class _print_func:
	def CALL_FUNCTION(mindustry, stack, current_stackvar, deferred_jumps, lines, field_of_view, args):
		mindustry.append(['print', *args])



renamed_names = {py_name: Name('@' + py_name[1:]) for py_name in [
	'_unit',
	
	'_dagger', '_mace', '_fortress', '_scepter', '_reign',
	'_nova', '_pulsar', '_quasar', '_vela', '_corvus',
	'_crawler', '_atrax', '_spiroct', '_arcyid', '_toxopid',
	'_flare', '_horizon', '_zenith', '_antumbra', '_eclipse',
	'_mono', '_poly', '_mega', '_quad', '_oct',
	'_risso', '_minke', '_bryde', '_sei', '_omura',
	'_retusa', '_oxynoe', '_cuerce', '_aegires', '_navanax',
	'_alpha', '_beta', '_gamma',
	
	'_copper', '_lead', '_metaglass', '_graphite', '_sand', '_coal',
	'_titanium', '_thorium', '_scrap', '_silicon', '_plastanium', '_phaseFabric',
	'_surgeAlloy', '_sporePod', '_blastCompound', '_pyratite',
	
	'_water', '_slag', '_oil', '_cryofluid',
	
	'_totalItems', '_firstItem', '_totalLiquids', '_itemCapacity', '_liquidCapacity',
	'_totalPower', '_powerCapacity', '_powerNetStored', '_powerNetCapacity', '_powerNetIn', '_powerNetOut',
	'_ammo', '_ammoCapacity', '_health', '_maxHealth', '_heat', '_efficiency', '_progress', '_timescale',
	'_rotation', '_x', '_y', '_shootX', '_shootY', '_size', '_dead', '_range', '_shooting', '_boosting',
	'_mineX', '_mineY', '_mining', '_team', '_type', '_flag', '_controlled', '_controller', '_name',
	'_payloadCount', '_payloadType', '_enabled', '_config',
]}

names = {
	**{
		'range': _range_func,
		'print': _print_func,
	},
	**{pattern[0]: _create_simple_func_class(pattern) for pattern in [
		['drawflush', '%arg'],
		['printflush', '%arg'],
		['getlink', '%out', '%arg'],
		['radar', '%arg', '%arg', '%arg', '%arg', '%arg', '%arg', '%out'],
		['wait', '%arg'],
		['lookup', '%arg', '%out', '%arg'],
		['ubind', '%arg'],
		['uradar', '%arg', '%arg', '%arg', '%arg', '%arg', '%out'],
		['ulocate', '%arg', '%arg', '%arg', '%arg', '%arg', '%out', '%out'],
	]},
	**{name: _create_simple_func_class(['op', name, '%out', '%arg', '%arg']) for name in [
		'pow', 'max', 'min', 'angle', 'len', 'noise',
	]},
	**{name: _create_simple_func_class(['op', name, '%out', '%arg', 0]) for name in [
		'abs', 'log', 'log10', 'floor', 'ceil', 'sqrt', 'rand', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
	]},
	'draw': type('_draw_class', (), {pattern[0]: _create_simple_func_class(['draw'] + pattern) for pattern in [
		['clear', '%arg', '%arg', '%arg', 0, 0, 0],
		['color', '%arg', '%arg', '%arg', '%arg', 0, 0],
		['stroke', '%arg', 0, 0, 0, 0, 0],
		['line', '%arg', '%arg', '%arg', '%arg', 0, 0],
		['rect', '%arg', '%arg', '%arg', '%arg', 0, 0],
		['lineRect', '%arg', '%arg', '%arg', '%arg', 0, 0],
		['poly', '%arg', '%arg', '%arg', '%arg', '%arg', 0],
		['linePoly', '%arg', '%arg', '%arg', '%arg', '%arg', 0],
		['triangle', '%arg', '%arg', '%arg', '%arg', '%arg', '%arg'],
		['image', '%arg', '%arg', '%arg', '%arg', '%arg', 0],
	]}),
	'ucontrol': type('_ucontrol_class', (), {pattern[0]: _create_simple_func_class(['ucontrol'] + pattern) for pattern in [
		['idle', 0, 0, 0, 0, 0],
		['stop', 0, 0, 0, 0, 0],
		['move', '%arg', '%arg', 0, 0, 0],
		['approach', '%arg', '%arg', '%arg', 0, 0],
		['boost', '%arg', 0, 0, 0, 0],
		['pathfind', 0, 0, 0, 0, 0],
		['target', '%arg', '%arg', '%arg', 0, 0],
		['targetp', '%arg', '%arg', 0, 0, 0],
		['itemDrop', '%arg', '%arg', 0, 0, 0],
		['itemTake', '%arg', '%arg', '%arg', 0, 0],
		['payDrop', 0, 0, 0, 0, 0],
		['payTake', '%arg', 0, 0, 0, 0],
		['payEnter', 0, 0, 0, 0, 0],
		['mine', '%arg', '%arg', 0, 0, 0],
		['flag', '%arg', 0, 0, 0, 0],
		['build', '%arg', '%arg', '%arg', '%arg', '%arg'],
		['getBlock', '%arg', '%arg', '%out', '%out'],
		['within', '%arg', '%arg', '%arg', '%out', 0],
	]}),
}

methods = {name: _create_simple_method_class(pattern) for name, pattern in [
	('drawflush', ['drawflush', '%arg']),
	('printflush', ['printflush', '%arg']),
	('off', ['control', 'enabled', 0, 0, 0, 0]),
	('on', ['control', 'enabled', 1, 0, 0, 0]),
	('enabled', ['control', 'enabled', '%arg', 0, 0, 0]),
	('shoot', ['control', 'shoot', '%arg', '%arg', '%arg', 0]),
	('shootp', ['control', 'shootp', '%arg', '%arg', 0, 0]),
	('config', ['control', 'config', '%arg', 0, 0, 0]),
	('color', ['control', 'color', '%arg', '%arg', '%arg', 0]),
]}

attrs = {
	**{attr_name: _create_simple_attr_class('@' + attr_name) for attr_name in [
		'copper', 'lead', 'metaglass', 'graphite', 'sand', 'coal',
		'titanium', 'thorium', 'scrap', 'silicon', 'plastanium', 'phaseFabric',
		'surgeAlloy', 'sporePod', 'blastCompound', 'pyratite',
		
		'water', 'slag', 'oil', 'cryofluid',
		
		'totalItems', 'firstItem', 'totalLiquids', 'itemCapacity', 'liquidCapacity',
		'totalPower', 'powerCapacity', 'powerNetStored', 'powerNetCapacity', 'powerNetIn', 'powerNetOut',
		'ammo', 'ammoCapacity', 'health', 'maxHealth', 'heat', 'efficiency', 'progress', 'timescale',
		'rotation', 'x', 'y', 'shootX', 'shootY', 'size', 'dead', 'range', 'shooting', 'boosting',
		'mineX', 'mineY', 'mining', 'team', 'type', 'flag', 'controlled', 'controller', 'name',
		'payloadCount', 'payloadType',
	]},
	**{attr_name: _create_simple_setattr_class('@' + attr_name) for attr_name in [
		'enabled', 'config',
	]},
}