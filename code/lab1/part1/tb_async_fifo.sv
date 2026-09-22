module tb_async_fifo;

    localparam int DATA_WIDTH = 8;
    localparam int DEPTH      = 16;

    // Thresholds the design is required to hit, spelled the same way the
    // design spells them so the testbench and fifo_wptr/fifo_rptr cannot
    // drift apart silently.
    localparam int AF_LEVEL   = (3 * DEPTH) / 4;   // almost_full  at 3/4 full
    localparam int AE_LEVEL   = DEPTH / 4;         // almost_empty at 3/4 empty

    logic [DATA_WIDTH-1:0] wdata;
    logic [DATA_WIDTH-1:0] rdata;

    logic winc;
    logic wclk;
    logic wrst_n;

    logic rinc;
    logic rclk;
    logic rrst_n;

    logic wfull;
    logic rempty;
    logic almost_full;
    logic almost_empty;

    integer errors;


    async_fifo #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)
    ) dut (
        .*
    );


    // Write clock: 10 ns period
    initial begin
        wclk = 1'b0;
        forever #5 wclk = ~wclk;
    end


    // Read clock: 14 ns period
    initial begin
        rclk = 1'b0;
        forever #7 rclk = ~rclk;
    end


    // Dump waveforms for Verdi
    initial begin
        $fsdbDumpfile("novas.fsdb");
        $fsdbDumpvars(0, tb_async_fifo);
    end


    // Optional CSV trace, switched on with +TRACE.
    //
    // The two clocks have different periods (10 ns and 14 ns), so there is no
    // one clock to sample on. We sample a flat 1 ns grid instead. That lands
    // exactly on every edge of both clocks, so a plot can be drawn from the
    // file without guessing where the edges were.
    //
    // Nothing is opened unless +TRACE is passed, so a normal run is untouched.
    int    trace_fd;
    bit    tracing = 1'b0;
    string trace_name = "run";

    initial begin
        if ($test$plusargs("TRACE")) begin
            void'($value$plusargs("TRACE=%s", trace_name));
            trace_fd = $fopen({"trace-", trace_name, ".csv"}, "w");
            $fdisplay(trace_fd,
                      "t_ns,wclk,rclk,winc,wdata,rinc,rdata,wfull,rempty,almost_full,almost_empty");
            tracing = 1'b1;
        end
    end

    always #1 begin
        if (tracing)
            $fdisplay(trace_fd, "%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d,%0d",
                      $time, wclk, rclk,
                      winc, wdata, rinc, rdata,
                      wfull, rempty, almost_full, almost_empty);
    end


    // Reset the FIFO
    task automatic reset_fifo;
        begin
            winc   = 1'b0;
            rinc   = 1'b0;
            wdata  = '0;

            wrst_n = 1'b0;
            rrst_n = 1'b0;

            repeat (3) @(posedge wclk);
            repeat (3) @(posedge rclk);

            @(negedge wclk);
            wrst_n = 1'b1;

            @(negedge rclk);
            rrst_n = 1'b1;

            repeat (3) @(posedge wclk);
            repeat (3) @(posedge rclk);
        end
    endtask


    // Write one value into the FIFO
    task automatic write_word(
        input logic [DATA_WIDTH-1:0] data
    );
        begin
            wait (!wfull);

            @(negedge wclk);
            wdata = data;
            winc  = 1'b1;

            @(negedge wclk);
            winc  = 1'b0;
        end
    endtask


    // Read one value from the FIFO
    task automatic read_word(
        output logic [DATA_WIDTH-1:0] data
    );
        begin
            wait (!rempty);

            @(negedge rclk);
            data = rdata;
            rinc = 1'b1;

            @(negedge rclk);
            rinc = 1'b0;
        end
    endtask


    // TEST 1:
    // FIFO starts empty, fills completely,
    // then is read until empty again.
    task automatic test_fill_empty;

        logic [DATA_WIDTH-1:0] read_value;
        integer i;

        begin
            $display("=================================");
            $display("TEST 1: EMPTY -> FULL -> EMPTY");
            $display("=================================");

            reset_fifo();

            if (!rempty) begin
                $error("FIFO should be empty after reset.");
                errors = errors + 1;
            end

            for (i = 0; i < DEPTH; i = i + 1)
                write_word(i);

            wait (wfull);

            $display("FIFO reached FULL state.");

            for (i = 0; i < DEPTH; i = i + 1) begin

                read_word(read_value);

                if (read_value !== i[DATA_WIDTH-1:0]) begin
                    $error(
                        "Data mismatch: expected %0d, got %0d",
                        i,
                        read_value
                    );
                    errors = errors + 1;
                end

            end

            wait (rempty);

            $display("FIFO returned to EMPTY state.");

        end

    endtask


    // TEST 2:
    // Check that almost_full and almost_empty assert at the right occupancy.
    //
    // The earlier version of this test filled to the threshold and then did
    // wait (almost_full). That only proves the flag asserts at some point, not
    // that it asserts at the right point: setting ALMOST_FULL_LEVEL to DEPTH/2
    // in fifo_wptr.sv still passed it, and the test even printed "asserted at
    // 3/4 full" because that string is a constant.
    //
    // So each flag is checked on both sides of its boundary. One entry short
    // it must be low, and on the entry that crosses it must be high.
    task automatic test_flags;

        logic [DATA_WIDTH-1:0] read_value;
        integer i;
        integer err_mark;

        begin
            $display("=================================");
            $display("TEST 2: ALMOST_FULL / ALMOST_EMPTY");
            $display("=================================");

            reset_fifo();

            if (!almost_empty) begin
                $error("almost_empty should be asserted after reset.");
                errors = errors + 1;
            end

            //--------------------------------------------------------------
            // almost_full boundary. No reads have happened, so the write side
            // sees an exact occupancy and the check needs no settling time.
            //--------------------------------------------------------------
            err_mark = errors;

            for (i = 0; i < AF_LEVEL - 1; i = i + 1)
                write_word(i + 8'h20);

            @(posedge wclk);
            if (almost_full) begin
                $error("almost_full asserted early: high at %0d of %0d entries, expected low until %0d.",
                       AF_LEVEL - 1, DEPTH, AF_LEVEL);
                errors = errors + 1;
            end

            write_word(8'h20 + AF_LEVEL - 1);

            @(posedge wclk);
            if (!almost_full) begin
                $error("almost_full did not assert at %0d of %0d entries.",
                       AF_LEVEL, DEPTH);
                errors = errors + 1;
            end

            if (errors == err_mark)
                $display("almost_full correct: low at %0d entries, high at %0d.",
                         AF_LEVEL - 1, AF_LEVEL);

            //--------------------------------------------------------------
            // almost_empty boundary. This flag lives in the read domain and is
            // computed from the synchronized write pointer, so wait for that
            // pointer to arrive before judging it. The writer is idle from here
            // on, so once it has arrived the occupancy the read side sees is
            // exact.
            //--------------------------------------------------------------
            wait (!almost_empty);

            err_mark = errors;

            for (i = 0; i < AF_LEVEL - AE_LEVEL - 1; i = i + 1)
                read_word(read_value);

            @(posedge rclk);
            if (almost_empty) begin
                $error("almost_empty asserted early: high with %0d entries left, expected low until %0d.",
                       AE_LEVEL + 1, AE_LEVEL);
                errors = errors + 1;
            end

            read_word(read_value);

            @(posedge rclk);
            if (!almost_empty) begin
                $error("almost_empty did not assert with %0d entries left.",
                       AE_LEVEL);
                errors = errors + 1;
            end

            if (errors == err_mark)
                $display("almost_empty correct: low with %0d entries left, high with %0d.",
                         AE_LEVEL + 1, AE_LEVEL);

        end

    endtask


    // TEST 3:
// Simultaneous reads and writes using different clocks.
task automatic test_simultaneous;

    logic [DATA_WIDTH-1:0] read_value;
    integer wi;
    integer ri;

    begin
        $display("=================================");
        $display("TEST 3: SIMULTANEOUS READ / WRITE");
        $display("=================================");

        reset_fifo();

        // Preload 4 entries so the reader has data available
        // when simultaneous operation begins.
        for (wi = 0; wi < 4; wi = wi + 1)
            write_word(wi + 8'h40);

        // Continue writing while reading at the same time.
        fork

            begin : writer
                for (wi = 4; wi < 12; wi = wi + 1)
                    write_word(wi + 8'h40);
            end

            begin : reader
                for (ri = 0; ri < 12; ri = ri + 1) begin

                    read_word(read_value);

                    if (read_value !== (ri + 8'h40)) begin
                        $error(
                            "Data mismatch: expected %0h, got %0h",
                            (ri + 8'h40),
                            read_value
                        );
                        errors = errors + 1;
                    end

                end
            end

        join

        wait (rempty);

        $display("Simultaneous read/write test complete.");

    end

endtask


    // Select one test from the command line.
    initial begin

        errors = 0;

        if ($test$plusargs("TEST_FILL_EMPTY")) begin

            test_fill_empty();

        end
        else if ($test$plusargs("TEST_FLAGS")) begin

            test_flags();

        end
        else if ($test$plusargs("TEST_SIMULTANEOUS")) begin

            test_simultaneous();

        end
        else begin

            $display("ERROR: No test was selected.");
            $display("Use one of:");
            $display("  +TEST_FILL_EMPTY");
            $display("  +TEST_FLAGS");
            $display("  +TEST_SIMULTANEOUS");

            errors = errors + 1;

        end


        if (errors == 0)
            $display("TEST PASSED.");
        else
            $display("TEST FAILED with %0d error(s).", errors);

        if (tracing) begin
            #50;
            tracing = 1'b0;
            $fclose(trace_fd);
            $display("TRACE wrote trace-%0s.csv", trace_name);
        end


        #50;
        $finish;

    end

endmodule
