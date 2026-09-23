`ifndef FIFO_DEPTH
  `define FIFO_DEPTH 64
`endif

module tb_fifo_q;

    localparam int DATA_WIDTH = 8;
    localparam int DEPTH      = `FIFO_DEPTH;

    logic                  clk;
    logic                  rst_n;

    logic                  wr_en;
    logic [DATA_WIDTH-1:0] wr_data;

    logic                  rd_en;
    logic [DATA_WIDTH-1:0] rd_data;

    logic                  full;
    logic                  empty;

    integer errors;
    integer empty_latency;


    fifo_q #(
        .DATA_WIDTH (DATA_WIDTH),
        .DEPTH      (DEPTH)
    ) dut (
        .*
    );


    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    initial begin
        $fsdbDumpfile("novas.fsdb");
        $fsdbDumpvars(0, tb_fifo_q);
    end


    task automatic reset_fifo;
        begin
            wr_en   = 1'b0;
            rd_en   = 1'b0;
            wr_data = '0;
            rst_n   = 1'b0;
            repeat (4) @(posedge clk);
            @(negedge clk);
            rst_n = 1'b1;
            repeat (4) @(posedge clk);
        end
    endtask


    task automatic push(input logic [DATA_WIDTH-1:0] d);
        begin
            @(negedge clk);
            wr_data = d;
            wr_en   = 1'b1;
            @(negedge clk);
            wr_en   = 1'b0;
        end
    endtask


    task automatic pop(output logic [DATA_WIDTH-1:0] d);
        begin
            @(negedge clk);
            d     = rd_data;
            rd_en = 1'b1;
            @(negedge clk);
            rd_en = 1'b0;
        end
    endtask


    task automatic measure_empty_latency;
        integer n;
        begin
            reset_fifo();

            if (!empty) begin
                $error("FIFO should be empty after reset.");
                errors = errors + 1;
            end

            push(8'hA5);

            n = 0;
            while (empty && n < 20) begin
                @(posedge clk);
                #1;
                n = n + 1;
            end

            empty_latency = n;

            if (empty) begin
                $error("empty never cleared after a write.");
                errors = errors + 1;
            end
            else begin
                $display("RESULT empty_latency = %0d cycle(s)", n);
            end

            if (rd_data !== 8'hA5) begin
                $error("head should be A5, got %02h", rd_data);
                errors = errors + 1;
            end
        end
    endtask


    task automatic fill_and_drain;
        logic [DATA_WIDTH-1:0] got;
        integer i;
        begin
            reset_fifo();

            for (i = 0; i < DEPTH; i = i + 1)
                push(i[DATA_WIDTH-1:0]);

            repeat (4) @(posedge clk);

            if (!full) begin
                $error("full should be asserted after %0d writes.", DEPTH);
                errors = errors + 1;
            end

            for (i = 0; i < DEPTH; i = i + 1) begin
                pop(got);
                if (got !== i[DATA_WIDTH-1:0]) begin
                    $error("order broken at %0d: expected %02h, got %02h",
                           i, i[DATA_WIDTH-1:0], got);
                    errors = errors + 1;
                end
            end

            repeat (4) @(posedge clk);

            if (!empty) begin
                $error("empty should be asserted after draining.");
                errors = errors + 1;
            end

            $display("RESULT fill_and_drain: %0d entries in order", DEPTH);
        end
    endtask


    task automatic stream;
        logic [DATA_WIDTH-1:0] got;
        integer i;
        begin
            reset_fifo();

            for (i = 0; i < 8; i = i + 1)
                push(8'h40 + i[DATA_WIDTH-1:0]);

            repeat (4) @(posedge clk);

            for (i = 8; i < 32; i = i + 1) begin
                @(negedge clk);
                wr_data = 8'h40 + i[DATA_WIDTH-1:0];
                wr_en   = 1'b1;
                got     = rd_data;
                rd_en   = 1'b1;
                @(negedge clk);
                wr_en   = 1'b0;
                rd_en   = 1'b0;

                if (got !== 8'h40 + (i - 8)) begin
                    $error("stream mismatch at %0d: expected %02h, got %02h",
                           i - 8, 8'h40 + (i - 8), got);
                    errors = errors + 1;
                end
            end

            $display("RESULT stream: 24 simultaneous read/write pairs in order");
        end
    endtask


    initial begin
        errors        = 0;
        empty_latency = -1;

        $display("=================================");
        $display("fifo_q level testbench");
        $display("=================================");

        measure_empty_latency();
        fill_and_drain();
        stream();

        if (errors == 0)
            $display("TEST PASSED. empty_latency=%0d", empty_latency);
        else
            $display("TEST FAILED with %0d error(s). empty_latency=%0d",
                     errors, empty_latency);

        #50;
        $finish;
    end

endmodule
