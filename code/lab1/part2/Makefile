VARIANT ?= sync

DEPTH_sync  ?= 40
DEPTH_async ?= 64
DEPTH        = $(DEPTH_$(VARIANT))

TEST ?=
ifeq ($(TEST),)
  PLUSARGS =
else
  PLUSARGS = +TEST=$(TEST)
endif

VCS   = $(VCS_HOME)/bin/vcs
VERDI = $(VERDI_HOME)/bin/verdi

PART1 = ../part1
BUILD = build/$(VARIANT)

SRC_sync  = rtl/sync/fifo_q.sv

SRC_async = $(PART1)/fifo_if.sv   $(PART1)/fifo_mem.sv  \
            $(PART1)/sync_r2w.sv  $(PART1)/sync_w2r.sv  \
            $(PART1)/fifo_rptr.sv $(PART1)/fifo_wptr.sv \
            $(PART1)/async_fifo.sv rtl/async/fifo_q.sv

FIFO_SRC = $(SRC_$(VARIANT))

VCSFLAGS = -full64 -sverilog -timescale=1ns/1ps -debug_access+all -kdb -lca \
           +define+FIFO_DEPTH=$(DEPTH)

all: compile

compile: $(BUILD)
	$(VCS) $(VCSFLAGS) $(FIFO_SRC) rtl/even_odd_top.sv tb/tb_even_odd.sv \
	  -top tb_even_odd -Mdir=$(BUILD)/csrc -o $(BUILD)/simv -l $(BUILD)/compile.log

run: compile
	cd $(BUILD) && ./simv $(PLUSARGS)

fifo: $(BUILD)
	$(VCS) $(VCSFLAGS) $(FIFO_SRC) tb/tb_fifo_q.sv \
	  -top tb_fifo_q -Mdir=$(BUILD)/csrc_fifo -o $(BUILD)/simv_fifo -l $(BUILD)/fifo.log
	cd $(BUILD) && ./simv_fifo

compare:
	@for v in sync async ; do \
	  echo "======== VARIANT=$$v  DEPTH=$$($(MAKE) --no-print-directory VARIANT=$$v printdepth)" ; \
	  $(MAKE) --no-print-directory VARIANT=$$v run 2>&1 \
	    | grep -E 'RESULT|stall|cycles|PASSED|FAILED|Error' ; \
	done

printdepth:
	@echo $(DEPTH)

trace: compile
	mkdir -p trace
	cd $(BUILD) && ./simv +TRACE $(PLUSARGS)
	cp $(BUILD)/trace-*.csv trace/
	@ls -1 trace/

verdi:
	$(VERDI) -dbdir $(BUILD)/simv.daidir -ssf $(BUILD)/novas.fsdb -nologo &

$(BUILD):
	mkdir -p $(BUILD)

clean:
	rm -rf build

.PHONY: all compile run fifo compare verdi clean printdepth trace
