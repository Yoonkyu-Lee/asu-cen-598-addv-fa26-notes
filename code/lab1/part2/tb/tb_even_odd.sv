// even_odd_top 의 testbench.
//
// 검증 요구는 둘이다.
//
//   1. 명시된 속도로 돌린다. 입력 80 data / 100 clock, 출력 8 data / 10 clock
//   2. FIFO 크기 계산 문서의 case 를 최소 두 개 태운다. 그중 하나는 크기를
//      정할 때 쓴 case 여야 한다
//
// 그래서 네 가지를 돌린다.
//
//   case9_skew    Case 9 의 속도. parity 가 최악으로 쏠린 입력 (짝 40개 먼저,
//                 그 다음 홀 40개). FIFO 깊이를 정한 case 가 이것이다
//   case9_random  Case 9 의 속도. parity 가 뒤섞인 입력. 정상 동작 확인용
//   case8         fA = fB, 쓰기 2클럭당 1개, 읽기 4클럭당 1개. 문서 Case 8
//   case7         fA = fB, 쓰기도 읽기도 매 클럭. 문서 Case 7
//
// 하나만 돌리려면 다시 컴파일하지 않고 이렇게 고른다.
//
//   ./simv +TEST=case9_skew
//
// +TRACE 를 같이 주면 사이클마다 CSV 한 줄을 trace-<test>.csv 로 흘린다.
// 학습 노트가 파형 그림을 그 파일에서 직접 그린다. 평소 실행에는 영향이 없다.
//
// 아무것도 안 주면 넷 다 돈다.
//
// -------------------------------------------------------------------------
// 확인하는 것
//
//   교대      연속 두 출력의 parity 가 절대 같지 않다
//   순서      같은 parity 안에서 입력 순서가 그대로 지켜진다
//   0 금지    Lab 이 "should not output a 0" 라고 적었다. 입력에 0 이 없으므로
//             출력에 0 이 나오면 그 자체가 버그다
//   넘침 없음 두 FIFO 의 full 이 한 번도 서지 않는다. 깊이가 충분하다는 증거다
//   점유량    각 FIFO 의 최대 점유량을 재서 찍는다. 리포트의 크기 근거가 된다
// -------------------------------------------------------------------------

`ifndef FIFO_DEPTH
  `define FIFO_DEPTH 64
`endif

module tb_even_odd;

    localparam int DATA_WIDTH = 8;
    localparam int DEPTH      = `FIFO_DEPTH;

    // 한 테스트당 보내는 개수. Lab 의 가정대로 짝 40개, 홀 40개다.
    localparam int N_ITEMS = 80;

    logic                  Clock;
    logic                  Reset;
    logic [DATA_WIDTH-1:0] Data_in;
    logic                  Write_en;
    logic [DATA_WIDTH-1:0] Data_out;
    logic                  Read_en;


    even_odd_top #(
        .DATA_WIDTH (DATA_WIDTH),
        .FIFO_DEPTH (DEPTH)
    ) dut (
        .*
    );


    initial begin
        Clock = 1'b0;
        forever #5 Clock = ~Clock;
    end

    initial begin
        $fsdbDumpfile("novas.fsdb");
        $fsdbDumpvars(0, tb_even_odd);
    end


    //======================================================================
    // 채점판. 쓴 것을 parity 별로 쌓아 두고, 나온 것과 맞춰 본다.
    // 같은 parity 안에서 순서가 보존되는지는 큐의 앞에서 꺼내 비교하면 끝난다.
    //======================================================================

    logic [DATA_WIDTH-1:0] exp_even [$];
    logic [DATA_WIDTH-1:0] exp_odd  [$];

    int errors;
    int total_errors;

    // 직전 출력의 parity. -1 은 아직 아무것도 안 나왔다는 뜻이다.
    int prev_parity;

    int occ_even, occ_odd;
    int peak_even, peak_odd;
    int out_count;
    int full_seen;

    // 첫 쓰기부터 마지막 출력까지 걸린 사이클. 두 구현의 처리 시간 차이가
    // 여기서 숫자로 나온다. empty 가 늦게 풀리면 읽기가 늦게 시작되고,
    // 그만큼 전체가 뒤로 밀린다.
    time start_time;
    time last_out_time;

    logic [DATA_WIDTH-1:0] stim [0:N_ITEMS-1];

    // +TRACE 를 주면 사이클마다 CSV 한 줄을 파일로 흘린다. 학습 노트가 파형을
    // 직접 그릴 때 쓴다. 안 주면 파일을 열지도 않으므로 평소 실행에는 영향이 없다.
    int  trace_fd;
    bit  tracing;

    string test_name;
    string want_test;


    //======================================================================
    // 점유량 추적.
    //
    // 두 구현이 점유량을 서로 다르게 들고 있으므로 (동기는 카운터 하나,
    // 비동기는 gray code 포인터 두 벌) FIFO 안을 들여다보지 않는다.
    // 대신 상위 모듈의 wr_en / rd_en 을 testbench 가 직접 센다.
    // 그래야 같은 잣대로 두 구현을 비교할 수 있다.
    //
    // posedge 에서 1ns 뒤에 본다. 구동 신호는 negedge 에 바뀌므로 그 사이에는
    // posedge 시점의 값이 그대로 남아 있다.
    //======================================================================

    always @(posedge Clock) begin
        #1;
        if (!Reset) begin

            if (dut.even_wr_en && !dut.even_full) occ_even = occ_even + 1;
            if (dut.even_rd_en)                   occ_even = occ_even - 1;

            if (dut.odd_wr_en  && !dut.odd_full)  occ_odd  = occ_odd  + 1;
            if (dut.odd_rd_en)                    occ_odd  = occ_odd  - 1;

            if (occ_even > peak_even) peak_even = occ_even;
            if (occ_odd  > peak_odd ) peak_odd  = occ_odd;

            if (dut.even_full || dut.odd_full) full_seen = full_seen + 1;

        end
    end


    //======================================================================
    // CSV 트레이스.
    //
    // 점유량 추적과 같은 시점(posedge + 1ns)에서 찍는다. 그래야 표에 나오는
    // peak 값과 파형에 그려지는 점유량이 같은 숫자가 된다.
    //======================================================================

    int trace_cycle;

    always @(posedge Clock) begin
        #2;
        if (tracing && !Reset) begin
            $fdisplay(trace_fd, "%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",
                      trace_cycle,
                      Write_en, Data_in,
                      Read_en,  dut.out_valid, Data_out,
                      dut.sel,  dut.do_pop,
                      occ_even, occ_odd);
            trace_cycle = trace_cycle + 1;
        end
    end


    //======================================================================
    // 자극 만들기
    //======================================================================

    // skew 가 1 이면 짝수 40개를 먼저 다 보내고 그 다음 홀수 40개를 보낸다.
    // 이게 최악이다. 홀수가 하나도 없는 동안 읽기 쪽은 짝수 하나를 내보낸 뒤
    // 멈춘 채로 기다리고, 그동안 짝수 FIFO 에만 계속 쌓인다.
    task automatic build_stim(input bit skew, input int seed);
        int i, j;
        logic [DATA_WIDTH-1:0] t;
        begin
            for (i = 0; i < 40; i = i + 1) begin
                stim[i]      = DATA_WIDTH'(2 + 2*i);  // 2, 4, ... 80  짝수
                stim[40 + i] = DATA_WIDTH'(1 + 2*i);  // 1, 3, ... 79  홀수
            end

            if (!skew) begin
                // Fisher-Yates. seed 를 박아서 매번 같은 순서가 나오게 한다.
                // 재현되지 않는 테스트는 디버깅할 수 없다.
                void'($urandom(seed));
                for (i = N_ITEMS - 1; i > 0; i = i - 1) begin
                    j = $urandom_range(i, 0);
                    t = stim[i]; stim[i] = stim[j]; stim[j] = t;
                end
            end
        end
    endtask


    //======================================================================
    // 생산자. wr_period 사이클마다 앞의 wr_on 사이클에서 쓴다.
    //
    //   Case 9 : wr_on = 80, wr_period = 100  ->  80 data / 100 clock
    //            문서가 최악을 이렇게 잡으라고 한다. 쓰기는 최대 속도로 몰아
    //            붙이고 읽기는 최저 속도로 두는 것
    //   Case 8 : wr_on = 1,  wr_period = 2    ->  2클럭당 1개
    //   Case 7 : wr_on = 1,  wr_period = 1    ->  매 클럭
    //======================================================================

    task automatic producer(input int wr_on, input int wr_period);
        int sent, c;
        begin
            sent = 0;
            c    = 0;

            while (sent < N_ITEMS) begin
                @(negedge Clock);

                if ((c % wr_period) < wr_on) begin
                    Data_in  = stim[sent];
                    Write_en = 1'b1;

                    if (stim[sent][0])
                        exp_odd.push_back(stim[sent]);
                    else
                        exp_even.push_back(stim[sent]);

                    sent = sent + 1;
                end
                else begin
                    Write_en = 1'b0;
                end

                c = c + 1;
            end

            @(negedge Clock);
            Write_en = 1'b0;
        end
    endtask


    //======================================================================
    // 소비자. rd_period 사이클마다 앞의 rd_on 사이클에서 읽기를 요청한다.
    // 다 나올 때까지 계속 요청한다. 설계가 멈춰 있으면 요청은 무시된다.
    //======================================================================

    task automatic consumer(input int rd_on, input int rd_period, input int max_cycles);
        int c;
        begin
            c = 0;
            while (out_count < N_ITEMS && c < max_cycles) begin
                @(negedge Clock);
                Read_en = ((c % rd_period) < rd_on);
                c = c + 1;
            end

            @(negedge Clock);
            Read_en = 1'b0;
        end
    endtask


    //======================================================================
    // 감시자. 나온 값 하나하나를 채점판과 맞춘다.
    //======================================================================

    task automatic monitor(input int max_cycles);
        logic [DATA_WIDTH-1:0] d;
        logic [DATA_WIDTH-1:0] want;
        int c;
        begin
            c = 0;
            while (out_count < N_ITEMS && c < max_cycles) begin
                @(negedge Clock);
                c = c + 1;

                if (dut.out_valid) begin
                    d = Data_out;

                    // 0 은 나오면 안 된다. 자극에 0 이 없기 때문이다.
                    if (d === '0) begin
                        $error("[%s] output 0 at time %0t. The circuit must pause instead.",
                               test_name, $time);
                        errors = errors + 1;
                    end

                    // 교대. 직전과 parity 가 같으면 설계의 핵심이 깨진 것이다.
                    if (prev_parity >= 0 && int'(d[0]) == prev_parity) begin
                        $error("[%s] two %s numbers in a row at time %0t (value %0d)",
                               test_name, d[0] ? "odd" : "even", $time, d);
                        errors = errors + 1;
                    end
                    prev_parity = int'(d[0]);

                    // 같은 parity 안의 순서.
                    if (d[0]) begin
                        if (exp_odd.size() == 0) begin
                            $error("[%s] got odd %0d but nothing was written", test_name, d);
                            errors = errors + 1;
                        end
                        else begin
                            want = exp_odd.pop_front();
                            if (d !== want) begin
                                $error("[%s] odd order broken: expected %0d, got %0d",
                                       test_name, want, d);
                                errors = errors + 1;
                            end
                        end
                    end
                    else begin
                        if (exp_even.size() == 0) begin
                            $error("[%s] got even %0d but nothing was written", test_name, d);
                            errors = errors + 1;
                        end
                        else begin
                            want = exp_even.pop_front();
                            if (d !== want) begin
                                $error("[%s] even order broken: expected %0d, got %0d",
                                       test_name, want, d);
                                errors = errors + 1;
                            end
                        end
                    end

                    out_count     = out_count + 1;
                    last_out_time = $time;
                end
            end
        end
    endtask


    //======================================================================
    // 한 테스트를 통째로 돌린다.
    //======================================================================

    task automatic run_case(input string name,
                            input bit    skew,
                            input int    seed,
                            input int    wr_on,
                            input int    wr_period,
                            input int    rd_on,
                            input int    rd_period);
        int err_mark;
        int max_cycles;
        begin
            test_name  = name;
            err_mark   = errors;
            max_cycles = 4000;

            // 판을 비운다.
            exp_even.delete();
            exp_odd.delete();
            prev_parity = -1;
            occ_even    = 0;
            occ_odd     = 0;
            peak_even   = 0;
            peak_odd    = 0;
            out_count     = 0;
            full_seen     = 0;
            last_out_time = 0;

            Write_en = 1'b0;
            Read_en  = 1'b0;
            Data_in  = '0;
            Reset    = 1'b1;
            repeat (4) @(negedge Clock);
            Reset    = 1'b0;
            repeat (2) @(negedge Clock);

            build_stim(skew, seed);

            if ($test$plusargs("TRACE")) begin
                trace_fd = $fopen({"trace-", name, ".csv"}, "w");
                $fdisplay(trace_fd,
                          "cycle,write_en,data_in,read_en,out_valid,data_out,sel,do_pop,occ_even,occ_odd");
                trace_cycle = 0;
                tracing     = 1'b1;
            end

            start_time = $time;

            fork
                producer(wr_on, wr_period);
                consumer(rd_on, rd_period, max_cycles);
                monitor(max_cycles);
            join

            if (tracing) begin
                tracing = 1'b0;
                $fclose(trace_fd);
                $display("TRACE wrote trace-%s.csv (%0d cycles)", name, trace_cycle);
            end

            if (out_count != N_ITEMS) begin
                $error("[%s] only %0d of %0d items came out", name, out_count, N_ITEMS);
                errors = errors + 1;
            end

            if (full_seen != 0) begin
                $error("[%s] a FIFO went full %0d time(s). DEPTH=%0d is too small.",
                       name, full_seen, DEPTH);
                errors = errors + 1;
            end

            $display("RESULT %-14s out=%0d/%0d  peak_even=%2d  peak_odd=%2d  cycles=%0d  %s",
                     name, out_count, N_ITEMS, peak_even, peak_odd,
                     (last_out_time - start_time) / 10, // 클럭 주기가 10ns 다
                     (errors == err_mark) ? "ok" : "FAILED");

            total_errors = errors;
        end
    endtask


    function automatic bit selected(input string name);
        begin
            selected = (want_test == "all") || (want_test == name);
        end
    endfunction


    initial begin
        errors       = 0;
        total_errors = 0;

        if (!$value$plusargs("TEST=%s", want_test))
            want_test = "all";

        $display("=========================================");
        $display("even_odd_top testbench");
        $display("  FIFO DEPTH = %0d", DEPTH);
        $display("  TEST       = %s", want_test);
        $display("=========================================");

        // Case 9, 최악의 parity 쏠림. FIFO 깊이를 정한 case 다.
        if (selected("case9_skew"))
            run_case("case9_skew",   1'b1,        0, 80, 100, 8, 10);

        // Case 9, parity 가 뒤섞인 보통 입력.
        if (selected("case9_random"))
            run_case("case9_random", 1'b0, 'h5EED_0009, 80, 100, 8, 10);

        // 문서 Case 8. fA = fB, 쓰기 2클럭당 1개, 읽기 4클럭당 1개.
        if (selected("case8"))
            run_case("case8",        1'b0, 'h5EED_0008,  1,   2, 1,  4);

        // 문서 Case 7. fA = fB, 둘 다 idle 없음.
        if (selected("case7"))
            run_case("case7",        1'b0, 'h5EED_0007,  1,   1, 1,  1);

        $display("-----------------------------------------");
        if (total_errors == 0)
            $display("TEST PASSED");
        else
            $display("TEST FAILED with %0d error(s)", total_errors);

        #50;
        $finish;
    end


    // 무한 대기 방지.
    initial begin
        #500000;
        $display("TEST FAILED: watchdog timeout");
        $finish;
    end

endmodule
