# Lab 1 Part 2: even/odd alternating circuit.
#
# 같은 상위 모듈과 같은 testbench 를 쓰고 FIFO 구현만 갈아끼운다. 그래야 두 구현의
# 차이만 남고 다른 변수가 안 섞인다. 두 구현은 모듈 이름이 fifo_q 로 같고
# 디렉토리로만 갈린다.
#
#   make                     동기 FIFO. 제출본이다
#   make VARIANT=async       Part 1 의 비동기 FIFO 를 동기 포트로 감싼 것
#   make fifo                FIFO 레벨 testbench. 구현 자체를 먼저 검증한다
#   make compare             둘 다 돌려서 결과를 나란히 찍는다
#
# 환경은 ../part1/env.sh 를 source 한 뒤에 쓴다 (Apporto 기본 셸이 bash 다).

VARIANT ?= sync

# 두 FIFO 의 깊이. 근거는 MEASUREMENTS.md 에 있다.
#   동기  : 40 이면 충분하다. 2의 거듭제곱일 필요가 없다
#   비동기: gray code 포인터 때문에 2의 거듭제곱이어야 한다. 40 을 못 쓰고 64 로 올린다
DEPTH_sync  ?= 40
DEPTH_async ?= 64
DEPTH        = $(DEPTH_$(VARIANT))

# 한 테스트만 돌릴 때: make run TEST=case9_skew
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

# 구현별 소스. async 는 Part 1 파일을 그대로 참조한다. 한 줄도 고치지 않는다.
SRC_sync  = rtl/sync/fifo_q.sv

SRC_async = $(PART1)/fifo_if.sv   $(PART1)/fifo_mem.sv  \
            $(PART1)/sync_r2w.sv  $(PART1)/sync_w2r.sv  \
            $(PART1)/fifo_rptr.sv $(PART1)/fifo_wptr.sv \
            $(PART1)/async_fifo.sv rtl/async/fifo_q.sv

FIFO_SRC = $(SRC_$(VARIANT))

VCSFLAGS = -full64 -sverilog -timescale=1ns/1ps -debug_access+all -kdb -lca \
           +define+FIFO_DEPTH=$(DEPTH)

all: compile

# ---------------------------------------------------------------- 상위 회로
compile: $(BUILD)
	$(VCS) $(VCSFLAGS) $(FIFO_SRC) rtl/even_odd_top.sv tb/tb_even_odd.sv \
	  -top tb_even_odd -Mdir=$(BUILD)/csrc -o $(BUILD)/simv -l $(BUILD)/compile.log

run: compile
	cd $(BUILD) && ./simv $(PLUSARGS)

# ---------------------------------------------------------------- FIFO 단독
fifo: $(BUILD)
	$(VCS) $(VCSFLAGS) $(FIFO_SRC) tb/tb_fifo_q.sv \
	  -top tb_fifo_q -Mdir=$(BUILD)/csrc_fifo -o $(BUILD)/simv_fifo -l $(BUILD)/fifo.log
	cd $(BUILD) && ./simv_fifo

# ------------------------------------------------------------------- 비교
# 두 구현을 같은 testbench 로 돌리고 요약 줄만 나란히 보여준다.
compare:
	@for v in sync async ; do \
	  echo "======== VARIANT=$$v  DEPTH=$$($(MAKE) --no-print-directory VARIANT=$$v printdepth)" ; \
	  $(MAKE) --no-print-directory VARIANT=$$v run 2>&1 \
	    | grep -E 'RESULT|stall|cycles|PASSED|FAILED|Error' ; \
	done

printdepth:
	@echo $(DEPTH)

# ------------------------------------------------------------------- 트레이스
# 사이클마다 CSV 한 줄을 흘린다. 학습 노트가 파형 그림을 이 파일에서 직접 그린다.
# Verdi 스크린샷 대신 쓰는 이유는 벡터로 그려야 주석을 이미지에 굽지 않고
# HTML 로 따로 둘 수 있기 때문이다.
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
