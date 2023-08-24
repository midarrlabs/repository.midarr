export PYTHONPATH := .:$(CURDIR)/test
PYTHON := python
KODI_PYTHON_ABIS := 3.0.1

name = $(shell xmllint --xpath 'string(/addon/@id)' addon.xml)
version = $(shell xmllint --xpath 'string(/addon/@version)' addon.xml)

zip_name = $(name)-$(version).zip

include_files = addon.py addon.xml LICENSE README resources/
include_paths = $(patsubst %,$(name)/%,$(include_files))
exclude_files = \*.new \*.orig \*.pyc \*.pyo
zip_dir = $(name)/

blue = \e[1;34m
white = \e[1;37m
reset = \e[0m

build: clean
	@echo -e "$(white)=$(blue) Building new package$(reset)"
	@rm -f ../$(zip_name)
	cd ..; zip -r $(zip_name) $(include_paths) -x $(exclude_files)
	@echo -e "$(white)=$(blue) Successfully wrote package as: $(white)../$(zip_name)$(reset)"

multizip: clean
	@-$(foreach abi,$(KODI_PYTHON_ABIS), \
		echo "cd /addon/requires/import[@addon='xbmc.python']/@version\nset $(abi)\nsave\nbye" | xmllint --shell addon.xml; \
		version=$(version); \
		echo "cd /addon/@version\nset $$version\nsave\nbye" | xmllint --shell addon.xml; \
		make build; \
	)

clean:
	@echo -e "$(white)=$(blue) Cleaning up$(reset)"
	find . -name '*.py[cod]' -type f -delete
	find . -name __pycache__ -type d -delete
	rm -rf .pytest_cache/ .tox/
	rm -f *.log