
NAME:= "azinvoicer"
RELNUM := $(shell cat RELEASE.txt)
PACKAGENAME="$(NAME).rel.v$(RELNUM).tar.gz"

UNITTEST=test.azinvoicer.test_iotools.TestIOTools.test_listToFile

all: clean dependencies format tests
githubpipeline: pyformatcheck tests
format: tounix pyformat pyformatcheck

dependencies:
	@echo "[>] ############################################"
	@echo "[>] installing python dependencies"
	@echo "[>] ############################################"
	@pip3 install -r requirements.txt

tounix:
	@echo "[>] ############################################"
	@echo "[>] converting files to unix format"
	@echo "[>] ############################################"
	@dos2unix *.py
	@dos2unix azinvoicer/*.py

pyformat:
	@echo "[>] ############################################"
	@echo "[>] formatting python source files"
	@echo "[>] ############################################"
	@python3 -m black azinvoicer/*.py
	@python3 -m black *.py 

pyformatcheck:
	@echo "[>] ############################################"
	@echo "[>] checking source syntax violations : "
	@echo "[>] ############################################"
	@python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "[>] ############################################"
	@echo "[>] checking source formatting violations : "
	@echo "[>] ############################################"
	@python3 -m flake8 . --count --statistics

clean:
	@echo "[>] ############################################"
	@echo "[>] cleaning release files"
	@echo "[>] ############################################"
	@rm -f "$(NAME).rel.*"
	@find . -type d -name "__pycache__" | xargs rm -rf

tests:
	@echo "[>] ############################################"
	@echo "[>] running unit tests"
	@echo "[>] ############################################"
	@python3 -m nose2 -v -F
	@echo "[>] ############################################"
	@echo "[>] computing test coverage"
	@echo "[>] ############################################"
	@python3 -m coverage run -m nose2 -C
	#@python3 -m coverage report


singletest:
	@echo "[>] ############################################"
	@echo "[>] running test $(UNITTEST)"
	@echo "[>] ############################################"
	@python3 -m nose2 -v $(UNITTEST)

release:
	@echo "[>] ############################################"
	@echo "[>] building release package"
	@echo "[>] ############################################"
	@rm -f $(PACKAGENAME)
	@tar cfz $(PACKAGENAME) azinvoicer/*.py *.py
	@echo "[>] archive $(PACKAGENAME) created"
	@echo "[>] ############################################"

