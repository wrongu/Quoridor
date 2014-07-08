def cache(key_ctor=(lambda k,a: k)):
	def decorator(fn):
		cache = {}
		def wrapper(inst, *args):
			key = key_ctor(inst.hash(), args)
			saved = cache.get(key)
			if saved:
				return saved
			else:
				created = fn(inst, *args)
				cache[key] = created
				return created
		return wrapper
	return decorator
