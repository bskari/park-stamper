all: js

.PHONY: js
js:
	static/js/lib/closure-library/closure/bin/build/depswriter.py --root_with_prefix='static/js/src ../../../../src' --output_file='static/js/deps.js'

.PHONY: clean
clean:
	find . -iname '*.pyc' -exec rm '{}' ';'
