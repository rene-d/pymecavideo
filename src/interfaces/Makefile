GUIS = $(shell ls *.ui)
COMPILED_GUIS = $(patsubst %.ui, Ui_%.py, $(GUIS))

RC = $(shell ls *.qrc)
COMPILED_RC = $(patsubst %.qrc, %_rc.py, $(RC))

all: $(COMPILED_GUIS) $(COMPILED_RC)

%_rc.py: %.qrc
	rcc -g python -o $@ $<
	sed -i 's/PySide./PyQt6/' $@

Ui_%.py: %.ui
	pyuic6 $< > $@

