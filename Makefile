POCS := $(wildcard poc-*)

.PHONY: test validate
test:
	@for d in $(POCS); do \
	  if [ -d $$d/tests ]; then echo "== $$d"; (cd $$d && python -m pytest -q) || exit 1; fi; \
	done

validate:
	@python -c "import glob,hcl2; fs=glob.glob('poc-*/terraform/*.tf'); [hcl2.load(open(f)) for f in fs]; print(f'{len(fs)} terraform files parse OK')"
