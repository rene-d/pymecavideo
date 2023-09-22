GUIS = $(shell ls *.ui)
COMPILED_GUIS = $(patsubst %.ui, Ui_%.py, $(GUIS))
RCC = pyside6-rcc

RC = $(shell ls *.qrc)
COMPILED_RC = $(patsubst %.qrc, %_rc.py, $(RC))

all: $(COMPILED_GUIS) $(COMPILED_RC)

%_rc.py: %.qrc
	$(RCC) -g python -o $@ $<
	sed -i.bak 's/PySide./PyQt6/' $@

Ui_%.py: %.ui
	pyuic6 $< > $@

