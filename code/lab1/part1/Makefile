SOURCES = fifo_if.sv fifo_mem.sv sync_r2w.sv sync_w2r.sv \
          fifo_rptr.sv fifo_wptr.sv async_fifo.sv tb_async_fifo.sv

VCS = $(VCS_HOME)/bin/vcs
VERDI = $(VERDI_HOME)/bin/verdi

all: compile

compile:
	$(VCS) -full64 -sverilog -timescale=1ns/1ps $(SOURCES) \
	-top tb_async_fifo -debug_access+all -kdb -lca

test1:
	./simv +TEST_FILL_EMPTY

test2:
	./simv +TEST_FLAGS

test3:
	./simv +TEST_SIMULTANEOUS

verdi:
	$(VERDI) -dbdir ./simv.daidir -ssf novas.fsdb -nologo

# Cycle-accurate CSV trace for plotting. Writes trace-<test>.csv next to simv.
# Nothing changes in a normal run; the testbench only opens the file on +TRACE.
trace: compile
	mkdir -p trace
	./simv +TEST_FILL_EMPTY   +TRACE=fill_empty
	./simv +TEST_FLAGS        +TRACE=flags
	./simv +TEST_SIMULTANEOUS +TRACE=simultaneous
	mv trace-*.csv trace/
	@ls -1 trace/

clean:
	rm -rf AN.DB csrc simv simv.daidir DVEfiles
	rm -f novas.fsdb novas_dump.log novas.conf novas.rc ucli.key
