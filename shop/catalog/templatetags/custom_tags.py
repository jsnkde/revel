from django import template

register = template.Library()

@register.filter
def range(value, end):
	return value[:end]

@register.filter
def slice(value, argstr):
	args = argstr.split(',')
	
	start = 0
	end = None
	step = 1

	try:
		if len(args) > 0: 
			start = int(args[0]) 
		if len(args) > 1: 
			end = int(args[1])
		if len(args) > 2: 
			step = int(args[2]) 

	except ValueError:
		pass

	return value[start:end:step]