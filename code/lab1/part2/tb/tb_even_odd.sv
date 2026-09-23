`ifndef FIFO_DEPTH
  `define FIFO_DEPTH 64
`endif

module tb_even_odd;

    localparam int DATA_WIDTH = 8;
    localparam int DEPTH      = `FIFO_DEPTH;

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


    logic [DATA_WIDTH-1:0] exp_even [$];
    logic [DATA_WIDTH-1:0] exp_odd  [$];

    int errors;
    int total_errors;

    int prev_parity;

    int occ_even, occ_odd;
    int peak_even, peak_odd;
    int out_count;
    int full_seen;

    time start_time;
    time last_out_time;

    logic [DATA_WIDTH-1:0] stim [0:N_ITEMS-1];

    int  trace_fd;
    bit  tracing;

    string test_name;
    string want_test;


    always @(posedge Clock) begin
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


    task automatic build_stim(input bit skew, input int seed);
        int i, j;
        logic [DATA_WIDTH-1:0] t;
        begin
            for (i = 0; i < 40; i = i + 1) begin
                stim[i]      = DATA_WIDTH'(2 + 2*i);
                stim[40 + i] = DATA_WIDTH'(1 + 2*i);
            end

            if (!skew) begin
                void'($urandom(seed));
                for (i = N_ITEMS - 1; i > 0; i = i - 1) begin
                    j = $urandom_range(i, 0);
                    t = stim[i]; stim[i] = stim[j]; stim[j] = t;
                end
            end
        end
    endtask


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

                    if (d === '0) begin
                        $error("[%s] output 0 at time %0t. The circuit must pause instead.",
                               test_name, $time);
                        errors = errors + 1;
                    end

                    if (prev_parity >= 0 && int'(d[0]) == prev_parity) begin
                        $error("[%s] two %s numbers in a row at time %0t (value %0d)",
                               test_name, d[0] ? "odd" : "even", $time, d);
                        errors = errors + 1;
                    end
                    prev_parity = int'(d[0]);

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
                     (last_out_time - start_time) / 10,
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

        if (selected("case9_skew"))
            run_case("case9_skew",   1'b1,        0, 80, 100, 8, 10);

        if (selected("case9_random"))
            run_case("case9_random", 1'b0, 'h5EED_0009, 80, 100, 8, 10);

        if (selected("case8"))
            run_case("case8",        1'b0, 'h5EED_0008,  1,   2, 1,  4);

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


    initial begin
        #500000;
        $display("TEST FAILED: watchdog timeout");
        $finish;
    end

endmodule
